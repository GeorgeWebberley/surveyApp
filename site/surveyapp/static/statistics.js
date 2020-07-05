// The DOM elements representing the different sections
const statisticalTests = document.querySelector(".statistical-tests")
const independentVariables = document.querySelector(".independent-variables")
const dependentVariables = document.querySelector(".dependent-variables")
const continueButton = document.querySelector(".analyse-continue")

// The DOM elements representing the select fields
const independentVariableList = document.querySelector(".independent-variable")
const dependentVariableList = document.querySelector(".dependent-variable")
const statisticalTestList = document.querySelector(".statistical-test")

// The DOM elements representing different information to be given to the user, depending on what test they pick
const testInfo = document.querySelector(".test-info")
const independentInfo = document.querySelector(".iv-info")
const dependentInfo = document.querySelector(".dv-info")

// Information links for different data types
const nominal = "<a class='ml-3' href='graphs.nominal'>Nominal</a>"
const ordinal = "<a class='ml-3' href='graphs.ordinal'>Ordinal</a>"
const interval = "<a class='ml-3' href='graphs.interval'>Interval</a>"
const ratio = "<a class='ml-3' href='graphs.ratio'>Ratio</a>"


const tests = [
  {
    "name": "Kruskall Wallis Test",
    "iv": [nominal, ordinal],
    "dv": [ordinal, interval, ratio]
  },
  {
    "name": "Mann-Whitney U Test",
    "iv": [nominal, ordinal],
    "dv": [ordinal, interval, ratio],
    "info": `The Mann-Whitney U test requires that the independent variable consists of just 2
              categorical groups (e.g. questions with yes/no answers). If your independent variable
              contains more groups then the Kruskall Wallis test should be used.`
  }
]



function setEventListeners() {
  statisticalTestList.onchange = function() {
    independentVariables.classList.remove("hidden-axis");
    statisticalTestList.firstChild.hidden = true;
    tests.forEach(test => {
      if(test.name == statisticalTestList.value){
        if(test.info != undefined){
          testInfo.innerHTML = test.info;
        }
        let ivTypes = `The independent variable can be of type:`
        console.log(test);
        test.iv.forEach(variable => {
          ivTypes += variable
        })
        independentInfo.innerHTML = ivTypes
        let dvTypes = `The dependent variable can be of type:`
        test.dv.forEach(variable => {
          dvTypes += variable
        })
        dependentInfo.innerHTML = dvTypes
      }
    })
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
