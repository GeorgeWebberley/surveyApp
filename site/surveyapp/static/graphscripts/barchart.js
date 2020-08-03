// ------VARIABLE DECLARATIONS------
const xAxisSelect = document.querySelector(".x-axis-value")
const yAxisSelect = document.querySelector(".y-axis-value")
const yAxisDetails = document.querySelector(".y-axis-details")
const yAxisAggDom = document.querySelector(".y-axis-aggregation")
const aggregate = document.querySelector(".aggregate")
const emptyGraph = document.querySelector(".empty-graph")
const exportButton = document.querySelector(".export")

// Get the DOM elements for all of the axes, so that we can add event listeners for when they are changed
const axesSettings = document.querySelectorAll(".axis-setting")

// Colours for our graph
const fill = "steelblue"
const hoverFill = "#2D4053"

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
// When the axes are altered, we need to re-group the data depending on the variables set
axesSettings.forEach(setting => {
  setting.onchange = function(){
    axisChange()
  }
})

// If the value is not equal to an empty string on page load (i.e. user is editing graph)
if(xAxisSelect.options[xAxisSelect.selectedIndex].value != ''){
  axisChange()
}

// Export button that allows user to export and download the SVG as a PNG image
exportButton.addEventListener("click", () => {
  let title = document.querySelector(".title").value
  let exportTitle = title == "" ? "plot.png": `${title}.png`
  saveSvgAsPng(document.getElementsByTagName("svg")[0], exportTitle, {scale: 2, backgroundColor: "#FFFFFF"});
})


// ------FUNCTIONS------
function axisChange (){
  // Get the selected values
  let xAxisValue = xAxisSelect.options[xAxisSelect.selectedIndex].value;
  let yAxisValue = yAxisSelect.options[yAxisSelect.selectedIndex].value;
  let yAxisAgg = yAxisAggDom.options[yAxisAggDom.selectedIndex].value;
  // Hide the overlay if it is still present
  emptyGraph.classList.remove("visible");
  emptyGraph.classList.add("invisible");

  // Remove the ' -- select an option -- ' option
  xAxisSelect.firstChild.hidden = true;
  // Reveal the y-axis variable for the user to select
  yAxisDetails.classList.remove('hidden-down')

  // If the chosen y variable is equal to 'Amount' then we don't want to give the user the option to perform data aggregations
  if(yAxisValue != 'Amount'){
    aggregate.classList.remove('hidden-down')
    aggregate.classList.add('visible')
  } else{
    aggregate.classList.remove('visible')
    aggregate.classList.add('hidden-down')
  }
  // Get the grouped data based on the chose variables
  let groupedData = groupData(xAxisValue, yAxisValue);

  // draw the graph with the chosen variables
  render(groupedData, xAxisValue, yAxisValue, yAxisAgg);
}


// Data grouping function. Called whenever an axis setting changes
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


