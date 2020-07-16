const xAxisSelect = document.querySelector(".x-axis-value")
const yAxisSelect = document.querySelector(".y-axis-value")
const yAxisDetails = document.querySelector(".y-axis-details")
const emptyGraph = document.querySelector(".empty-graph")
const exportButton = document.querySelector(".export")

const addLine = document.querySelector(".add-line")

const axesRange = document.querySelectorAll(".axis-range")

const xFrom = document.querySelector(".x-from")
const yFrom = document.querySelector(".y-from")
const xTo = document.querySelector(".x-to")
const yTo = document.querySelector(".y-to")



// Get the DOM elements for all of the axes, so that we can add event listeners for when they are changed
const axesSettings = document.querySelectorAll(".axis-setting")

// Get the graph data
const data = graphData["chart_data"]
// // Get the column info, which will be used to identify
// const columnInfo = graphData["column_info"]

// const parseDate = d3.time.format("%Y-%m-%d %X");

// initialiseData(data, columnInfo);

// // This function is used to check and parse date/time columns (if any)
// function initialiseData(data, columnInfo){
//   columnInfo.forEach(column => {
//     console.log(data);
//     if(column["data_type"] == "date"){
//       console.log(column["title"]);
//     }
//     else if(column["data_type"] == "time"){
//       console.log(column["title"]);
//     }
//     else if(column["data_type"] == "date/time"){
//       parseDate = d3.time.format("%Y-%m-%d %X");
//     }
//   })
// }
//



// When the axes are altered, we need to re-group the data depending on the variables set
axesSettings.forEach(setting => {
  setting.onchange = function(){
    axisChange()
  }
})


function axisChange (){
    let xAxisValue = xAxisSelect.options[xAxisSelect.selectedIndex].value;
    let yAxisValue = yAxisSelect.options[yAxisSelect.selectedIndex].value;

    // Remove the ' -- select an option -- ' option
    xAxisSelect.firstChild.hidden = true;
    yAxisSelect.firstChild.hidden = true;

    // Reveal the y-axis variable for the user to select
    yAxisDetails.classList.remove('hidden-axis')

    // If the user has selected variables for both the x and the y axes
    if (xAxisValue != "" && yAxisValue != ""){
      // Make the overlay hidden
      emptyGraph.classList.remove("visible");
      emptyGraph.classList.add("hidden");
      addLine.disabled = false;
      // re-draw the graph with the chosen variables
      render(data);
    }
}


addLine.addEventListener("change", function(){
  if(this.checked){
    // d3.selectAll('.graph-line').attr("opacity",1);
    d3.selectAll('.graph-line').transition().duration(1000).style("visibility", "visible");
    render(data)
  } else {
    // d3.selectAll('.graph-line').attr("opacity",0);
    d3.selectAll('.graph-line').transition().duration(1000).style("visibility", "hidden");
    render(data)
  }
})

axesRange.forEach(input => {
  input.onchange = function() {
    render(data)
  }
})



addLine.addEventListener("change", function(){
  if(this.checked){
    // d3.selectAll('.graph-line').attr("opacity",1);
    d3.selectAll('.graph-line').transition().duration(1000).style("visibility", "visible");
    render(data)
  } else {
    // d3.selectAll('.graph-line').attr("opacity",0);
    d3.selectAll('.graph-line').transition().duration(1000).style("visibility", "hidden");
    render(data)
  }
})






// Set graph dimensions
var width = document.getElementById('graph').clientWidth;
var height = document.getElementById('graph').clientHeight;

window.onresize = function(){
  width = document.getElementById('graph').clientWidth;
  height = document.getElementById('graph').clientHeight;
  svg.attr('width', width).attr('height', height);
}


// Create SVG ready for graph
const svg = d3.select('#graph').append("svg").attr("width", width).attr("height", height).attr("viewBox", "0 0 " + width + " " + height).attr("preserveAspectRatio", "none")

// Set margins around graph for axis and labels
const margin = { top: 20, right: 20, bottom: 60, left: 80 };
// Set the graph width and height to account for axes
const gWidth = width - margin.left - margin.right;
const gHeight = height - margin.top - margin.bottom;

