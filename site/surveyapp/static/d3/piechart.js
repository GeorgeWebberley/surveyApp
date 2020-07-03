const xAxisSelect = document.querySelector(".x-axis-value")
const yAxisSelect = document.querySelector(".y-axis-value")
const yAxisDetails = document.querySelector(".y-axis-details")
const yAxisAggDom = document.querySelector(".y-axis-aggregation")
const aggregate = document.querySelector(".aggregate")
const emptyGraph = document.querySelector(".empty-graph")
const exportButton = document.querySelector(".export")

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

    // Hide the overlay
    emptyGraph.classList.remove("visible");
    emptyGraph.classList.add("hidden");

    // Remove the ' -- select an option -- ' option
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


// Create SVG ready for graph
// const svg = d3.select('#graph').append("svg").attr("width", "100%").attr("height", "100%")


const svg = d3.select('#graph').append("svg")
        .attr("width", width)
        .attr("height", height).attr("viewBox", "0 0 " + width + " " + height)
        .attr("preserveAspectRatio", "none")
      .append("g")
        .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");


svg.append("g")
	.attr("class", "labels")

// Define margins around graph for axis and labels
const margin = { top: 20, right: 20, bottom: 20, left: 20 };
// Define the graph width and height to account for axes
const gWidth = width - margin.left - margin.right;
const gHeight = height - margin.top - margin.bottom;

// Define the radius of the pie_chart (half the graph)
const radius = Math.min(gWidth, gHeight) / 2

// Define the 'arc' (i.e. the curve/radius of the pie)
var arc = d3.arc()
	.outerRadius(radius * 0.8)
	.innerRadius(radius * 0.5);

var labelArc = d3.arc()
	.innerRadius(radius)
	.outerRadius(radius);


const render = (groupedData) => {
  let xAxisValue = xAxisSelect.options[xAxisSelect.selectedIndex].value;
  let yAxisValue = yAxisSelect.options[yAxisSelect.selectedIndex].value;
  let yAxisAgg = yAxisAggDom.options[yAxisAggDom.selectedIndex].value;

  // Specify the values and keys to be used by the graph
  const keys = d => d.data.data.key;
  const values = d => d.value;



  // set the colour scale, using D3 colour scheme 'Tableau10'
  var colour = d3.scaleOrdinal()
    .domain(groupedData)
    .range(d3.schemeTableau10);

    // Compute the position of each group on the pie:
  var pie = d3.pie()
    .value(values)
    .sort(null);

  var pieData = pie(groupedData)



  // Add percentages to pieData
  var total = d3.sum(pieData, values);
  const percentage = d => Math.round((d.value / total) * 100) + "%";
  const combined = function(d){
    let key = d.data.data.key
    let value = d.value
    let percentage = Math.round((d.value / total) * 100) + "%";
    return `${key}: ${value} (${percentage})`
  }

  // map to data
  var segments = svg.selectAll("path")
    .data(pieData)

  segments
    .enter()
    .append('path')
    .merge(segments)
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

  // remove the group that is not present anymore
  segments
    .exit()
    .remove()

  var text = svg.select(".labels").selectAll("text")
	.data(pie(pieData));


  function midAngle(d){
  return d.startAngle + (d.endAngle - d.startAngle)/2;
  }


	text.enter()
		.append("text")
    .style("font-size", "0.8rem")
    .merge(text)
    .transition()
    .duration(750)
		.text(combined)
    .attr("transform", function(d) {return "translate(" + labelArc.centroid(d) + ")";  })
    .style("text-anchor", "middle")


	text.exit()
		.remove();




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
  var doctype = '<?xml version="1.0" standalone="no"?>'
               + '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">';
  // serialise the graph svg
  var source = (new XMLSerializer()).serializeToString(svg.node());
  // convert to Blob
  var blob = new Blob([ doctype + source], { type: 'image/svg+xml' });
  var imageURL = window.URL.createObjectURL(blob);
  var img = new Image();


  img.onload = async function(){
    var canvas = d3.select('body').append('canvas').node();
    canvas.width = width;
    canvas.height = height;

    var ctx = canvas.getContext('2d');

    // draw image on canvas
    ctx.drawImage(img, 0, 0, width, height);

    var glContextAttributes = { preserveDrawingBuffer: true };
    var gl = canvas.getContext("experimental-webgl", glContextAttributes);


    var imgData = await canvas.toDataURL("image/png");
    canvas.remove();

    // ajax call to send canvas(base64) url to server.
    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrf)
        }
      }
    })

    var postData = $('form').serializeArray()
    postData.push({name: "image", value: imgData})
    $.ajax({
        type: "POST",
        url: url,
        data: postData,
        success: function () {
          window.location.href = redirectUrl;
          // console.log("success");
        }
    });
  }

  img.src =  imageURL;
  // window.open().document.write('<img src="' + img.src + '"/>');




});
