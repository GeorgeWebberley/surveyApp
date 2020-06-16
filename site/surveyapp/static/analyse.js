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
  onChangeListener(surveyList, statisticalTests);
  onChangeListener(statisticalTestList, independentVariables);
  onChangeListener(independentVariableList, dependentVariables);
  onChangeListener(dependentVariableList, continueButton);
}

function onChangeListener(options, nextSection){
  options.onchange = function() {
    nextSection.classList.remove("hidden-axis");
    options.firstChild.hidden = true;
  }
}


setEventListeners()