// Add the graph area to the SVG, factoring in the margin dimensions
var graph = svg.append('g').attr("transform", `translate(${margin.left}, ${margin.top})`)

const render = (data) => {

  let xAxisValue = xAxisSelect.options[xAxisSelect.selectedIndex].value;
  let yAxisValue = yAxisSelect.options[yAxisSelect.selectedIndex].value;


  // Specify the x-axis values and the y-axis values
  const xValues = d => d[xAxisValue];
  const yValues = d => d[yAxisValue];

  // Remove old axes labels (if they exist)
  d3.selectAll('.label').remove();

  // sort the grouped data keys in ascending order (i.e. so the x-axis is in numerical order)
  // data.sort(function(a, b) { return d3.ascending(parseInt(a.key), parseInt(b.key))});
  data.sort(function(a, b) {
    return d3.ascending(parseInt(a[xAxisValue]), parseInt(b[xAxisValue]))
  });


  // set the input fields for the domain (i.e. range of values) if not yet set
  if(xFrom.value == "") xFrom.value = d3.min(data, xValues)
  if(xTo.value == "") xTo.value = d3.max(data, xValues)
  if(yFrom.value == "") yFrom.value = d3.min(data, yValues)
  if(yTo.value == "") yTo.value = d3.max(data, yValues)

  // Now extract the range from the values (if they are specifed by user)
  // If the values specified by the user are outside the range of the data, increase the range
  // else use the range of the data as default.
  xFromValue = xFrom.value = Math.min(d3.min(data, xValues), xFrom.value)
  xToValue = xTo.value = Math.max(d3.max(data, xValues), xTo.value)
  yFromValue = yFrom.value = Math.min(d3.min(data, yValues), yFrom.value)
  yToValue = yTo.value = Math.max(d3.max(data, yValues), yTo.value)

  // Reveal the 'add-line' select option
  document.querySelector(".form-add-line").classList.remove("hidden")

  // Set the scale for the x-axis
  const xScale = d3.scaleLinear()
    .domain([xFromValue, xToValue]).nice()
    .range([0, gWidth])

  // Set the scale for the y-axis
  const yScale = d3.scaleLinear()
    .domain([yFromValue, yToValue])
    .range([gHeight, 0])


  // Select the axes (if they exist)
  var yAxis = d3.selectAll(".yAxis")
  var xAxis = d3.selectAll(".xAxis")

  // Get the position of the axes. Either set to 0 or set to the far left/bottom
  xPosition = (0 > yFromValue && 0 < yToValue) ? yScale(0) : gHeight
  yPosition = (0 > xFromValue && 0 < xToValue) ? xScale(0) : 0


  // If they dont exist, we create them. If they do, we update them
  if (yAxis.empty() && xAxis.empty()){
    // For the x-axis we create an axisBottom and 'translate' it so it appears on the bottom of the graph
    graph.append('g').attr("class", "xAxis").call(d3.axisBottom(xScale))
    .attr("transform", `translate(0, ${xPosition})`)
    // For why axis we do not need to translate it, as the default is on the left
    graph.append('g').attr("class", "yAxis").call(d3.axisLeft(yScale))
    .attr("transform", `translate(${yPosition}, 0)`)
  } else {
    // Adjust the x-axis according the x-axis variable data
    xAxis.transition()
      .duration(1000)
      .call(d3.axisBottom(xScale))
      .attr("transform", `translate(0, ${xPosition})`)
    // Adjust the y-axis according the y-axis variable data
    yAxis.transition()
      .duration(1000)
      .call(d3.axisLeft(yScale))
      .attr("transform", `translate(${yPosition}, 0)`)
  }





  // Add y axis label
  svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("class", "label")
      .attr("y", 0)
      .attr("x",0 - (gHeight / 2))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .text(yAxisValue);



  // Add x axis label
  svg.append("text")
    .attr("transform",`translate(${width/2}, ${gHeight + margin.top + 55})`)
    .attr("class", "label")
    .text(xAxisValue);


  var line = d3.line()
    .x(d => xScale(xValues(d)))
    .y(d => yScale(yValues(d)))
    // .curve(d3.curveCatmullRom.alpha(0.5));

  var startingLine = d3.line()
    .x(d => xScale(xValues(d)))
    .y(d => yScale(0))


  var path = graph.selectAll('.graph-line').data(data)



  if(addLine.checked == true){
    path
     .enter()
     .append("path")
     .attr("class","graph-line")
     .merge(path)
     .transition()
     .duration(1000)
     .attr("d", line(data))
       .attr("fill", "none")
       .attr("stroke", "steelblue")
       .attr("stroke-width", 2.5)
  }



  // Select all 'circle' DOM elements (if they exist)
  var circle = graph.selectAll('circle').data(data)

  // D3 'exit()' is what happens to DOM elements that no longer have data bound to them
  // Given a transition that shrinks them down to the x-axis
  circle.exit().transition()
  .duration(1000)
  .attr("cy", yScale(0))
  .remove()

  // D3 'enter()' is the creation of DOM elements bound to the data
  var plot = circle.enter()
  .append('circle')
      .attr("cy",  yScale(0))
      .attr('cx', d => xScale(xValues(d)))
      .attr("r", 3)
      .style('fill', 'steelblue')


  // For the colour, I had to convert the 'primary-colour-dark' variable into a hex colour so that the effect can work
  plot.on('mouseenter', function(d) {
    d3.select(this)
    .transition()
    .duration(100)
    .style('fill', '#2D4053')


    var tooltipOffset = (d3.select(this).attr("width") - 80)/2;

    var tooltip = d3.select(".graph-tooltip")

    // To position the tool tip when the user hovers. Use the window and calculate the offset
    var position = this.getScreenCTM()
        .translate(+ this.getAttribute("x"), + this.getAttribute("y"));

    // Now give the tooltip the data it needs to show and the position it should be.
    tooltip.html(yValues(d))
        .style("left", (window.pageXOffset + position.e + tooltipOffset) + "px") // Center it horizontally over the bar
        .style("top", (window.pageYOffset + position.f) + "px"); // Shift it 40 px above the bar



		tooltip.classed("tooltip-hidden", false)

  }).on('mouseout', function() {
    d3.select(this)
    .transition()
    .style('fill', 'steelblue')

    d3.select(".graph-tooltip").classed("tooltip-hidden", true);
  })

  plot.merge(circle)  // 'merge' merges the 'enter' and 'update' groups
      .transition()
      .delay(d =>  xScale(xValues(d))/2 )
      .duration(1000)
      .attr('cy', d=>  yScale(yValues(d)))
      .attr('cx', d => xScale(xValues(d)))

}




