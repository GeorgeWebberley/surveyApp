const xAxisSelect = document.querySelector(".x-axis-value")
const xAxisValue = xAxisSelect.options[xAxisSelect.selectedIndex].value;

const data = graphData["chart_data"]
var column = xAxisValue;

var groupedData = d3.nest()
  .key(function(d) { return d[column]; })
  .rollup(function(v) { return v.length; })
  .entries(data);

xAxisSelect.onchange = function (column, xAxisValue, columnCount) {
  xAxisValue = xAxisSelect.options[xAxisSelect.selectedIndex].value;
  column = xAxisValue;
  groupedData = d3.nest()
    .key(function(d) { return d[column]; })
    .rollup(function(v) { return v.length; })
    .entries(data);
  render(data, column, groupedData);
}

const width = 1000;
const height = 640;
const svg = d3.select('#graph').append("svg")
  .attr("width", width)
  .attr("height", height)



const margin = { top: 20, right: 20, bottom: 100, left: 100 };
const gWidth = width - margin.left - margin.right;
const gHeight = height - margin.top - margin.bottom;


var graph = svg.append('g')
.attr("transform", `translate(${margin.left}, ${margin.top})`)



const render = (data, column, groupedData) => {
  const xValues = d => d.key;
  const yValues = d => d.value;

  graph.remove()

  const xScale = d3.scaleBand()
    .domain(groupedData.map(xValues))
    .range([0, gWidth])
    .paddingInner(0.1)


  const yScale = d3.scaleLinear()
    .domain([0, d3.max(groupedData, yValues)])
    .range([gHeight, 0])


  graph = svg.append('g')
  .attr("transform", `translate(${margin.left}, ${margin.top})`)


  var hasAxis = graph.select('.axis')["_groups"][0][0];
  if(hasAxis != undefined){
    d3.selectAll('.axis').remove();
  }
  d3.selectAll('.axis').remove();
  graph.append('g').attr("class", "axis").call(d3.axisLeft(yScale))
  graph.append('g').attr("class", "axis").call(d3.axisBottom(xScale))
    .attr("transform", `translate(0, ${gHeight})`)

  graph.selectAll('rect').data(groupedData)
    .enter().append('rect')
      .attr('height', d => gHeight - yScale(yValues(d)))
      .attr('width', xScale.bandwidth()) // band width is width of a single bar
      .attr('x', d => xScale(xValues(d)))
      .attr('y', d=>  yScale(yValues(d)))

}

render(data, column, groupedData);
