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


// Information boxes for different data types
const nominal = `<span data-toggle='tooltip' class="badge badge-light ml-3"
title='Nominal data has no numeric value (i.e. cannot be measured) and has no natural order to it. An example could be race, gender or yes/no questions.'>
Nominal</span>`
const ordinal = `<span data-toggle='tooltip' class="badge badge-light ml-3"
title='Ordinal data has no numeric value but it does have a natural order. An example could be positions in a race (first, second, third) or Likert type questions (answers ranging from strongly agree to strongly disagree).'>
Ordinal</span>`
const interval = `<span data-toggle='tooltip' class="badge badge-light ml-3"
title='Interval data has numeric value, with equal value between each point, but 0 does not mean absolute 0. An example could be temperature in Celcius (0°C does not mean absolute 0 since you can have negative degree Celcius)'>
Interval</span>`
const ratio = `<span data-toggle='tooltip' class="badge badge-light ml-3"
title='Ratio data is similar to interval data in that it has numeric value, but it also has absolute 0 (i.e. no negative values). An example could be weight or height.'>
Ratio</span>`


const tests = [
  {
    "name": "Kruskall Wallis Test",
    "iv": [nominal, ordinal],
    "dv": [ordinal, interval, ratio],
    "info": ""
  },
  {
    "name": "Mann-Whitney U Test",
    "iv": [nominal, ordinal],
    "dv": [ordinal, interval, ratio],
    "info": `The Mann-Whitney U test requires that the independent variable consists of just 2
              categorical groups (e.g. questions with yes/no answers). If your independent variable
              contains more groups then the Kruskall Wallis test should be used.`
  },
  {
    "name": "Chi-Square Test",
    "iv": [nominal, ordinal],
    "dv": [nominal, ordinal],
    "info": `The Chi Square test requires that both variables be categorical (i.e. nominal or ordinal).
              Both variables should contain 2 or more distinct categorical groups (e.g.
              2 groups: yes/no answers, 3 groups: low/medium/high income) Furthermore, these groups must
              be independent (i.e. no subjects are in more than one group).`
  }
]


// set page event listeners on each of the drop down menus
function setEventListeners() {

  revealHtml(statisticalTestList, independentVariables)
  revealHtml(independentVariableList, dependentVariables)
  revealHtml(dependentVariableList, continueButton)
  populateInfo()
  statisticalTestList.onchange = function() {
    independentVariables.classList.remove("hidden-axis");
    statisticalTestList.firstChild.hidden = true;
    // Loop through each test and check to see if it is the one selected
    populateInfo()
    // Using Jquery, initialise Popper.js tooltips
    $('[data-toggle="tooltip"]').tooltip()
  }

  // Add event listeners that re-sets the options whenever one is changed
  independentVariableList.onchange = function(){
    setSelectOptions(independentVariableList, dependentVariableList, dependentVariables);
  }
  dependentVariableList.onchange = function(){
    setSelectOptions(dependentVariableList, independentVariableList, continueButton);
  }
}


// A function that hides some select options, preventing user from picking the same option for both variables
function setSelectOptions(currentSelect, otherSelect, nextSection){
  revealHtml(currentSelect, nextSection)
  variable = currentSelect.value
  for (var i=0; i < otherSelect.length; i++) {
      if (otherSelect.options[i].value == variable){
        otherSelect.options[i].hidden = true;
      } else {
        otherSelect.options[i].hidden = false;
      }
  }
}

// Function that reveals the next section of HTML, after the user selects an option in the current section
function revealHtml(currentSelect, nextSection){
  if(currentSelect.value != ""){
    nextSection.classList.remove("hidden-axis");
  }
}

// Function that populates the html with information regarding the statistical test chosen and the variables required
function populateInfo(){
  tests.forEach(test => {
    if(test.name == statisticalTestList.value){
      testInfo.innerHTML = test.info;
      // Populate the HTML based on the selected test
      let ivTypes = `The independent variable can be of type:`
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



setEventListeners()
