// The DOM elements representing the different sections
const statisticalTests = document.querySelector(".statistical-tests")
const independentVariables = document.querySelector(".independent-variables")
const dependentVariables = document.querySelector(".dependent-variables")
const continueButton = document.querySelector(".analyse-continue")

// The DOM elements representing the select fields
const independentVariableList = document.querySelector(".independent-variable")
const dependentVariableList = document.querySelector(".dependent-variable")
const statisticalTestList = document.querySelector(".statistical-test")

function setEventListeners() {

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
