const xAxisSelect = document.querySelector(".x-axis-value")
const yAxisSelect = document.querySelector(".y-axis-value")
const yAxisAggDom = document.querySelector(".y-axis-aggregation")
const aggregate = document.querySelector(".aggregate")
const emptyGraph = document.querySelector(".empty-graph")

// Get the DOM elements for all of the axes, so that we can add event listeners for when they are changed
const axesSettings = document.querySelectorAll(".axis-setting")


// Function that checks if the y variable changes. If anything but 'count' is selected then the
// different aggregations will be presented to the user to choose from.
// yAxisSelect.onchange = function () {
//   var yAxisValue = yAxisSelect.options[yAxisSelect.selectedIndex].value;
//   if(yAxisValue != 'Amount'){
//     console.log("LOL");
//     aggregate.classList.remove('hidden')
//     aggregate.classList.add('visible')
//   } else{
//     console.log("nOT LOL");
//     aggregate.classList.remove('visible')
//     aggregate.classList.add('hidden')
//   }
// }



// GRAPH CREATIONG JAVASCRIPT
const data = graphData["chart_data"]
var column = "Favourite ice-cream";

result = d3.nest()
  .key(function(d) { return d[column]; })
  .rollup(function(v) { return d3.mean(v, function(d) { return d["Age"]; }); })
  .entries(data)


console.log(result);
// DATA GROUPING FUNCTION. CALLED WHEN PAGE FIRST LOADS AND


function groupData(xAxisValue, yAxisValue){
  // If the y axis is just to count the values, we can group and perform a roll up on the calculation of the length
  if(yAxisValue == "Amount"){
    return d3.nest()
    .key(function(d) { return d[xAxisValue]; })
    .rollup(function(v) { return v.length; })
    .entries(data);
  }
  // Else, we need to see which y-axis aggregation was chosen
  let yAxisAgg = yAxisAggDom.options[yAxisAggDom.selectedIndex].value;
  if(yAxisAgg == "Average"){
    return d3.nest()
      .key(function(d) { return d[xAxisValue]; })
      .rollup(function(v) { return d3.mean(v, function(d) { return d[yAxisValue]; }); })
      .entries(data)
  }
  if(yAxisAgg == "Highest"){
    return d3.nest()
      .key(function(d) { return d[xAxisValue]; })
      .rollup(function(v) { return d3.max(v, function(d) { return d[yAxisValue]; }); })
      .entries(data)
  }
  if(yAxisAgg == "Lowest"){
    return d3.nest()
      .key(function(d) { return d[xAxisValue]; })
      .rollup(function(v) { return d3.min(v, function(d) { return d[yAxisValue]; }); })
      .entries(data)
  }
  if(yAxisAgg == "Sum"){
    return d3.nest()
      .key(function(d) { return d[xAxisValue]; })
      .rollup(function(v) { return d3.sum(v, function(d) { return d[yAxisValue]; }); })
      .entries(data)
  }
}

// When the axes are altered, we need to re-group the data depending on the variables set
axesSettings.forEach(setting => {
  setting.onchange = function() {
    let xAxisValue = xAxisSelect.options[xAxisSelect.selectedIndex].value;
    let yAxisValue = yAxisSelect.options[yAxisSelect.selectedIndex].value;
    // If the chosen y variable is equal to 'Amount' then we don't want to give the user the option to perform data aggregations
    if(yAxisValue != 'Amount'){
      aggregate.classList.remove('hidden')
      aggregate.classList.add('visible')
    } else{
      aggregate.classList.remove('visible')
      aggregate.classList.add('hidden')
    }
    // A function that carries ou the grouping, based on the chosen settings
    let groupedData = groupData(xAxisValue, yAxisValue);
    // remove the 'Choose an x-axis variable to get started' if it is present
    emptyGraph.classList.remove("visible");
    emptyGraph.classList.add("hidden");
    // re-draw the graph with the chosen variables
    render(data, groupedData);
  };
})


// Set graph dimensions
const width = 1000;
const height = 640;
// Create SVG ready for graph
const svg = d3.select('#graph').append("svg").attr("width", width).attr("height", height)

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
  graph.remove()
  // Remove old axes (if they exist)
  d3.selectAll('.axis').remove();
  // Remove old axes labels (if they exist)
  d3.selectAll('.label').remove();

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
  graph = svg.append('g')
  .attr("transform", `translate(${margin.left}, ${margin.top})`)

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


  // Draw bars for the bar chart
  graph.selectAll('rect').data(groupedData)
    .enter().append('rect')
      .attr('height', d => gHeight - yScale(yValues(d)))
      .attr('width', xScale.bandwidth()) // band width is width of a single bar
      .attr('x', d => xScale(xValues(d)))
      .attr('y', d=>  yScale(yValues(d)))
}
