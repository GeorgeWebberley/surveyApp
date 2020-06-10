

// var margin = {top: 30, right: 50, bottom: 30, left: 50};
// var svgWidth = 600;
// var svgHeight = 270;
// var graphWidth = svgWidth - margin.left - margin.right;
// var graphHeight = svgHeight - margin.top - margin.bottom;
//
// var parseTime = d3.timeParse("%Y-%m-%d");
//
// var x = d3.scaleTime().range([0, graphWidth]);
// var y = d3.scaleLinear().range([graphHeight, 0]);
//
// var xAxis = d3.axisBottom(x).ticks(5);
// var yAxis = d3.axisLeft(y).ticks(5);
//
//
// var highLine = d3.line()
//     .x(function(d) { return x(d.Date); })
//     .y(function(d) { return y(d.High); });
//
// var closeLine = d3.line()
//     .x(function(d) { return x(d.Date); })
//     .y(function(d) { return y(d.Close); });
// var lowLine = d3.line()
//     .x(function(d) { return x(d.Date); })
//     .y(function(d) { return y(d.Low); });
//
//
// var area = d3.area()
//     .x(function(d) { return x(d.Date); })
//     .y0(function(d) { return y(d.Low); })
//     .y1(function(d) { return y(d.High); })
//
// var svg = d3.select("#graph")
//     .append("svg")
//         .attr("width", svgWidth)
//         .attr("height", svgHeight)
//     .append("g")
//         .attr("transform",
//         "translate(" + margin.left + "," + margin.top + ")")

const data = graphData["chart_data"]
const column = graphData["column"]
console.log(data);

const width = 1000;
const height = 640;
const svg = d3.select('#graph').append("svg")
  .attr("width", width)
  .attr("height", height)

const render = data => {
  // defining these values, means we don't limit our functions to this particular data set (just to these 2 values)
  const xValues = d => d[column];
  const yValues = d => d.c;

  const margin = { top: 20, right: 20, bottom: 100, left: 100 };
  const gWidth = width - margin.left - margin.right;
  const gHeight = height - margin.top - margin.bottom;

  // create instance of d3 linear scale
  // linear scales are useful for quantitative attributes (in our case, the populations)
  const xScale = d3.scaleBand()
    // domain is the range of our actual data
    .domain(data.map(xValues))
    // range is the 'screen range' of our actual data
    .range([0, gWidth])
    .paddingInner(0.1)

  // We create a yAxis (on the left) and pass it the scale we want it to use


  const yScale = d3.scaleLinear()
    // band scales are useful for ordinal attributes (in our case, the countries)
    // each row is set to one country
    .domain([0, d3.max(data, yValues)])
    .range([gHeight, 0])



  // Make a group section (which is affectively the graph area, not the axes values/titles etc.)
  // We therefore need to shift the group section, so it is not at the top left but instead in the center (with the surrounding margins)
  const g = svg.append('g')
  .attr("transform", `translate(${margin.left}, ${margin.top})`)

  // make a new 'group' element inside our existing 'group element' set this to the yAxis
  // We create a yAxis (on the left) and pass it the scale we want it to use
  // yAxis(g.append('g'));
  g.append('g').call(d3.axisLeft(yScale))

  g.append('g').call(d3.axisBottom(xScale))
    // Now we translate the x-axis so it is at the bottom, not at the top
    .attr("transform", `translate(0, ${gHeight})`)


  g.selectAll('rect').data(data)
    .enter().append('rect')
      .attr('height', d => gHeight - yScale(yValues(d)))
      .attr('width', xScale.bandwidth()) // band width is width of a single bar
      .attr('x', d => xScale(xValues(d)))
      .attr('y', d=>  yScale(yValues(d)))
}

render(data);
