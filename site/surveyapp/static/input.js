const button = document.querySelector(".save")
const info = document.querySelector(".table-guide")
const container = document.querySelector(".handsontable-container")
const table = document.getElementById('handsontable');
const addVariable = document.querySelector(".add-variable")
const inputOverlay = document.querySelector(".input-overlay")


let values = data["values"]
let headers = data["headers"]
let hot;



console.log(values);
console.log(headers);

if(headers.length == 0){
  container.classList.add("hidden")
  addVariable.addEventListener("click", () => {
    firstVariable = prompt("Enter your first column heading")
    if(firstVariable){
      container.classList.remove("hidden")
      inputOverlay.classList.add("hidden")
      headers.push(firstVariable)
      let columns = columnData(headers)
      values=[[]]
      renderTable(values, headers, columns)
    }
  })
} else{
  // Edge case: handsontable needs a 2d array. If values is empty it needs converting
  if (values.length == 0){
    values = [[]]
  }
  inputOverlay.classList.add("hidden")
  let columns = columnData(headers)
  renderTable(values, headers, columns)
}

function columnData(headers){
  columns = []
  headers.forEach(header => {
    columns.push({data: header})
  })
  return columns
}


function renderTable(values, headers){
  hot = new Handsontable(table, {
    data: values,
    minRows: 1,
    minCols: 1,
    rowHeaders: true,
    colHeaders: true,
    minSpareRows: 1,
    allowEmpty: false,
    filters: true,
    colHeaders: headers,
    licenseKey: 'non-commercial-and-evaluation',
    dropdownMenu: {
      items: [
        {
          key:'rename_column',
          name: 'Rename column',
          callback: (key, option) => {
            cellIndex = option[0].end.col
            var newColHeader = prompt('Pick new name');
            if(newColHeader){
              headers[cellIndex] = newColHeader
              hot.render()
            }
          }
        },
        '---------',
        'remove_col',
        '---------',
        'col_left',
        '---------',
        'col_right'
      ]
    },
    afterChange: function (change, source) {
      if (source !== 'loadData') {
        info.innerHTML = "You have unsaved changes"
        info.style.color = "red"
      }
    }
  });
}



$('form').submit(function (e) {
  // Remove the 'spare' row before saving
  hot.updateSettings({
    minSpareRows: 0
  })
  // Remove empty rows (if any)
  let newHot = removeEmptyRows();
  let exportPlugin;
  if(newHot != undefined){
    exportPlugin = newHot.getPlugin('exportFile');
  }else{
    exportPlugin = hot.getPlugin('exportFile');
  }
  const string = exportPlugin.exportAsString('csv', {
    columnHeaders: true,
  });
  postData(string)
  e.preventDefault();
  // Change spare rows back to 1 if user wants to continue editing
  hot.updateSettings({
    minSpareRows: 1
  })
  // alert("Your changes have been saved")
  info.innerHTML = "Up to date"
  info.style.color = "green"
});


function removeEmptyRows(){
  let data = hot.getData()
  let emptyRows = []
  data.forEach((row, i) => {
    if(hot.isEmptyRow(i)){
      emptyRows.push([i, 1])
    }
  })
  newHot = hot.alter("remove_row", emptyRows, 1)
  return newHot
}



function postData(dataString){

  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
          xhr.setRequestHeader("X-CSRFToken", csrf)
      }
    }
  })
  var postData = $('form').serializeArray()
  postData.push({name: "table", value: dataString})
  $.ajax({
      type: "POST",
      url: url,
      data: postData,
      success: function () {
          console.log("Table posted to server")
      }
  });
}
