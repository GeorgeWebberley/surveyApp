// ------VARIABLE DECLARATIONS------
const xAxisSelect = document.querySelector(".x-axis-value")
const emptyGraph = document.querySelector(".empty-graph") //overlay
const exportButton = document.querySelector(".export")
const settingsGroup = document.querySelector(".extra-settings-group")
const extraSettings = document.querySelectorAll(".extra-setting")
// x-axis range
const xFrom = document.querySelector(".x-from")
const xTo = document.querySelector(".x-to")
const numberOfGroups = document.querySelector(".number-groups")
// Get the DOM elements for all of the axes, so that we can add event listeners for when they are changed
const axisSettings = document.querySelector(".axis-setting")

// Get the graph data
const data = graphData["chart_data"]

// Get the width and height of the SVG on the client screen
let width = document.getElementById('graph').clientWidth;
let height = document.getElementById('graph').clientHeight;
// Re-set the width and height on window resize
window.onresize = function(){
  width = document.getElementById('graph').clientWidth;
  height = document.getElementById('graph').clientHeight;
  svg.attr('width', width).attr('height', height);
}
// Set margins around graph for axis and labels
const margin = { top: 20, right: 20, bottom: 60, left: 80 };
// Set the graph width and height to account for margins
const gWidth = width - margin.left - margin.right;
const gHeight = height - margin.top - margin.bottom;

// Create SVG ready for graph
const svg = d3.select('#graph')
              .append("svg")
                .attr("width", width)
                .attr("height", height)
                .attr("viewBox", "0 0 " + width + " " + height)
                .attr("preserveAspectRatio", "none")

// Add the graph area to the SVG, factoring in the margin dimensions
let graph = svg.append('g').attr("transform", `translate(${margin.left}, ${margin.top})`)
// ------END OF VARIABLE DECLARATIONS------

// ------EVENT LISTENERS------
// When the axis is altered, we trigger the graph rendering
axisSettings.onchange = function(){
  axisChange()
}

// If the x-axis is not an empty string on page load (i.e. if user is editing a graph)
if(xAxisSelect.options[xAxisSelect.selectedIndex].value != ''){
  axisChange()
}

// When the x-axis range is altered or the group size is altered, we need to re-render the table
// We do not need to call 'axisChange' as the variables themselves haven't changed
extraSettings.forEach(input => {
  input.onchange = function() {
    render(data)
  }
})

// Export button that allows user to export and download the SVG as a PNG image
exportButton.addEventListener("click", () => {
  saveSvgAsPng(document.getElementsByTagName("svg")[0], "plot.png", {scale: 2, backgroundColor: "#FFFFFF"});
})


// ------FUNCTIONS FOR DRAWING GRAPH------
// Resets some options and handles DOM elements visibility
function axisChange (){
    // Reset the axis range and number of groups when user selects a new variable
    xFrom.value = ""
    xTo.value = ""
    numberOfGroups.value == ""
    // Remove the ' -- select an option -- ' option
    xAxisSelect.firstChild.hidden = true;

    // Reveal the extra settings
    settingsGroup.classList.remove('hidden-axis')

    // Make the overlay hidden
    emptyGraph.classList.remove("visible");
    emptyGraph.classList.add("hidden");

    // re-draw the graph with the chosen variables
    render(data);
}

// Draws the graph with the chosen variable
function render(data){
  let xAxisValue = xAxisSelect.options[xAxisSelect.selectedIndex].value;

  // Specify the x-axis values and the y-axis values
  const xValues = d => d[xAxisValue];
  const yValues = d => d.length;

  // Remove old axes labels (if they exist)
  d3.selectAll('.label').remove();

  // sort the data keys in ascending order (i.e. so the x-axis is in numerical order)
  // IS THIS NEEDED?
  // data.sort(function(a, b) { return d3.ascending(parseInt(a.key), parseInt(b.key))});

  // set the input fields for the domain (i.e. range of values) if not yet set
  if(xFrom.value == "") xFrom.value = d3.min(data, xValues)
  if(xTo.value == "") xTo.value = d3.max(data, xValues)

  // Now extract the range from the values (if they are specifed by user)
  // If the values specified by the user are outside the range of the data, increase the range
  // else use the range of the data as default.
  let xFromValue = xFrom.value = Math.min(d3.min(data, xValues), xFrom.value)
  let xToValue = xTo.value = Math.max(d3.max(data, xValues), xTo.value)

  // Set the scale for the x-axis
  const xScale = d3.scaleLinear()
    .domain([xFromValue, xToValue]).nice()
    .range([0, gWidth])

  let groups;
  // If the user hasn't specified the number of groups, we will use the default of xScale.ticks()
  if(numberOfGroups.value == ""){
    groups = xScale.ticks()
    numberOfGroups.value = xScale.ticks().length-1
  }else{
    groups = numberOfGroups.value
  }

  let histogram = d3.histogram()
    .value(xValues)
    .domain(xScale.domain())
    .thresholds(groups)

  let bins = histogram(data)

  // Set the scale for the y-axis based on the size of the biggest bin
  const yScale = d3.scaleLinear()
    .domain([0, d3.max(bins, d => d.length)]).nice()
    .range([gHeight, 0])

  // Select the axes (if they exist)
  let yAxis = d3.selectAll(".yAxis")
  let xAxis = d3.selectAll(".xAxis")

  // Get the position of the y-axis (as it will shift with negative x-axis data)
  let yPosition = (0 > xFromValue && 0 < xToValue) ? xScale(0) : 0

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
      .text("Frequency");

  // Add x axis label (again, translated to the correct position)
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
  let bar = rect.enter()
  .append('rect')
      .attr("y",  yScale(0))
      .attr('x', d => xScale(d.x0))
      .attr('width', d => Math.max(0, xScale(d.x1) - xScale(d.x0) - 1)) // width of a single bar
      .style('fill', 'steelblue')

  setTooltip(bar, yValues)

  bar.merge(rect)  // 'merge' merges the 'enter' and 'update' groups
      .transition()
      .duration(1000)
      .attr('height', d => yScale(0) - yScale(d.length))
      .attr('y', d => yScale(d.length))
      .attr('x', d => xScale(d.x0))
      .attr('width', d => Math.max(0, xScale(d.x1) - xScale(d.x0) - 1)) // band width is width of a single bar
}


// Function that sets tooltip over each bar when hovered over
function setTooltip(bar, yValues){
  // For the colour, I had to convert the 'primary-colour-dark' variable into a hex colour so that the effect can work
  bar.on('mouseenter', function(d) {
    d3.select(this)
    .transition()
    .duration(100)
    .style('fill', '#2D4053')

    let tooltip = d3.select(".graph-tooltip")
    let tooltipOffset = (d3.select(this).attr("width") - 80)/2;
    // To position the tool tip when the user hovers. Use the window and calculate the offset
    let position = this.getScreenCTM()
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
    // Hide the tooltip
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

// Function required to activate the 'help' tooltip on the axis
$(function () {
    $("[data-toggle='help']").tooltip();
});

// When the form is submitted, we want to get a jpg image of the svg
$('form').submit(function (e) {
  // prevent default form submission
  e.preventDefault();
  // call function to post form (separate js file)
  postgraph(width, height)
});
