// ------VARIABLE DECLARATIONS------
const settings = document.querySelectorAll(".axis-setting")
const variable = document.querySelector(".x-axis-value")
const scope = document.querySelector(".scope")
const exportButton = document.querySelector(".export")
// Get the graph data
const data = graphData["chart_data"]

// Width/height needed for saving image to dashboard
const width = document.getElementById('graph').clientWidth;
const height = document.getElementById('graph').clientHeight;

// Get the iso code for all the countries and pair them with country names for later access
let iso = {}
const countries = Datamap.prototype.worldTopo.objects.world.geometries;
for (let i = 0, j = countries.length; i < j; i++) {
  iso[countries[i].properties.name] = countries[i].id
}

// Set the projections for various parts of the world
// REFACTOR THIS CODE????/
const africa = function(element) {
    let projection = d3.geo.equirectangular()
      .center([19, 0])
      .rotate([4.4, 0])
      .scale(400)
      .translate([element.offsetWidth / 2, element.offsetHeight / 2]);
    let path = d3.geo.path()
      .projection(projection);
    return {path: path, projection: projection};
}

const europe = function(element) {
    let projection = d3.geo.mercator()
      .center([20, 56])
      .rotate([0, 0])
      .scale(490)
      .translate([element.offsetWidth / 2, element.offsetHeight / 2]);
    let path = d3.geo.path()
      .projection(projection);
    return {path: path, projection: projection};
}

const southAmerica = function(element) {
    let projection = d3.geo.mercator()
      .center([-65, -24])
      .rotate([0, 0])
      .scale(350)
      .translate([element.offsetWidth / 2, element.offsetHeight / 2]);
    let path = d3.geo.path()
      .projection(projection);
    return {path: path, projection: projection};
}

const northAmerica = function(element) {
    let projection = d3.geo.mercator()
      .center([-90, 45])
      .rotate([0, 0])
      .scale(340)
      .translate([element.offsetWidth / 2, element.offsetHeight / 2]);
    let path = d3.geo.path()
      .projection(projection);
    return {path: path, projection: projection};
}

const asia = function(element) {
    let projection = d3.geo.mercator()
      .center([100, 35])
      .rotate([0, 0])
      .scale(340)
      .translate([element.offsetWidth / 2, element.offsetHeight / 2]);
    let path = d3.geo.path()
      .projection(projection);
    return {path: path, projection: projection};
}

const oceania = function(element) {
    let projection = d3.geo.mercator()
      .center([130, -20])
      .rotate([0, 0])
      .scale(400)
      .translate([element.offsetWidth / 2, element.offsetHeight / 2]);
    let path = d3.geo.path()
      .projection(projection);
    return {path: path, projection: projection};
}

// ------END OF VARIABLE DECLARATIONS------
// ------SET EVENT LISTENERS------
// Add event listener for any axis changes
settings.forEach(setting => {
  setting.onchange = function(){
    render(variable.options[variable.selectedIndex].value);
  }
})

// Runs if variables already set (i.e. if user is choosing to edit rather than create)
if(variable.options[variable.selectedIndex].value != ''){
  render(variable.options[variable.selectedIndex].value)
}

// Export button that allows user to export and download the SVG as a PNG image
exportButton.addEventListener("click", () => {
  let title = document.querySelector(".title").value
  let exportTitle = title == "" ? "plot.png": `${title}.png`
  saveSvgAsPng(document.getElementsByTagName("svg")[0], exportTitle, {scale: 2, backgroundColor: "#FFFFFF"});
})

