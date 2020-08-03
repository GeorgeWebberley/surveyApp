const xAxisSelect = document.querySelector(".x-axis-value")
const yAxisSelect = document.querySelector(".y-axis-value")
const xAxisDetails = document.querySelector(".x-axis-details")
const emptyGraph = document.querySelector(".empty-graph")
const exportButton = document.querySelector(".export")

// Get the DOM elements for all of the axes, so that we can add event listeners for when they are changed
const axesSettings = document.querySelectorAll(".axis-setting")

// Colours for our graph
const fill = "steelblue"
const hoverFill = "#2D4053"

// Get the graph data
const data = graphData["chart_data"]


// Set graph dimensions
var width = document.getElementById('graph').clientWidth;
var height = document.getElementById('graph').clientHeight;
// Re set dimensions on window resize
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

function axisChange (){
    let xAxisValue = xAxisSelect.options[xAxisSelect.selectedIndex].value;
    let yAxisValue = yAxisSelect.options[yAxisSelect.selectedIndex].value;

    // Hide the overlay
    emptyGraph.classList.remove("visible");
    emptyGraph.classList.add("invisible");

    // Remove the ' -- select an option -- ' option
    yAxisSelect.firstChild.hidden = true;
    // Reveal the y-axis variable for the user to select
    xAxisDetails.classList.remove('hidden-down')

    let dataStats = getData(yAxisValue, xAxisValue)
    // re-draw the graph with the chosen variables
    render(dataStats);
}


// Function used for getting different stats needed for box-whisker plot and for each group
// Returns an function that can calculate the stats for each x-axis group.
function getData(yAxisValue, xAxisValue){

  // We use our nested data to calculate the first quartile, third quartile, median, min and max
  var dataStats = d3.nest() // nest function allows to group the calculation per level of a factor
  // Depending if user selects a x-axis variable, we group the data
    .key(function(d) { return xAxisValue == "" ? 1 : d[xAxisValue]})
    .rollup(function(d) {
      let
        orderedArray = d.map(g => g[yAxisValue]).sort(d3.ascending)
        q1 = d3.quantile(orderedArray,.25)
        median = d3.quantile(orderedArray,.5)
        q3 = d3.quantile(orderedArray,.75)
        interQuantileRange = q3 - q1
        // Whiskers can have multiple different meanings. In mine, I have decided to
        // go with the commonly used highest-value and lowest-values
        // min = q1 - 1.5 * interQuantileRange
        // max = q3 + 1.5 * interQuantileRange
        min = d3.min(orderedArray)
        max = d3.max(orderedArray)
      return({q1: q1, median: median, q3: q3, interQuantileRange: interQuantileRange, min: min, max: max})
    })
    .entries(data)
  return dataStats
}


