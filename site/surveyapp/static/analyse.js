// The DOM elements representing the different sections
const statisticalTests = document.querySelector(".statistical-tests")
const independentVariables = document.querySelector(".independent-variables")
const dependentVariables = document.querySelector(".dependent-variables")
const continueButton = document.querySelector(".analyse-continue")

// The DOM elements representing the select fields
const surveyList = document.querySelector(".analyse-survey")
const independentVariableList = document.querySelector(".independent-variable")
const dependentVariableList = document.querySelector(".dependent-variable")
const statisticalTestList = document.querySelector(".statistical-test")

function setEventListeners() {

  surveyList.onchange = function() {
    statisticalTests.classList.remove("hidden-axis");
    surveyList.firstChild.hidden = true;
    survey = surveyList.value
    fetch("/analyse/" + survey)
      .then(response => response.json())
      .then(data => {
        let independentSelect = "<option value=''> -- select an option -- </option>";
        data.independentVariables.forEach(variable => {
          independentSelect += "<option value='" + variable + "'>" + variable + "</option>";
        })
        let dependentSelect = "<option value=''> -- select an option -- </option>";
        data.dependentVariables.forEach(variable => {
          dependentSelect += "<option value='" + variable + "'>" + variable + "</option>";
        })
        independentVariableList.innerHTML = independentSelect;
        dependentVariableList.innerHTML = dependentSelect;
      })
  }

  statisticalTestList.onchange = function() {
    independentVariables.classList.remove("hidden-axis");
    statisticalTestList.firstChild.hidden = true;
  }

  onChangeListener(independentVariableList, dependentVariableList, dependentVariables);
  onChangeListener(dependentVariableList, independentVariableList, continueButton);

}

// This function removes the chosen variable from the opposite select box, preventing the same variable being picked twice
function onChangeListener(currentSelect, otherSelect, nextSection){
  currentSelect.onchange = function() {
    nextSection.classList.remove("hidden-axis");
    currentSelect.firstChild.hidden = true;
    variable = currentSelect.value
    for (var i=0; i < otherSelect.length; i++) {
        if (otherSelect.options[i].value == variable){
          otherSelect.options[i].hidden = true;
        } else {
          otherSelect.options[i].hidden = false;
        }
    }
    otherSelect.firstChild.hidden = true;
  }
}


setEventListeners()