// ------FUNCTIONS FOR DRAWING THE GRAPH------
function render(chosenVariable){
  // Needed to delete the old graph (if present)
  $("#graph").parent().append( "<div id='graph' class='h-100 position-relative'/>");
  $("#graph").remove();
  // Get the grouped data
  let groupedData = group(chosenVariable);
  // Get the most common country value so that we can base our colour scale of that
  let max = getMax(groupedData)

  // set the legend variables, based on the maximum value. We have 5 in total,
  // so each bin comprises a 5th of the maximum value
  let veryHigh = `- Between ${(max/5)*4} and ${max}`
  let high = `- Between ${(max/5)*3} and ${(max/5)*4 - 1}`
  let medium = `- Between ${(max/5)*2} and ${(max/5)*3 - 1}`
  let veryLow = `- Between ${max/5} and ${(max/5)*2 - 1}`
  let low = `- Less than ${max/5}`

  // Get our colour scale and link it to the values in our legend
  let colourScale = getColourScale(max, veryHigh, high, medium, veryLow, low)

  let result = {};
  // Loop through our data, setting the colour for each
  groupedData.forEach(country => {
    let colour = 'defaultFill'
    if(country.values < max) colour = veryHigh
    if(country.values < (max / 5)*4) colour = high
    if(country.values < (max / 5)*3) colour = medium
    if(country.values < (max / 5)*2) colour = low
    if(country.values < max / 5) colour = veryLow
    let fill = {
      "fillKey": colour,
      "value": country.values
    }
    // Convert the country to 3 letter ISO code (if needed)
    let countryCode = iso[country.key] == undefined ? country.key : iso[country.key]
    result[countryCode] = fill
  })
  // Get the projection and scope of the graph
  // Scope relates to whether it is focused on states of America or countries of the World
  let chosenProjection = getProjection()
  let usa_world = getScope()
  // Draw our map with our colourscale and data
  let map = new Datamap({
      element: document.getElementById('graph'),
      scope: usa_world,
      geographyConfig: {
                // Set the border colour to same colour as the default fill
                highlightBorderColor: '#FC8D59',
                // Customise popup to also display the values/counts if they exist
                popupTemplate: function(geography, data) {
                  if(data == null){
                    return '<div class="hoverinfo"><strong>' + geography.properties.name + '</strong></div>';
                  }
                  return '<div class="hoverinfo"><strong>' + geography.properties.name + ':</strong> ' + data.value +  '</div>';
                }
            },
      projection: 'mercator',
      setProjection: chosenProjection,
      fills: colourScale,
      data: result
  });
  // Add legend to the map
  map.legend();
}

// Groups the data on the chosenVariable/column
function group(chosenVariable){
  // We can create a 'nested' D3 object, with the key as the chosen x-axis variable
  let nestedData = d3.nest().key(function(d) { return d[chosenVariable]; })
  return nestedData
    .rollup(function(v) { return v.length; })
    .entries(data)
}

// Gets the maximum value and then increases it so it is divisible by 5 (for the 5 bins)
function getMax(groupedData){
  let max = 0
  for(let i = 0; i < groupedData.length; i++){
    if(groupedData[i].values > max){
      max = groupedData[i].values
    }
  }
  // we now increase the maximum until it is directly divisble by 5 (as we have 5 bins)
  max++;
  while(max % 5 != 0){
    max++;
  }
  return max
}

// Sets the colour scale of the map
function getColourScale(max, veryHigh, high, medium, veryLow, low){
  // Save as string so that we can insert in javascript variables
  let colourScale = `{
      "${veryLow}": "#DEEDCF",
      "${low}": "#74C67A",
      "${medium}": "#1D9A6C",
      "${high}": "#137177",
      "${veryHigh}": "#0A2F51",
      "defaultFill": "#dae4eb"
    }`
  // Convert to JSON object to be used in the map
  return JSON.parse(colourScale)
}

// Gets the projection of the map, depending on the chosen user input
function getProjection(){
  if(scope.options[scope.selectedIndex].value == "Europe"){
    return europe
  }else if(scope.options[scope.selectedIndex].value == "Africa"){
    return africa
  }else if(scope.options[scope.selectedIndex].value == "Asia"){
    return asia
  }else if(scope.options[scope.selectedIndex].value == "South America"){
    return southAmerica
  }else if(scope.options[scope.selectedIndex].value == "Australia/Oceania"){
    return oceania
  }else if(scope.options[scope.selectedIndex].value == "North America"){
    return northAmerica
  }else{
    return null
  }
}

// Gets the scope (either countries of the world or states of america)
function getScope(){
  if(scope.options[scope.selectedIndex].value == "United States of America"){
    return "usa"
  }else{
    return "world"
  }
}

// Ajax call used to post, as we are also sending the image of the graph (not in form)
$('form').submit(function (e) {
  // prevent default form submission
  e.preventDefault();
  // call function to post form (separate js file)
  postgraph(width, height)
});
