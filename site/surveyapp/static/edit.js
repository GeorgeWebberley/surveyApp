const button = document.querySelector(".save")
const info = document.querySelector(".table-guide")
const container = document.querySelector(".handsontable-container")
const table = document.getElementById('handsontable');
const addVariable = document.querySelector(".add-variable")
const inputOverlay = document.querySelector(".input-overlay")


let values = data["values"]
let headers = data["headers"]
let hot;


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
  console.log(headers);
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


// Post table back to server when user clicks on 'save'
button.addEventListener('click', () => {
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
  $.post( "/edit", {
    table: string,
    surveyId: data["surveyId"]
  });
  // Change spare rows back to 1 if user wants to continue editing
  hot.updateSettings({
    minSpareRows: 1
  })
  // alert("Your changes have been saved")
  info.innerHTML = "Up to date"
  info.style.color = "green"
})

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