let xAxisValue = xAxisSelect.options[xAxisSelect.selectedIndex].value;
if(xAxisValue != ''){
  axisChange()
}



exportButton.addEventListener("click", () => {
  saveSvgAsPng(document.getElementsByTagName("svg")[0], "plot.png", {scale: 2, backgroundColor: "#FFFFFF"});
})



// When the form is submitted, we want to get a jpg image of the svg
$('form').submit(function (e) {

  // Prevent default submission of form
  e.preventDefault();
  var doctype = '<?xml version="1.0" standalone="no"?>'
               + '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">';

  var source = (new XMLSerializer()).serializeToString(svg.node());
  var blob = new Blob([ doctype + source], { type: 'image/svg+xml' });
  var imageURL = window.URL.createObjectURL(blob);
  var img = new Image();

  img.onload = async function(){
    var canvas = d3.select('body').append('canvas').node();
    canvas.width = width;
    canvas.height = height;

    var ctx = canvas.getContext('2d');

    // draw image on canvas
    ctx.drawImage(img, 0, 0, width, height);

    var glContextAttributes = { preserveDrawingBuffer: true };
    var gl = canvas.getContext("experimental-webgl", glContextAttributes);

    var imgData = await canvas.toDataURL("image/png");
    canvas.remove();

    // ajax call to send canvas(base64) url to server.
    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrf)
        }
      }
    })

    var postData = $('form').serializeArray()
    postData.push({name: "image", value: imgData})
    $.ajax({
        type: "POST",
        url: url,
        data: postData,
        success: function () {
          window.location.href = redirectUrl;
        }
    });
  }

  img.src =  imageURL;

});
