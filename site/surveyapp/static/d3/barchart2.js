const xAxisSelect = document.querySelector(".x-axis-value")
const yAxisSelect = document.querySelector(".y-axis-value")
const yAxisDetails = document.querySelector(".y-axis-details")
const yAxisAggDom = document.querySelector(".y-axis-aggregation")
const aggregate = document.querySelector(".aggregate")
const emptyGraph = document.querySelector(".empty-graph")
const exportButton = document.querySelector(".export")
// const saveJpg = document.querySelector(".save-as-jpg")
// const form = document.querySelector(".chart-form")

// Get the DOM elements for all of the axes, so that we can add event listeners for when they are changed
const axesSettings = document.querySelectorAll(".axis-setting")

// Get the graph data
const data = graphData["chart_data"]



// DATA GROUPING FUNCTION. CALLED WHEN AN AXIS SETTING CHANGES
function groupData(xAxisValue, yAxisValue){
  // We can create a 'nested' D3 object, with the key as the chosen x-axis variable
  let nestedData = d3.nest().key(function(d) { return d[xAxisValue]; })

  // If the y axis is just to count the values, we can group and perform a roll up on the calculation of the length
  if(yAxisValue == "Amount"){
    return nestedData
    .rollup(function(v) { return v.length; })
    .entries(data)
  }
  // Else, we need to see which y-axis aggregation was chosen
  let yAxisAgg = yAxisAggDom.options[yAxisAggDom.selectedIndex].value;
  if(yAxisAgg == "Average"){
    return nestedData
      .rollup(function(v) { return d3.mean(v, function(d) { return d[yAxisValue]; }); })
      .entries(data)
  }
  if(yAxisAgg == "Highest"){
    return nestedData
      .rollup(function(v) { return d3.max(v, function(d) { return d[yAxisValue]; }); })
      .entries(data)
  }
  if(yAxisAgg == "Lowest"){
    return nestedData
      .rollup(function(v) { return d3.min(v, function(d) { return d[yAxisValue]; }); })
      .entries(data)
  }
  if(yAxisAgg == "Sum"){
    return nestedData
      .rollup(function(v) { return d3.sum(v, function(d) { return d[yAxisValue]; }); })
      .entries(data)
  }
}



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
    emptyGraph.classList.remove("visible");
    emptyGraph.classList.add("hidden");
    yAxisDetails.classList.remove('hidden-axis')

    xAxisSelect.firstChild.hidden = true;
    // Reveal the y-axis variable for the user to select
    yAxisDetails.classList.remove('hidden-axis')


    // If the chosen y variable is equal to 'Amount' then we don't want to give the user the option to perform data aggregations
    if(yAxisValue != 'Amount'){
      aggregate.classList.remove('hidden-axis')
      aggregate.classList.add('visible')
    } else{
      aggregate.classList.remove('visible')
      aggregate.classList.add('hidden-axis')
    }
    // A function that carries ou the grouping, based on the chosen settings
    let groupedData = groupData(xAxisValue, yAxisValue);

    // re-draw the graph with the chosen variables
    render(data, groupedData);
}



// Set graph dimensions
const width = 1000;
const height = 640;
// Create SVG ready for graph
// const svg = d3.select('#graph').append("svg").attr("width", width).attr("height", height)
const svg = d3.select('#graph').append("svg").attr("viewBox", "0 0 " + width + " " + height).attr("preserveAspectRatio", "xMidYMid meet");

// Set margins around graph for axis and labels
const margin = { top: 20, right: 20, bottom: 100, left: 100 };
// Set the graph width and height to account for axes
const gWidth = width - margin.left - margin.right;
const gHeight = height - margin.top - margin.bottom;

// Add the graph area to the SVG, factoring in the margin dimensions
var graph = svg.append('g').attr("transform", `translate(${margin.left}, ${margin.top})`)


const render = (data, groupedData) => {
  let xAxisValue = xAxisSelect.options[xAxisSelect.selectedIndex].value;
  let yAxisValue = yAxisSelect.options[yAxisSelect.selectedIndex].value;
  let yAxisAgg = yAxisAggDom.options[yAxisAggDom.selectedIndex].value;


  // Specify the x-axis values and the y-axis valus
  const xValues = d => d.key;
  const yValues = d => d.value;
  // Remove old graph and old axes when new graph is produced.
  // graph.remove()



  // Remove old axes (if they exist)
  d3.selectAll('.axis').remove();
  // Remove old axes labels (if they exist)
  d3.selectAll('.label').remove();

  // sort the grouped data keys in ascending order (i.e. so the x-axis is in numerical order)
  groupedData.sort(function(a, b) { return d3.ascending(parseInt(a.key), parseInt(b.key))});
  // Set the scale for the x-axis
  const xScale = d3.scaleBand()
    .domain(groupedData.map(xValues))
    .range([0, gWidth])
    .paddingInner(0.1)

  // Set the scale for the y-axis
  const yScale = d3.scaleLinear()
    .domain([0, d3.max(groupedData, yValues)])
    .range([gHeight, 0])

  // Create graph element, factoring in space for axes.
  // graph = svg.append('g')
  // .attr("transform", `translate(${margin.left}, ${margin.top})`)

  // Add new y axis
  graph.append('g').attr("class", "axis").call(d3.axisLeft(yScale))

  // Add y axis label
  svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("class", "label")
      .attr("y", 30)
      .attr("x",0 - (gHeight / 2))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .text(`${yAxisAgg}: ${yAxisValue}`);

  // Add new x axis
  graph.append('g').attr("class", "axis").call(d3.axisBottom(xScale))
    .attr("transform", `translate(0, ${gHeight})`)

  // Add x axis label
  svg.append("text")
    .attr("transform",`translate(${width/2}, ${gHeight + margin.top + 50})`)
    .attr("class", "label")
    .text(xAxisValue);

  // Select all 'rect' DOM elements (if they exist)
  var rect = graph.selectAll('rect').data(groupedData)

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
      .attr('x', d => xScale(xValues(d)))
      .attr('width', xScale.bandwidth()) // band width is width of a single bar
      .style('fill', 'steelblue')


  // For the colour, I had to convert the 'primary-colour-dark' variable into a hex colour so that the effect can work
  bar.on('mouseenter', function(d) {
    d3.select(this)
    .transition()
    .duration(100)
    .style('fill', '#2D4053')


    var tooltipOffset = (d3.select(this).attr("width") - 80)/2;

    var tooltip = d3.select(".tooltip")

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

    d3.select(".tooltip").classed("tooltip-hidden", true);
  })

  bar.merge(rect)  // 'merge' merges the 'enter' and 'update' groups
      .transition()
      .delay(d =>  xScale(xValues(d))/2 )
      .duration(1000)
      .attr('height', d => gHeight - yScale(yValues(d)))
      .attr('y', d=>  yScale(yValues(d)))
      .attr('x', d => xScale(xValues(d)))
      .attr('width', xScale.bandwidth()) // band width is width of a single bar
}

