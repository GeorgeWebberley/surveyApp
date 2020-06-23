var headers = []

if(data["dataObj"][0]){
  headers = Object.keys(data["dataObj"][0]);
}

var container = document.getElementById('handsontable');
var hot = new Handsontable(container, {
  data: data["dataObj"],
  rowHeaders: true,
  colHeaders: true,
  filters: true,
  dropdownMenu: true,
  colHeaders: headers,
  licenseKey: 'non-commercial-and-evaluation'
});

const button = document.querySelector(".save")

button.addEventListener('click', function(){
  const exportPlugin = hot.getPlugin('exportFile');
  const string = exportPlugin.exportAsString('csv', {
    columnHeaders: true,
  });
  $.post( "/input", {
    table: string,
    surveyId: data["surveyId"]
  });
  // var xhr = new XMLHttpRequest();
  // xhr.open("POST", url, true);
  // xhr.setRequestHeader('Content-Type', 'application/json');
  // xhr.send(JSON.stringify({
  //     value: string
  // }));
})


const exportPlugin = hot.getPlugin('exportFile');
