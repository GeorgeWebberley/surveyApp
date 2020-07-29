const xAxisSelect = document.querySelector(".x-axis-value")
const yAxisSelect = document.querySelector(".y-axis-value")
const xAxisDetails = document.querySelector(".x-axis-details")
const emptyGraph = document.querySelector(".empty-graph")
const exportButton = document.querySelector(".export")

// Get the DOM elements for all of the axes, so that we can add event listeners for when they are changed
const axesSettings = document.querySelectorAll(".axis-setting")

// Get the graph data
const data = graphData["chart_data"]


// When the axes are altered, we need to re-group the data depending on the variables set
axesSettings.forEach(setting => {
  setting.onchange = function(){
    axisChange()
  }
})


function axisChange (){
    let xAxisValue = xAxisSelect.options[xAxisSelect.selectedIndex].value;
    let yAxisValue = yAxisSelect.options[yAxisSelect.selectedIndex].value;

    // Hide the overlay
    emptyGraph.classList.remove("visible");
    emptyGraph.classList.add("hidden");

    // Remove the ' -- select an option -- ' option
    yAxisSelect.firstChild.hidden = true;
    // Reveal the y-axis variable for the user to select
    xAxisDetails.classList.remove('hidden-axis')

    // Ternary operator used to set our dataStats variable. If x-axis variable has been
    // selected then this will be a function, returning the stats for each group as an object.
    // Else it will just be an object containing the stats.
    dataStats = xAxisValue == "" ? nestData(xAxisValue, yAxisValue) : nestDataStats(xAxisValue, yAxisValue)

    let mapFunction;
    let preparedData;

    if(xAxisValue != ""){
      // Create our function to be used for calculating q1, q3 and median
      mapFunction = function(group, quartile){
        d3.quantile(group.map(g => {return g[yAxisValue]}).sort(d3.ascending), quartile)
      }
      preparedData = d3.nest().key(function(d) { return d[xAxisValue]; })
    }else{
      // Create our function to be used for calculating q1, q3 and median
      mapFunction = function(group, quartile){
        d3.quantile(group.sort(d3.ascending), quartile)
      }
      preparedData = d3.nest()
    }

    let dataStats = getData(yAxisValue, mapFunction, preparedData)
    // re-draw the graph with the chosen variables
    render(dataStats);
}