let xAxisValue = xAxisSelect.options[xAxisSelect.selectedIndex].value;
if(xAxisValue != ''){
  axisChange()
}





exportButton.addEventListener("click", () => {
  saveSvgAsPng(document.getElementsByTagName("svg")[0], "plot.png", {scale: 2, backgroundColor: "#FFFFFF"});
})


// function svg2Png(svg, postData){
//   var canvas = document.createElement('canvas'); // Create a Canvas element.
//   var ctx = canvas.getContext('2d'); // For Canvas returns 2D graphic.
//   var data = svg.outerHTML; // Get SVG element as HTML code.
//   canvg(canvas, data); // Render SVG on Canvas.
//   postData(canvas); // Execute callback function.
// }
//
//
// function postData(canvas){
//
// }



// When the form is submitted, we want to get a jpg image of the svg
$('form').submit(function (e) {

  e.preventDefault();
  // svg.node().setAttribute('xlink', 'http://www.w3.org/1999/xlink');
  // var serializer = new XMLSerializer();
	// var svgString = serializer.serializeToString(svg.node());
  // var imgsrc = 'data:image/svg+xml;base64,'+ btoa( unescape( encodeURIComponent( svgString ) ) ); // Convert SVG string to data URL
  //
	// var canvas = document.createElement("canvas");
	// var context = canvas.getContext("2d");
  // let form = this
	// canvas.width = width;
	// canvas.height = height;
  //
	// var image = new Image();
	// image.onload = function() {
	// 	context.clearRect ( 0, 0, width, height );
	// 	context.drawImage(image, 0, 0, width, height);
	// 	canvas.toBlob( function(blob) {
	// 		var filesize = Math.round( blob.length/1024 ) + ' KB';
	// 		// if ( callback ) callback( blob, filesize );
	// 	});
	// };

  // svg2Png(svg, postData)

  //
  // let canvas = document.createElement('canvas');
  // const ctx = canvas.getContext('2d');
  // let image = canvg.Canvg.fromString(ctx, svg.outerHTML);
  // image.start()
  // console.log(image.toDataURL('image/png'));
  // // let imageData = image.toDataURL('image/png');
  // // canvg(canvas, svg);
  // // let imgData = canvas.toDataURL('image/png');




// -------THIS NEARLY WORKS------
  // var img = new Image(),
  //     serializer = new XMLSerializer(),
  //     svgStr = serializer.serializeToString(svg.node());
  //
  // img.src = 'data:image/svg+xml;base64,'+window.btoa(svgStr);
  //
  // // You could also use the actual string without base64 encoding it:
  // // img.src = "data:image/svg+xml;utf8," + svgStr;
  // window.open().document.write('<img src="' + img.src + '"/>');
  //
  //
  // var canvas = document.createElement("canvas");
  // document.body.appendChild(canvas);
  //
  // canvas.width = width;
  // canvas.height = height;
  // canvas.getContext("2d").drawImage(img,0,0,width,height);
  // var imgData = canvas.toDataURL('image/jpeg');
  //
  //
  // imageData = img.src
// --------------------


  var doctype = '<?xml version="1.0" standalone="no"?>'
               + '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">';

  var source = (new XMLSerializer()).serializeToString(svg.node());

  var blob = new Blob([ doctype + source], { type: 'image/svg+xml' });

  var url = window.URL.createObjectURL(blob);
  var img = new Image();





    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrf)
        }
      }
    })

    var postData = $('form').serializeArray()
    postData.push({name: "image", value: "hello"})
    // console.log(imgData);
    $.ajax({
        type: "POST",
        url: url,
        data: postData,
        success: function () {
          // window.location.href = redirectUrl;
          // console.log("success");
        }
    });






  img.onload = function(){
    var canvas = d3.select('body').append('canvas').node();
    canvas.width = width;
    canvas.height = height;

    var ctx = canvas.getContext('2d');

    // draw image on canvas
    ctx.drawImage(img, 0, 0);
    var imgData = canvas.toDataURL("image/jpeg");
    canvas.remove();
    console.log("hello");
    // ajax call to send canvas(base64) url to server.

  }

  img.src =  url;



});
