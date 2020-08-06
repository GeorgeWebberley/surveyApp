const button = document.querySelector(".save")
const infoRow = document.querySelector(".info-row")
const info = document.querySelector(".table-guide")
const container = document.querySelector(".handsontable-container")
const table = document.getElementById('handsontable');
const addVariable = document.querySelector(".add-variable")
const inputOverlay = document.querySelector(".input-overlay")
const addColumn = document.querySelector(".add-column")

const newVariable = document.querySelector(".heading")

const proceed = document.querySelector(".proceed")



let values = data["values"]
let headers = data["headers"]
let hot;
let savedChanges = True;


// If the table has not yet been created then we want to hide the DOM elements
if(headers.length == 0){
  container.classList.add("invisible")
  infoRow.classList.add("invisible")
} else{
  // Edge case: handsontable needs a 2d array. If 'values' is empty it needs converting
  if (values.length == 0){
    values = [[]]
  }
  inputOverlay.classList.add("invisible")
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
      container.classList.remove("invisible")
      infoRow.classList.remove("invisible")
      inputOverlay.classList.add("invisible")
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
    columnSorting: true,
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
        savedChanges = False;
      }
    }
  });
}


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




// Put all of our standalone jquery function inside a document ready check
$(document).ready(function(){
  // A function that prompts the user to save if they have not done so before moving to home
  $('#proceed').click(function(event) {
      if(!savedChanges){
        event.preventDefault();
        $('#save-changes-modal').modal('toggle');
      }
  });


  // Prevent form auto submitting when a user presses Enter
  $(document).on("keydown", "form", function(event) {
      return event.key != "Enter";
  });


  // Function responsible for form submission
  $('form').submit(function (e) {
    // Remove any extra rows before saving (so they are not also submitted)
    hot.updateSettings({
      minSpareRows: 0,
      minRows:0
    })
    // Remove empty rows (if any)
    let newHot = removeEmptyRows();

    // Get the export plugin on the newHot (if it exists) else on the old hot
    let exportPlugin = newHot != undefined ? newHot.getPlugin('exportFile') : hot.getPlugin('exportFile')

    const string = exportPlugin.exportAsString('csv', {
      columnHeaders: true,
    });
    // Post the data has a string to the server
    postData(string)
    // Prevent default form submission
    e.preventDefault();

    // Change spare rows back to 1 and min back to 23 if user wants to continue editing
    hot.updateSettings({
      minSpareRows: 1,
      minRows:23
    })
    // Update the html to display that the changes have been submitted
    info.innerHTML = "Up to date"
    info.style.color = "green"
    savedChanges = True;
  });
});


// Post the table as a string to the server (with the title)
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
      success: function (data) {
        // The server returns the id of the survey (if it is new) so we can update our URL
        url = Flask.url_for("surveys.input", {"survey_id": data})
      }
  });
}