// Function used for getting different stats needed for box-whisker plot and for each group
// Returns an function that can calculate the stats for each x-axis group.
function getData(yAxisValue, mapFunction, preparedData){
  // Create our function to be used for calculating q1, q3 and median
  let mapFunction = function(group, quartile){
    d3.quantile(group.map(g => {return g[yAxisValue]}).sort(d3.ascending), quartile)
  }
  // We use our nested data to calculate the first quartile, third quartile, median, min and max
  let dataStats = preparedData
  .rollup(function(group) {
    let
      q1 = mapFunction(group, 0.25)
      median = mapFunction(group, 0.5)
      q3 = mapFunction(group, 0.75)
      interQuartileRange = q3 - q1
      min = q1 - 1.5* interQuartileRange
      max = q1 + 1.5* interQuartileRange
    return({q1: q1,
            median: median,
            q3: q3,
            interQuartileRange: interQuartileRange,
            min: min,
            max: max})
  })
  .entries(data)
  return dataStats
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


const render = (dataStats) => {
  let xAxisValue = xAxisSelect.options[xAxisSelect.selectedIndex].value;
  let yAxisValue = yAxisSelect.options[yAxisSelect.selectedIndex].value;
  let yAxisAgg = yAxisAggDom.options[yAxisAggDom.selectedIndex].value;


  // Specify the x-axis values and the y-axis valus
  const xValues = d => d.key;
  const yValues = d => d.value;

  // Remove old axes labels (if they exist)
  d3.selectAll('.label').remove();


  // Set the scale for the y-axis
  const yScale = d3.scaleLinear()
    .domain([0, d3.max(dataStats, yValues)]).nice()
    .range([gHeight, 0])

  let xDomain = xAxisValue == "" ? "" : dataStats.map(xValues)
  // Set the scale for the x-axis
  const xScale = d3.scaleBand()
    .domain(xDomain)
    .range([0, gWidth])
    .paddingInner(1)

  // Set the scale for the y-axis
  const yScale = d3.scaleLinear()
    .domain([0, d3.max(dataStats, yValues)]).nice()
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

  let vertLines = graph.selectAll('vertLines').data(dataStats)
    .enter()
    .append("line")
      .attr("x1", xScale(xValues()))
      .attr("x2", xScale(xValues()))
      .attr("y1", d => {return yScale(d.value.min)})
      .attr("y2", d => {return yScale(d.value.max)})
      .attr("stroke", "black")
      .style("width", "40")


  // Select all 'boxes' DOM elements (if they exist)
  let box = graph.selectAll('boxes').data(dataStats)
    .enter()
    .append("rect")
      .attr("x", xScale(xValues.bandwidth()))
      .attr("y", d => {return yScale(d.value.q3) })
      .attr("height", d => {(yScale(d.value.q1)-yScale(d.value.q3)) })
      .attr("width", xScale.bandwidth() )
      .attr("stroke", "black")
      .style("fill", "#69b3a2")


  // // D3 'exit()' is what happens to DOM elements that no longer have data bound to them
  // // Given a transition that shrinks them down to the x-axis
  // box.exit().transition()
  // .duration(1000)
  // .attr("y", yScale(0))
  // .attr('height', 0)
  // .remove()
  //
  // // D3 'enter()' is the creation of DOM elements bound to the data
  // var boxPlot = box.enter()
  // .append('rect')
  //     .attr("y",  yScale(0))
  //     .attr('x', d => xScale(xValues(d)))
  //     .attr('width', xScale.bandwidth()) // band width is width of a single bar
  //     .style('fill', 'steelblue')
  //
  //
  // // For the colour, I had to convert the 'primary-colour-dark' variable into a hex colour so that the effect can work
  // bar.on('mouseenter', function(d) {
  //   d3.select(this)
  //   .transition()
  //   .duration(100)
  //   .style('fill', '#2D4053')
  //
  //
  //   var tooltipOffset = (d3.select(this).attr("width") - 80)/2;
  //
  //   var tooltip = d3.select(".graph-tooltip")
  //
  //   // To position the tool tip when the user hovers. Use the window and calculate the offset
  //   var position = this.getScreenCTM()
  //       .translate(+ this.getAttribute("x"), + this.getAttribute("y"));
  //
  //   // Now give the tooltip the data it needs to show and the position it should be.
  //   tooltip.html(xValues(d)+": " + yValues(d))
  //       .style("left", (window.pageXOffset + position.e + tooltipOffset) + "px") // Center it horizontally over the bar
  //       .style("top", (window.pageYOffset + position.f - 50) + "px"); // Shift it 50 px above the bar
  //
  //
  //
	// 	tooltip.classed("tooltip-hidden", false)
  //
  // }).on('mouseout', function() {
  //   d3.select(this)
  //   .transition()
  //   .style('fill', 'steelblue')
  //
  //   d3.select(".graph-tooltip").classed("tooltip-hidden", true);
  // })
  //
  // bar.merge(rect)  // 'merge' merges the 'enter' and 'update' groups
  //     .transition()
  //     .delay(d =>  xScale(xValues(d))/2 )
  //     .duration(1000)
  //     .attr('height', d => gHeight - yScale(yValues(d)))
  //     .attr('y', d=>  yScale(yValues(d)))
  //     .attr('x', d => xScale(xValues(d)))
  //     .attr('width', xScale.bandwidth()) // band width is width of a single bar
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
  // prevent default form submission
  e.preventDefault();
  // call function to post form (separate js file)
  postgraph(width, height)
});