// Function that draws the graph
function render(groupedData, xAxisValue, yAxisValue, yAxisAgg){
  // Specify the x-axis values and the y-axis valus
  const xValues = d => d.key;
  const yValues = d => d.value;

  // Remove old axes labels (if they exist)
  d3.selectAll('.label').remove();

  // sort the grouped data keys in ascending order (so the x-axis is in numerical order)
  groupedData.sort(function(a, b) { return d3.ascending(parseInt(a.key), parseInt(b.key))});
  // Set the scale for the x-axis (domain is the range of our data, range is the physical width of the graph)
  const xScale = d3.scaleBand()
    .domain(groupedData.map(xValues))
    .range([0, gWidth])
    .paddingInner(0.1)

  // Set the scale for the y-axis
  const yScale = d3.scaleLinear()
    .domain([0, d3.max(groupedData, yValues)]).nice()
    .range([gHeight, 0])

  // Select the axes (if they exist)
  let yAxis = d3.selectAll(".yAxis")
  let xAxis = d3.selectAll(".xAxis")

  // If they dont exist, we create them. If they do, we update them
  if (yAxis.empty() && xAxis.empty()){
    // For the x-axis we create an axisBottom and 'translate' it so it appears on the bottom of the graph
    graph.append('g').attr("class", "xAxis").call(d3.axisBottom(xScale))
    .attr("transform", `translate(0, ${gHeight})`)
    // For y axis we do not need to translate it, as the default is on the left
    graph.append('g').attr("class", "yAxis").call(d3.axisLeft(yScale))
  } else {
    // Adjust the x-axis according the x-axis variable data
    xAxis.transition().duration(1000).call(d3.axisBottom(xScale))
    // Adjust the y-axis according the y-axis variable data
    yAxis.transition().duration(1000).call(d3.axisLeft(yScale))
  }

  // If the yAxis is 'Amount' we can leave the label as it is, otherwise we need to add the type of aggregation
  let yAxisLabel = yAxisValue == 'Amount' ? 'Amount' : `${yAxisAgg}: ${yAxisValue}`

  // Add y axis label
  svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("class", "label")
      .attr("y", 0)
      .attr("x",0 - (gHeight / 2))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .text(yAxisLabel);

  // Add x axis label
  svg.append("text")
    .attr("transform",`translate(${width/2}, ${gHeight + margin.top + 55})`)
    .attr("class", "label")
    .text(xAxisValue);

  // Select all 'rect' DOM elements (if they exist)
  let rect = graph.selectAll('rect').data(groupedData)

  // D3 'exit()' is what happens to DOM elements that no longer have data bound to them
  // Given a transition that shrinks them down to the x-axis before removing
  rect.exit().transition()
  .duration(1000)
  .attr("y", yScale(0))
  .attr('height', 0)
  .remove()

  // D3 'enter()' is the creation of DOM elements bound to the data
  // At this stage, the bars are all flat along the x-axis
  let bar = rect.enter()
  .append('rect')
      .attr("y",  yScale(0))
      .attr('x', d => xScale(xValues(d)))
      .attr('width', xScale.bandwidth()) // band width is width of a single bar
      .style('fill', fill)

  // Tooltip needs to be set before merging?????
  setTooltip(bar, xValues, yValues)

  // Finally, we merge the newly entered bars with the existing ones.
  // (i.e. merges the 'enter and 'update' groups)
  bar.merge(rect)  // 'merge' merges the 'enter' and 'update' groups
      .transition()
      .delay(d =>  xScale(xValues(d))/2 )
      .duration(1000)
      .attr('height', d => gHeight - yScale(yValues(d)))
      .attr('y', d=>  yScale(yValues(d)))
      .attr('x', d => xScale(xValues(d)))
      .attr('width', xScale.bandwidth()) // band width is width of a single bar
}

// Function that sets tooltip over each bar when hovered over
function setTooltip(bar, xValues, yValues){
  bar.on('mouseenter', function(d) {
    d3.select(this)
    .transition()
    .duration(100)
    .style('fill', hoverFill)
    let tooltip = d3.select(".graph-tooltip")
    // 80 chosen to position the tooltip above bars
    let tooltipOffset = (d3.select(this).attr("width") - 80)/2;

    // To position the tool tip when the user hovers. Use the window and calculate the offset
    let position = this.getScreenCTM()
        .translate(+ this.getAttribute("x"), + this.getAttribute("y"));

    // Now give the tooltip the data it needs to show and the position it should be.
    tooltip.html(xValues(d)+": " + yValues(d))
        .style("left", (window.pageXOffset + position.e + tooltipOffset) + "px") // Center it horizontally over the bar
        .style("top", (window.pageYOffset + position.f - 50) + "px"); // Shift it 50 px above the bar
    // Finally remove the 'hidden' class
    tooltip.classed("tooltip-hidden", false)
  }).on('mouseout', function() {
    d3.select(this)
    .transition()
    .duration(100)
    .style('fill', fill)
    // When the mouse is removed from the bar we can add the hidden class to the tooltip again
    d3.select(".graph-tooltip").classed("tooltip-hidden", true);
  })
}


// When the form is submitted, we want to get a jpg image of the svg
$('form').submit(function (e) {
  // prevent default form submission
  e.preventDefault();
  // call function to post form (separate js file)
  postgraph(width, height)
});