function render(dataStats){
  let xAxisValue = xAxisSelect.options[xAxisSelect.selectedIndex].value;
  let yAxisValue = yAxisSelect.options[yAxisSelect.selectedIndex].value;

  // Specify the x-axis values and the y-axis valus
  const xValues = d => d.key;
  const hoverText = d => `
  Q1: <strong class="badge badge-dark">${d.value.q1}</strong>
  Q3: <strong class="badge badge-dark">${d.value.q3}</strong>
  Median: <strong class="badge badge-dark">${d.value.median}</strong>
  Max: <strong class="badge badge-dark">${d.value.max}</strong>
  Min: <strong class="badge badge-dark">${d.value.min}</strong>
  `;

  // Remove old axes labels (if they exist)
  d3.selectAll('.label').remove();

  // Get the highest value from our objects so we can base the y-axis on that.
  // I could instead find the highest value in that column. However, doing it this way
  // it means I can change the definition of the whiskers without needing to change
  // in both places. See above.
  let yMax = Math.max.apply(Math, dataStats.map(function(object) { return object.value.max}))
  // Set the scale for the y-axis
  const yScale = d3.scaleLinear()
    .domain([0, yMax]).nice()
    .range([gHeight, 0])

  // Set the scale for the x-axis
  const xScale = d3.scaleBand()
    .domain(dataStats.map(xValues))
    .range([0, gWidth])
    .paddingInner(.3)
    .paddingOuter(.1)


  // Select the axes (if they exist)
  var yAxis = d3.selectAll(".yAxis")
  var xAxis = d3.selectAll(".xAxis")

  // If they dont exist, we create them. If they do, we update them
  if (yAxis.empty() && xAxis.empty()){
    // For the x-axis we create an axisBottom and 'translate' it so it appears on the bottom of the graph
    graph.append('g').attr("class", "xAxis").call(d3.axisBottom(xScale))
    .attr("transform", `translate(0, ${gHeight})`)
    // For y axis we do not need to translate it, as the default is on the left
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

  let yAxisLabel = yAxisValue

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


  let boxDom = graph.selectAll("rect").data(dataStats)
  let medianDom = graph.selectAll(".medianLine").data(dataStats)
  let vertDom = graph.selectAll(".vertLine").data(dataStats)
  let minDom = graph.selectAll(".minLine").data(dataStats)
  let maxDom = graph.selectAll(".maxLine").data(dataStats)

  // Exit functions, for when the SVG elements are no longer linked with data elements
  medianDom.exit().remove()
  vertDom.exit().remove()
  minDom.exit().remove()
  maxDom.exit().remove()
  boxDom.exit()
    .transition()
    .duration(600)
    .attr("height", 0)
    .attr("width", 0)
    .remove()

  // ------Vertical line enter, merge and exit functions------
  let vertical = vertDom
    .enter()
    .append("line")
      .attr("class", "vertLine")
      .attr("x1", d => xScale(xValues(d)) + xScale.bandwidth()/2)
      .attr("x2", d => xScale(xValues(d)) + xScale.bandwidth()/2)
      .attr("y1", d => yScale(d.value.median))
      .attr("y2", d => yScale(d.value.median))
      .attr("stroke", "black")
      .style("width", "40")

  vertical.merge(vertDom)
    .transition()
    .delay(d =>  xScale(xValues(d))/2 )
    .duration(300)
    .attr("x1", d => xScale(xValues(d)) + xScale.bandwidth()/2)
    .attr("x2", d => xScale(xValues(d)) + xScale.bandwidth()/2)
    .attr("y1", d => {return yScale(d.value.min)})
    .attr("y2", d => {return yScale(d.value.max)})

  // ------Box enter, merge and exit functions------
  let box = boxDom
    .enter()
    .append("rect")
      .attr("x", d => xScale(d.key) + xScale.bandwidth()/2)
      .attr("y", d => yScale(d.value.median))
      .attr("height", 0)
      .attr("width", 0)
      .attr("stroke", "black")
      .style('fill', fill)

  setTooltip(box, hoverText, xValues)

  box.merge(boxDom)  // 'merge' merges the 'enter' and 'update' groups
      .transition()
      .delay(d =>  xScale(xValues(d))/2 )
      .duration(600)
        .attr("x", d => {return xScale(xValues(d))})
        .attr("y", d => {return yScale(d.value.q3) })
        .attr("width", xScale.bandwidth())
        .attr("height", d => {return (yScale(d.value.q1)-yScale(d.value.q3)) })


  // ------Median enter, merge and exit functions------
  let median = medianDom
    .enter()
    .append("line")
    .attr("class", "medianLine")
      .attr("y1", d => yScale(d.value.median))
      .attr("y2", d => yScale(d.value.median))
      .attr("x1", d => xScale(d.key)+xScale.bandwidth()/2)
      .attr("x2", d => xScale(d.key)+xScale.bandwidth()/2)
      .attr("stroke", "black")
      .style("width", 80)

  median.merge(medianDom)  // 'merge' merges the 'enter' and 'update' groups
      .transition()
      .delay(d =>  xScale(xValues(d))/2 )
      .duration(600)
      .attr("y1", d => yScale(d.value.median))
      .attr("y2", d => yScale(d.value.median))
      .attr("x1", d => xScale(d.key))
      .attr("x2", d => xScale(d.key)+xScale.bandwidth())


  // ------Min line enter, merge and exit functions------
  let min = minDom
    .enter()
    .append("line")
    .attr("class", "minLine")
      .attr("y1", d => yScale(d.value.min))
      .attr("y2", d => yScale(d.value.min))
      .attr("x1", d => xScale(d.key)+xScale.bandwidth()/2)
      .attr("x2", d => xScale(d.key)+xScale.bandwidth()/2)
      .attr("stroke", "black")
      .style("width", 80)

  min.merge(minDom)  // 'merge' merges the 'enter' and 'update' groups
      .transition()
      .delay(d =>  300 + xScale(xValues(d))/2 )
      .duration(600)
      .attr("y1", d => yScale(d.value.min))
      .attr("y2", d => yScale(d.value.min))
      .attr("x1", d => xScale(d.key)+xScale.bandwidth()/4)
      .attr("x2", d => xScale(d.key)+xScale.bandwidth()*3/4)

  // ------Min line enter, merge and exit functions------
  let max = maxDom
    .enter()
    .append("line")
    .attr("class", "maxLine")
      .attr("y1", d => yScale(d.value.max))
      .attr("y2", d => yScale(d.value.max))
      .attr("x1", d => xScale(d.key)+xScale.bandwidth()/2)
      .attr("x2", d => xScale(d.key)+xScale.bandwidth()/2)
      .attr("stroke", "black")
      .style("width", 80)

  max.merge(maxDom)  // 'merge' merges the 'enter' and 'update' groups
      .transition()
      .delay(d =>  300 + xScale(xValues(d))/2 )
      .duration(600)
      .attr("y1", d => yScale(d.value.max))
      .attr("y2", d => yScale(d.value.max))
      .attr("x1", d => xScale(d.key)+xScale.bandwidth()/4)
      .attr("x2", d => xScale(d.key)+xScale.bandwidth()*3/4)

}

// Function that sets tooltip over each box and whisker when hovered over
function setTooltip(box, hoverText, xValues){
  box.on('mouseenter', function(d) {
    d3.select(this)
    .transition()
    .duration(100)
    .style('fill', hoverFill)

    let tooltip = d3.select(".graph-tooltip")
    // 80 chosen as it positions the tooltip in an appropriate location to the boxes
    let tooltipOffset = (d3.select(this).attr("width") - 80)/2;

    // To position the tool tip when the user hovers. Use the window and calculate the offset
    let position = this.getScreenCTM()
        .translate(+ this.getAttribute("x"), + this.getAttribute("y"));

    // Now give the tooltip the data it needs to show and the position it should be.
    tooltip
        .html(xValues(d) + "<br>" + hoverText(d))
        .style("left", (window.pageXOffset + position.e + tooltipOffset) + "px") // Center it horizontally over the box
        .style("top", (window.pageYOffset + position.f - 80) + "px"); // Shift it 80 px above the box

    // Finally remove the 'hidden' class
    tooltip.classed("tooltip-hidden", false)
  }).on('mouseout', function() {
    d3.select(this)
    .transition()
    .duration(100)
    .style('fill', fill)
    // When the mouse is removed from the box we can add the hidden class to the tooltip again
    d3.select(".graph-tooltip").classed("tooltip-hidden", true);
  })
}


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
