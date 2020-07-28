const variableSelect = document.querySelector(".x-axis-value")
const againstSelect = document.querySelector(".y-axis-value")
const againstSection = document.querySelector(".y-axis-details")
const againstAggDOM = document.querySelector(".y-axis-aggregation")
const aggregate = document.querySelector(".aggregate")
const emptyGraph = document.querySelector(".empty-graph")
const exportButton = document.querySelector(".export")

// Get the DOM elements for all of the axes, so that we can add event listeners for when they are changed
const axesSettings = document.querySelectorAll(".axis-setting")

// Get the graph data
const data = graphData["chart_data"]



// DATA GROUPING FUNCTION. CALLED WHEN AN AXIS SETTING CHANGES
function groupData(variableValue, againstValue){
  // We can create a 'nested' D3 object, with the key as the chosen x-axis variable
  let nestedData = d3.nest().key(function(d) { return d[variableValue]; })

  // If the y axis is just to count the values, we can group and perform a roll up on the calculation of the length
  if(againstValue == "Amount"){
    return nestedData
    .rollup(function(v) { return v.length; })
    .entries(data)
  }
  // Else, we need to see which y-axis aggregation was chosen
  let aggainstAgg = againstAggDOM.options[againstAggDOM.selectedIndex].value;
  if(aggainstAgg == "Average"){
    return nestedData
      .rollup(function(v) { return d3.mean(v, function(d) { return d[againstValue]; }); })
      .entries(data)
  }
  if(aggainstAgg == "Highest"){
    return nestedData
      .rollup(function(v) { return d3.max(v, function(d) { return d[againstValue]; }); })
      .entries(data)
  }
  if(aggainstAgg == "Lowest"){
    return nestedData
      .rollup(function(v) { return d3.min(v, function(d) { return d[againstValue]; }); })
      .entries(data)
  }
  if(aggainstAgg == "Sum"){
    return nestedData
      .rollup(function(v) { return d3.sum(v, function(d) { return d[againstValue]; }); })
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
    let variableValue = variableSelect.options[variableSelect.selectedIndex].value;
    let againstValue = againstSelect.options[againstSelect.selectedIndex].value;

    // Hide the overlay
    emptyGraph.classList.remove("visible");
    emptyGraph.classList.add("hidden");

    // Remove the ' -- select an option -- ' option
    variableSelect.firstChild.hidden = true;
    // Reveal the y-axis variable for the user to select
    againstSection.classList.remove('hidden-axis')


    // If the chosen y variable is equal to 'Amount' then we don't want to give the user the option to perform data aggregations
    if(againstValue != 'Amount'){
      aggregate.classList.remove('hidden-axis')
      aggregate.classList.add('visible')
    } else{
      aggregate.classList.remove('visible')
      aggregate.classList.add('hidden-axis')
    }
    // A function that carries ou the grouping, based on the chosen settings
    let groupedData = groupData(variableValue, againstValue);

    // re-draw the graph with the chosen variables
    render(groupedData);
}



// Set graph dimensions
var width = document.getElementById('graph').clientWidth;
var height = document.getElementById('graph').clientHeight;



window.onresize = function(){
  width = document.getElementById('graph').clientWidth;
  height = document.getElementById('graph').clientHeight;
  svg.attr('width', width).attr('height', height);
}


const svg = d3.select('#graph').append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", "0 0 " + width + " " + height)
        .attr("preserveAspectRatio", "none")

// Add a 'graph' group to the svg
const graph = svg.append("g")
    .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

// Add 'labels' group to the graph
graph.append("g")
	.attr("class", "labels")


// Define margins around graph for labels
const margin = { top: 20, right: 20, bottom: 20, left: 20 };
// Define the graph width and height to account for margin
const gWidth = width - margin.left - margin.right;
const gHeight = height - margin.top - margin.bottom;

// Define the radius of the pie_chart (half the graph)
const radius = Math.min(gWidth, gHeight) / 2

// Define the 'arc' (i.e. the curve/radius of the pie)
var arc = d3.arc()
	.outerRadius(radius * 0.8)
	.innerRadius(radius * 0.5);

// The 'labels' will be on a circle with a greater radius than the pie (i.e. just outside)
var labelArc = d3.arc()
	.innerRadius(radius)
	.outerRadius(radius);

// Define size for the legend
var legendRectSize = 18;
var legendSpacing = 4;



const render = (groupedData) => {
  let variableValue = variableSelect.options[variableSelect.selectedIndex].value;
  let againstValue = againstSelect.options[againstSelect.selectedIndex].value;
  let aggainstAgg = againstAggDOM.options[againstAggDOM.selectedIndex].value;

  // Specify the values and keys to be used by the graph
  const keys = d => d.data.data.key;
  const values = d => d.value;


  // set the colour scale, using D3 spectral scheme
  var colour = d3.scaleOrdinal(d3.schemeSet3)
    .domain(groupedData)


  // Compute the position of each group on the pie:
  var pie = d3.pie()
    .value(values)
    .sort(null);

  var pieData = pie(groupedData)

  // Add percentages to pieData
  var total = d3.sum(pieData, values);
  const percentage = d => Math.round((d.value / total) * 100) + "%";
  const combined = function(d){
    let value = d.value
    let percentage = Math.round((d.value / total) * 100) + "%";
    return `${value} (${percentage})`
  }

  // map to data
  var segments = graph.selectAll("path")
    .data(pieData)

  // Need to first initialise each segment
  var initSegment = segments
    .enter()
    .append('path')

  // Then add the tooltip on hover affect
  initSegment.on("mouseenter", function(d){
    d3.select(this)
    .transition()
    .duration(100)
    .style('opacity', '50%')

    var tooltip = d3.select(".graph-tooltip")
    .style("left", d3.event.pageX + 20 + "px")
    .style("top", d3.event.pageY + "px")
    .style("opacity", 1)
    // .classed("tooltip-hidden", false)
    .select(".tooltip-value")
    .text(d.data.key + ": " + d.value)
  })

    .on('mouseout', function() {
      d3.select(this)
      .style('opacity', '1')

      d3.select(".graph-tooltip")
      .style("opacity", 0)
    })


    // Finally merge the segments
    initSegment.merge(segments)
    .transition()
    .duration(750)
    // Custom function for transitioning, needed for pie charts due to the 'sweep-flag' and 'large-arc-flag'
    // See stackoverflow here   https://stackoverflow.com/questions/21285385/d3-pie-chart-arc-is-invisible-in-transition-to-180
    .attrTween("d", function(d) {
      let transition = d3.interpolate(this.angle, d);
      this.angle = transition(0);
      return function(t) {
        return arc(transition(t));
      };
		})
    .attr('fill', function(d){ return(colour(d.data.key)) })
    .attr("stroke", "white")
    .style("stroke-width", "4px")
    .style("opacity", 1)


  // remove the groups that are not present anymore
  segments
    .exit()
    .remove()


  var text = graph.select(".labels").selectAll("text")
	.data(pie(pieData));

	text.enter()
		.append("text")
    .style("font-size", "0.8rem")
    .merge(text)
    .transition()
    .duration(750)
		.text(percentage)
    .attr("transform", function(d) {return "translate(" + labelArc.centroid(d) + ")";  })
    .style("text-anchor", "middle")


	text.exit()
		.remove();

  // A BIT HACKY AT THE MOMENT. THE FIRST ELEMENT I COLOUR.DOMAIN() IS AN UNWANTED OBJECT SO IT IS REMOVED
  // REVIEW THIS TO SEE IF BETTER WAY
  var legendData = colour.domain().slice(1)

  // Remove the legend and title before redrawing it
  svg.selectAll(".legend").remove()
  svg.selectAll(".legend-title").remove()

  var legend = graph.selectAll("#graph")
  .data(legendData)
  .enter()
  .append('g')
     .attr('class', 'legend')
  .attr('transform', function(d, i) {
      let height = legendRectSize + legendSpacing;
      // The vertical position is distance from the center
      // I also add 1 x 'height' onto the value to make space for legend title
      let vert = height + (i * height - (gHeight/2));
      return 'translate(' + (-gWidth/2) + ',' + vert + ')';
  });

  legend.append('rect')
      .attr('width', legendRectSize)
      .attr('height', legendRectSize)
      .style('fill', colour)
      .style('stroke', colour)


  legend.append('text')
      .attr('x', legendRectSize + legendSpacing)
      .attr('y', legendRectSize - legendSpacing)
      .style("font-size", "1rem")
      .text(function(d) {return d });

  // And now add the legend title
  let legendTitle

  if(againstValue == 'Amount'){
    legendTitle = variableValue
  } else{
    legendTitle = `${aggainstAgg} ${againstValue} of ${variableValue}`
  }

  graph.append("text")
        .attr("class", "legend-title")
        .attr("x", -gWidth / 2)
        .attr("y", -gHeight / 2)
        .attr("text-anchor", "left")
        .style("font-size", "1rem")
        .style("text-decoration", "underline")
        .text(legendTitle);



}

let variableValue = variableSelect.options[variableSelect.selectedIndex].value;
if(variableValue != ''){
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
