const button = document.querySelector(".save")
const infoRow = document.querySelector(".info-row")
const info = document.querySelector(".table-guide")
const container = document.querySelector(".handsontable-container")
const table = document.getElementById('handsontable');
const addVariable = document.querySelector(".add-variable")
const inputOverlay = document.querySelector(".input-overlay")
const addColumn = document.querySelector(".add-column")

const newVariable = document.querySelector(".heading")



let values = data["values"]
let headers = data["headers"]
let hot;


// If the table has not yet been created then we want to hide the DOM elements
if(headers.length == 0){
  container.classList.add("hidden")
  infoRow.classList.add("hidden")
} else{
  // Edge case: handsontable needs a 2d array. If 'values' is empty it needs converting
  // if (values.length == 0){
  //   values = [[]]
  // }
  inputOverlay.classList.add("hidden")
  let columns = columnData(headers)
  renderTable(values, headers, columns)
}

addColumn.addEventListener('click', function () {
  triggerModal()
});


function triggerModal(){
  // Allow user to submit a column field simply by pressing enter
  $(document).unbind("keyup").keyup(function(e){
      // Get the key code
      let code = e.which;
      // If it is equal to 13 then click the confirm button
      if(code==13)
      {
          $("#confirm").click();
      }
  });

  if(newVariable.value == ""){
    // If the user tries to enter in an empty string, modal remains open with warning class
    newVariable.classList.add("is-invalid")
  }else{
    // Remove the warning box class if the user has previously tried to enter an empty string
    newVariable.classList.remove("is-invalid")
    // Add new column heading
    headers.push(newVariable.value)
    // Close the modal and reset the input box to be empty
    $('#new-column-modal').modal('toggle');
    newVariable.value = ""
    // If the table does not yet exist, we need to remove the overlay and make the table visible
    if(hot == undefined){
      container.classList.remove("hidden")
      infoRow.classList.remove("hidden")
      inputOverlay.classList.add("hidden")
      // Populate column headers with provided headers
      let columns = columnData(headers)
      // Intialise empty 2d array to represent the cells in the table
      values=[[]]
      // Render the table
      renderTable(values, headers, columns)
      // If table already exists we can simply update it
    }else{
      hot.alter('insert_col', headers.length, 1)
      // Necessary, since 'insert_col' will add an an 'undefined' header to the header list
      // (which is not needed since we have already added the header with the specified name)
      headers.pop()
    }
  }
}



function columnData(headers){
  let columns = []
  headers.forEach(header => {
    columns.push({data: header})
  })
  return columns
}


function renderTable(values, headers){
  hot = new Handsontable(table, {
    data: values,
    // 23 rows will fill up the view for the user
    minRows: 23,
    minCols: 1,
    stretchH: 'all',
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



// function triggerModal(){
//   if(newVariable.value == ""){
//     newVariable.classList.add("is-invalid")
//   }else{
//     headers.push(newVariable.value)
//     newVariable.value = ""
//     hot.alter('insert_col', headers.length, 1)
//     headers.pop()
//     $('#new-column-modal').modal('toggle');
//   }
// }

// Prevent form auto submitting when a user presses Enter
$(document).on("keydown", "form", function(event) {
    return event.key != "Enter";
});



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
  let newHot = hot.alter("remove_row", emptyRows, 1)
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
