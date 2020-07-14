const xAxisSelect = document.querySelector(".x-axis-value")
const emptyGraph = document.querySelector(".empty-graph")
const exportButton = document.querySelector(".export")

const settingsGroup = document.querySelector(".extra-settings-group")

const extraSettings = document.querySelectorAll(".extra-setting")

const xFrom = document.querySelector(".x-from")
const xTo = document.querySelector(".x-to")
const numberOfGroups = document.querySelector(".number-groups")

// Get the DOM elements for all of the axes, so that we can add event listeners for when they are changed
const axisSettings = document.querySelector(".axis-setting")

// Get the graph data
const data = graphData["chart_data"]

// When the axis is altered, we need to re-group the data depending on the variable set
axisSettings.onchange = function(){
  axisChange()
}

// When the x-axis range is altered or the group size is altered, we need to re-render the table
extraSettings.forEach(input => {
  input.onchange = function() {
    render(data)
  }
})


function axisChange (){
    let xAxisValue = xAxisSelect.options[xAxisSelect.selectedIndex].value;
    // Reset the axis range and number of groups when user selects a new variable
    xFrom.value = ""
    xTo.value = ""
    numberOfGroups.value == ""
    // Remove the ' -- select an option -- ' option
    xAxisSelect.firstChild.hidden = true;

    // Reveal the extra settings
    settingsGroup.classList.remove('hidden-axis')

    // If the user has selected variables for both the x and the y axes
    // Make the overlay hidden
    emptyGraph.classList.remove("visible");
    emptyGraph.classList.add("hidden");

    // group the data
    // let groupedData = groupData(xAxisValue);
    // re-draw the graph with the chosen variables
    render(data);
}





// DATA GROUPING FUNCTION. CALLED WHEN AN AXIS SETTING CHANGES
function groupData(xAxisValue){
  // We can create a 'nested' D3 object, with the key as the chosen x-axis variable
  let nestedData = d3.nest().key(function(d) { return d[xAxisValue]; })

  return nestedData
    .rollup(function(v) { return v.length; })
    .entries(data)

}




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

  // Specify the x-axis values and the y-axis values
  const xValues = d => d[xAxisValue];
  const yValues = d => d.length;

  // Remove old axes labels (if they exist)
  d3.selectAll('.label').remove();

  // sort the grouped data keys in ascending order (i.e. so the x-axis is in numerical order)
  data.sort(function(a, b) { return d3.ascending(parseInt(a.key), parseInt(b.key))});


  // set the input fields for the domain (i.e. range of values) if not yet set
  if(xFrom.value == "") xFrom.value = d3.min(data, xValues)
  if(xTo.value == "") xTo.value = d3.max(data, xValues)

  // Now extract the range from the values (if they are specifed by user)
  // If the values specified by the user are outside the range of the data, increase the range
  // else use the range of the data as default.
  xFromValue = xFrom.value = Math.min(d3.min(data, xValues), xFrom.value)
  xToValue = xTo.value = Math.max(d3.max(data, xValues), xTo.value)

  // Set the scale for the x-axis
  const xScale = d3.scaleLinear()
    // .domain(d3.extent(data, xValues)).nice()
    .domain([xFromValue, xToValue]).nice()
    .range([0, gWidth])

  let groups;
  if(numberOfGroups.value == ""){
    groups = xScale.ticks()
  }else{
    groups = numberOfGroups.value
  }


  let histogram = d3.histogram()
    .value(xValues)
    .domain(xScale.domain())
    // .thresholds(xScale.ticks())
    .thresholds(groups)

  var bins = histogram(data)


  // Set the scale for the y-axis
  const yScale = d3.scaleLinear()
    .domain([0, d3.max(bins, d => d.length)]).nice()
    .range([gHeight, 0])



  // Select the axes (if they exist)
  var yAxis = d3.selectAll(".yAxis")
  var xAxis = d3.selectAll(".xAxis")

  // If they dont exist, we create them. If they do, we update them
  if (yAxis.empty() && xAxis.empty()){
    // For the x-axis we create an axisBottom and 'translate' it so it appears on the bottom of the graph
    graph.append('g').attr("class", "xAxis").call(d3.axisBottom(xScale))
    .attr("transform", `translate(0, ${gHeight})`)
    // For why axis we do not need to translate it, as the default is on the left
    graph.append('g').attr("class", "yAxis").call(d3.axisLeft(yScale))
  } else {
    // Adjust the x-axis according the x-axis variable data
    xAxis.transition()
      .duration(1000)
      .call(d3.axisBottom(xScale))
    // Adjust the y-axis according the y-axis variable data
    yAxis.transition()
      .duration(1000)
      .call(d3.axisLeft(yScale))
  }


  // Add y axis label
  svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("class", "label")
      .attr("y", 0)
      .attr("x",0 - (gHeight / 2))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .text("Frequency");

  // Add x axis label
  svg.append("text")
    .attr("transform",`translate(${width/2}, ${gHeight + margin.top + 55})`)
    .attr("class", "label")
    .text(xAxisValue);


  let rect = graph.selectAll('rect').data(bins)

  // D3 'exit()' is what happens to DOM elements that no longer have data bound to them
  // Given a transition that shrinks them down to the x-axis
  rect.exit().transition()
  .duration(1000)
  .attr("y", yScale(0))
  .attr('height', 0)
  .remove()

  // D3 'enter()' is the creation of DOM elements bound to the data
  var bar = rect.enter()
  .append('rect')
      .attr("y",  yScale(0))
      .attr('x', d => xScale(d.x0))
      .attr('width', d => Math.max(0, xScale(d.x1) - xScale(d.x0) - 1)) // width of a single bar
      .style('fill', 'steelblue')

  // For the colour, I had to convert the 'primary-colour-dark' variable into a hex colour so that the effect can work
  bar.on('mouseenter', function(d) {
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
        .style("top", (window.pageYOffset + position.f - 50) + "px"); // Shift it 50 px above the bar



		tooltip.classed("tooltip-hidden", false)

  }).on('mouseout', function() {
    d3.select(this)
    .transition()
    .style('fill', 'steelblue')

    d3.select(".graph-tooltip").classed("tooltip-hidden", true);
  })


  bar.merge(rect)  // 'merge' merges the 'enter' and 'update' groups
      .transition()
      // .delay(d =>  xScale(xValues(d))/2 )
      .duration(1000)
      .attr('height', d => yScale(0) - yScale(d.length))
      .attr('y', d => yScale(d.length))
      .attr('x', d => xScale(d.x0))
      .attr('width', d => Math.max(0, xScale(d.x1) - xScale(d.x0) - 1)) // band width is width of a single bar

}




let xAxisValue = xAxisSelect.options[xAxisSelect.selectedIndex].value;
if(xAxisValue != ''){
  axisChange()
}



exportButton.addEventListener("click", () => {
  saveSvgAsPng(document.getElementsByTagName("svg")[0], "plot.png", {scale: 2, backgroundColor: "#FFFFFF"});
})


// Prevent form auto submitting when a user presses Enter
$(document).on("keydown", "form", function(event) {
    return event.key != "Enter";
});


$('body').on('keydown', 'input, select', function(e) {
  if (e.key === "Enter") {
    var self = $(this), form = self.parents('form:eq(0)'), focusable, next;
    focusable = form.find('input,a,select,button,textarea').filter(':visible');
    next = focusable.eq(focusable.index(this)+1);
    if (next.length) {
      next.focus();
    } else {
      form.submit();
    }
    return false;
  }
});


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
