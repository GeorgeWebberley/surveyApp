let data = []
let headers = []

let container = document.getElementById('handsontable');
let hot = new Handsontable(container, {
  data: [],
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
  $.post( "/edit", {
    table: string,
    surveyId: data["surveyId"]
  });
  // let xhr = new XMLHttpRequest();
  // xhr.open("POST", url, true);
  // xhr.setRequestHeader('Content-Type', 'application/json');
  // xhr.send(JSON.stringify({
  //     value: string
  // }));
})


const exportPlugin = hot.getPlugin('exportFile');
