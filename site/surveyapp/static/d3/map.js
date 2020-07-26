const settings = document.querySelectorAll(".axis-setting")
const variable = document.querySelector(".x-axis-value")
const scope = document.querySelector(".scope")
const exportButton = document.querySelector(".export")


// Get the iso code for all the countries and pair them with country names for later access
let iso = {}
const countries = Datamap.prototype.worldTopo.objects.world.geometries;
for (var i = 0, j = countries.length; i < j; i++) {
  iso[countries[i].properties.name] = countries[i].id
}


// Get the graph data
const data = graphData["chart_data"]


// Set the projections for various parts of the world
const africa = function(element) {
    var projection = d3.geo.equirectangular()
      .center([19, 0])
      .rotate([4.4, 0])
      .scale(400)
      .translate([element.offsetWidth / 2, element.offsetHeight / 2]);
    var path = d3.geo.path()
      .projection(projection);

    return {path: path, projection: projection};
}
const europe = function(element) {
    var projection = d3.geo.mercator()
      .center([20, 56])
      .rotate([0, 0])
      .scale(490)
      .translate([element.offsetWidth / 2, element.offsetHeight / 2]);
    var path = d3.geo.path()
      .projection(projection);

    return {path: path, projection: projection};
}






function groupData(chosenVariable){
  // Delete old graph (if present)
  $("#graph").parent().append( "<div id='graph' class='h-100 position-relative'/>");
  $("#graph").remove();
  // Get the grouped data
  let groupedData = group(chosenVariable);
  // Get the most common country value so that we can base our colour scale of that
  let max = 0
  for(let i = 0; i < groupedData.length; i++){
    if(groupedData[i].values > max)[
      max = groupedData[i].values
    ]
  }
  // we now increase the maximum until it is directly divisble by 5 (as we have 5 bins)
  max++;
  while(max % 5 != 0){
    max++;
  }

  // Set our colour scale based on the max
  let colourScale = getColourScale(max)


  let result = {};
  // Loop through our data, setting the colour for each
  groupedData.forEach(country => {
    let colour = 'defaultFill'
    if(country.values < max) colour = `- Between ${(max/5)*4} and ${max}`
    if(country.values < (max / 5)*4) colour = `- Between ${(max/5)*3} and ${(max/5)*4}`
    if(country.values < (max / 5)*3) colour = `- Between ${(max/5)*2} and ${(max/5)*3}`
    if(country.values < (max / 5)*2) colour = `- Between ${max/5} and ${(max/5)*2}`
    if(country.values < max / 5) colour = `- Less than ${max/5}`
    let fill = {
      "fillKey": colour
    }
    // Get the country code (ISO 3 letter code)
    let countryCode = iso[country.key]
    result[countryCode] = fill
  })

  // Get the projection/scope of the graph
  let projection = getProjection()

  // Draw our map with our colourscale and data
  var map = new Datamap({
      element: document.getElementById('graph'),
      projection: 'mercator',
      setProjection: projection,
      fills: colourScale,
      data: result
  });
  map.legend();
}

function getColourScale(max){
  // Save as string so that we can insert in values
  let colourScale = `{
      "- Less than ${max/5}": "#c7d2f2",
      "- Between ${max/5} and ${(max/5)*2}": "#acc1fc",
      "- Between ${(max/5)*2} and ${(max/5)*3}": "#6f8ee3",
      "- Between ${(max/5)*3} and ${(max/5)*4}": "#3258bf",
      "- Between ${(max/5)*4} and ${max}": "#012178",
      "defaultFill": "#e3e3e3"
    }`
  // Convert to JSON object to be used in the map
  return JSON.parse(colourScale)
}

function getProjection(){
  if(scope.options[scope.selectedIndex].value == "Europe"){
    return europe
  }else if(scope.options[scope.selectedIndex].value == "Africa"){
    return africa
  }else{
    return null
  }
}


function group(chosenVariable){
  // We can create a 'nested' D3 object, with the key as the chosen x-axis variable
  let nestedData = d3.nest().key(function(d) { return d[chosenVariable]; })
  return nestedData
    .rollup(function(v) { return v.length; })
    .entries(data)
}

// Add event listener
settings.forEach(setting => {
  setting.onchange = function(){
    groupData(variable.options[variable.selectedIndex].value);
  }
})


if(variable.options[variable.selectedIndex].value != ''){
  groupData(variable.options[variable.selectedIndex].value)
}




exportButton.addEventListener("click", () => {
  saveSvgAsPng(document.getElementsByTagName("svg")[0], "plot.png", {scale: 2, backgroundColor: "#FFFFFF"});
})



// When the form is submitted, we want to get a jpg image of the svg
$('form').submit(function (e) {
  let svg = d3.select('#graph')
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
    console.log("hello");
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
    console.log(imgData);
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
