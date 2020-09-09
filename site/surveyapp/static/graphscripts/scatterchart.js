// VARiABLE DECLARATIONS
// Get the DOM elements for all of the axes, so that we can add event listeners for when they are changed
const axesSettings = document.querySelectorAll(".axis-setting")
const xAxisSelect = document.querySelector(".x-axis-value")
const yAxisSelect = document.querySelector(".y-axis-value")
const yAxisDetails = document.querySelector(".y-axis-details")
const emptyGraph = document.querySelector(".empty-graph")
const exportButton = document.querySelector(".export")
// Connecting line (if user wants to make a line graph)
const addLine = document.querySelector(".add-line")

const axesRange = document.querySelectorAll(".axis-range")
// x and y axis ranges
const xFrom = document.querySelector(".x-from")
const yFrom = document.querySelector(".y-from")
const xTo = document.querySelector(".x-to")
const yTo = document.querySelector(".y-to")
// Colours for our graph
const fill = "steelblue"
const hoverFill = "#2D4053"
const stroke = "steelblue"

// Get the graph data
const data = graphData["chart_data"]




// Set graph dimensions
var width = document.getElementById('graph').clientWidth;
var height = document.getElementById('graph').clientHeight;
// Re set graph size when window changes size
window.onresize = function(){
  width = document.getElementById('graph').clientWidth;
  height = document.getElementById('graph').clientHeight;
  svg.attr('width', width).attr('height', height);
}
// Set margins around graph for axis and labels
const margin = { top: 20, right: 20, bottom: 60, left: 80 };
// Set the graph width and height to account for axes
const gWidth = width - margin.left - margin.right;
const gHeight = height - margin.top - margin.bottom;
// Create SVG ready for graph
const svg = d3.select('#graph').append("svg").attr("width", width).attr("height", height).attr("viewBox", "0 0 " + width + " " + height).attr("preserveAspectRatio", "none")
// Add the graph area to the SVG, factoring in the margin dimensions
var graph = svg.append('g').attr("transform", `translate(${margin.left}, ${margin.top})`)



// EVENT LISTENERS
// Function required to activate the 'help' tooltip on the axis
$(function () {
    $("[data-toggle='help']").tooltip();
});

// If the x-axis is not empty (i.e. if user is editing graph) then call function immediately
if(xAxisSelect.options[xAxisSelect.selectedIndex].value != ''){
  axisChange()
}

// Export button that allows user to export and download the SVG as a PNG image
exportButton.addEventListener("click", () => {
  let title = document.querySelector(".title").value
  let exportTitle = title == "" ? "plot.png": `${title}.png`
  saveSvgAsPng(document.getElementsByTagName("svg")[0], exportTitle, {scale: 2, backgroundColor: "#FFFFFF"});
})


// When the axes are altered, we need to re-group the data depending on the variables set
axesSettings.forEach(setting => {
  setting.onchange = function(){
    axisChange()
  }
})

// Whenever the range changes we want to draw the graph (without having to re-get the data)
axesRange.forEach(input => {
  input.onchange = function() {
    render(data)
  }
})

// Event listener for adding a connecting line
addLine.addEventListener("change", function(){
  if(this.checked){
    d3.selectAll('.graph-line').transition().duration(1000).style("visibility", "visible");
  } else {
    d3.selectAll('.graph-line').transition().duration(1000).style("visibility", "hidden");
  }
  render(data)
})


// FUNCTIONS FOR RENDERING GRAPH
function axisChange (){
    let xAxisValue = xAxisSelect.options[xAxisSelect.selectedIndex].value;
    let yAxisValue = yAxisSelect.options[yAxisSelect.selectedIndex].value;

    // Remove the ' -- select an option -- ' option
    xAxisSelect.firstChild.hidden = true;
    yAxisSelect.firstChild.hidden = true;

    // Reveal the y-axis variable for the user to select
    yAxisDetails.classList.remove('hidden-down')

    // If the user has selected variables for both the x and the y axes
    if (xAxisValue != "" && yAxisValue != ""){
      // Make the overlay hidden
      emptyGraph.classList.remove("visible");
      emptyGraph.classList.add("invisible");
      addLine.disabled = false;
      // re-draw the graph with the chosen variables
      render(data);
    }
}


function render(data){
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
  document.querySelector(".form-add-line").classList.remove("invisible")

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
    .style("text-anchor", "middle")
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
       .attr("stroke", stroke)
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
      .style('fill', fill)

  setTooltip(plot, yValues)

  plot.merge(circle)  // 'merge' merges the 'enter' and 'update' groups
      .transition()
      .delay(d =>  xScale(xValues(d))/2 )
      .duration(1000)
      .attr('cy', d=>  yScale(yValues(d)))
      .attr('cx', d => xScale(xValues(d)))

}

function setTooltip(plot, yValues){
  plot.on('mouseenter', function(d) {
    d3.select(this)
    .transition()
    .duration(100)
    .style('fill', hoverFill)

    var tooltipOffset = (d3.select(this).attr("width") - 80)/2;

    var tooltip = d3.select(".graph-tooltip")

    // To position the tool tip when the user hovers. Use the window and calculate the offset
    var position = this.getScreenCTM()
        .translate(+ this.getAttribute("cx"), + this.getAttribute("cy"));

    // Now give the tooltip the data it needs to show and the position it should be.
    tooltip.html(yValues(d))
        .style("left", (window.pageXOffset + position.e + tooltipOffset) + "px") // Center it horizontally over the plot
        .style("top", (window.pageYOffset + position.f - 80) + "px"); // Shift it 40 px above the plot

    tooltip.classed("tooltip-hidden", false)

  }).on('mouseout', function() {
    d3.select(this)
    .transition()
    .duration(100)
    .style('fill', fill)

    d3.select(".graph-tooltip").classed("tooltip-hidden", true);
  })

}






// JQUERY functions
// Function that will confirm user input when they press enter, without submitting the form
$('body').on('keydown', 'input, select', function(e) {
  if (e.key === "Enter") {
    $(this).blur()
  }
});


// When the form is submitted, we want to get a jpg image of the svg
$('form').submit(function (e) {
  // prevent default form submission
  e.preventDefault();
  // call function to post form (separate js file)
  postgraph(width, height)
});
