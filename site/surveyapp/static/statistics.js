"use strict";

// The DOM elements representing the different sections
const statisticalTests = document.querySelector(".statistical-tests")
const independentVariables = document.querySelector(".independent-variables")
const dependentVariables = document.querySelector(".dependent-variables")
const continueButton = document.querySelector(".analyse-continue")

// The DOM elements representing the question text
const firstQuestion = document.querySelector(".first-variable-question")
const secondQuestion = document.querySelector(".second-variable-question")


// The DOM elements representing the select fields
const independentVariableList = document.querySelector(".independent-variable")
const dependentVariableList = document.querySelector(".dependent-variable")
const statisticalTestList = document.querySelector(".statistical-test")

// The DOM elements representing different information to be given to the user, depending on what test they pick
const testInfo = document.querySelector(".test-info")
const independentInfo = document.querySelector(".iv-info")
const dependentInfo = document.querySelector(".dv-info")

// A boolean flag, to keep track of how many variables in the chosen statistical test
let one_variable = false


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
    "variable1": {
      "name": "independent variable",
      "type": [nominal, ordinal]
    },
    "variable2": {
      "name": "dependent variable",
      "type": [ordinal, interval, ratio]
    },
    "info": ""
  },
  {
    "name": "Mann-Whitney U Test",
    "variable1": {
      "name": "independent variable",
      "type": [nominal, ordinal]
    },
    "variable2": {
      "name": "dependent variable",
      "type": [ordinal, interval, ratio]
    },
    "info": `The Mann-Whitney U test requires that the independent variable consists of just 2
              categorical groups (e.g. questions with yes/no answers). If your independent variable
              contains more groups then the Kruskall Wallis test should be used.`
  },
  {
    "name": "Chi-Square Test",
    "variable1": {
      "name": "first variable",
      "type": [nominal, ordinal]
    },
    "variable2": {
      "name": "second variable",
      "type": [nominal, ordinal]
    },
    "info": `The Chi Square test requires that both variables be categorical (i.e. nominal or ordinal).
              Both variables should contain 2 or more distinct categorical groups (e.g.
              2 groups: yes/no answers, 3 groups: low/medium/high income) Furthermore, these groups must
              be independent (i.e. no subjects are in more than one group).`
  },
  {
    "name": "Chi-Square goodness of fit",
    "variable1": {
      "name": "first variable",
      "type": [nominal, ordinal]
    },
    "info": `The Chi Square goodness of fit takes one categorical variable. It is used to see if the
              different categories in that variable follow the same distribution that you would expect.`
  }
]


if(statisticalTestList.value != ""){
  populateInfo();
  // Add event listeners that re-sets the options whenever one is changed
  independentVariableList.onchange = function(){
    setSelectOptions(independentVariableList, dependentVariableList);
  }
  dependentVariableList.onchange = function(){
    setSelectOptions(dependentVariableList, independentVariableList);
  }
}


statisticalTestList.onchange = function (){
  // Using Jquery, initialise Popper.js tooltips
  $(function () {
      $("[data-toggle='tooltip']").tooltip();
  });
  populateInfo();
  // Add event listeners that re-sets the options whenever one is changed
  independentVariableList.onchange = function(){
    if(one_variable == true){
      revealHtml(independentVariableList, continueButton)
    }
    setSelectOptions(independentVariableList, dependentVariableList);
  }
  dependentVariableList.onchange = function(){
    setSelectOptions(dependentVariableList, independentVariableList);
    revealHtml(dependentVariableList, continueButton)
  }
}



//
//
// // set page event listeners on each of the drop down menus
// function setEventListeners() {
//
//   revealHtml(statisticalTestList, independentVariables)
//   if(one_variable){
//     revealHtml(independentVariableList, continueButton)
//     dependentVariables.classList.add("hidden-axis")
//   }else{
//     revealHtml(independentVariableList, dependentVariables)
//   }
//   revealHtml(dependentVariableList, continueButton)
//   populateInfo()
//   statisticalTestList.onchange = function() {
//     independentVariables.classList.remove("hidden-axis");
//     dependentVariables.classList.add("hidden-axis");
//     statisticalTestList.firstChild.hidden = true;
//     // Loop through each test and check to see if it is the one selected
//     populateInfo()
//     // Using Jquery, initialise Popper.js tooltips
//     $('[data-toggle="tooltip"]').tooltip()
//   }
//   // Add event listeners that re-sets the options whenever one is changed
//   independentVariableList.onchange = function(){
//     if(one_variable){
//       setSelectOptions(independentVariableList, dependentVariableList, continueButton);
//       dependentVariables.classList.add("hidden-axis")
//     }else{
//       setSelectOptions(independentVariableList, dependentVariableList, dependentVariables);
//     }
//   }
//   dependentVariableList.onchange = function(){
//     setSelectOptions(dependentVariableList, independentVariableList, continueButton);
//   }
// }


// A function that hides some select options, preventing user from picking the same option for both variables
function setSelectOptions(currentSelect, otherSelect){
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
  let test = getTest(statisticalTestList.value)
  if(test){
    // Populate the question titles, information and data types based on the selected test
    // Question 1
    firstQuestion.innerHTML = test.variable1.name
    testInfo.innerHTML = test.info;
    let ivTypes = `For this test the independent variable can be:`
    test.variable1.type.forEach(variable => {
      ivTypes += variable
    })
    independentInfo.innerHTML = ivTypes
    if(test.variable2 == undefined){
      one_variable = true;
      independentVariables.classList.remove("hidden-axis");
      dependentVariables.classList.add("hidden-axis");
      revealHtml(independentVariableList, continueButton)
    }else{
      independentVariables.classList.remove("hidden-axis");
      dependentVariables.classList.remove("hidden-axis");
      revealHtml(dependentVariableList, continueButton)
      one_variable = false;
      // Question 2
      secondQuestion.innerHTML = test.variable2.name
      let dvTypes = `For this test the dependent variable can be:`
      test.variable2.type.forEach(variable => {
        dvTypes += variable
      })
      dependentInfo.innerHTML = dvTypes
    }
  }
}


function getTest(name){
  let result
  tests.forEach(test => {
    if(test.name == name){
      result = test;
    }
  })
  return result
}


// setEventListeners()
