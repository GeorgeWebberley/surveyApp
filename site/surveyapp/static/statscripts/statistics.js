"use strict";

// The DOM elements representing the different sections
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
const nominal = `<span data-toggle='tooltip' class="badge badge-dark ml-3 help"
title='Nominal data has no numeric value (i.e. cannot be measured) and has no natural order to it. An example could be race, gender or yes/no questions.'>
Nominal</span>`
const ordinal = `<span data-toggle='tooltip' class="badge badge-dark ml-3 help"
title='Ordinal data has no numeric value but it does have a natural order. An example could be positions in a race (first, second, third) or Likert type questions (answers ranging from strongly agree to strongly disagree).'>
Ordinal</span>`
const interval = `<span data-toggle='tooltip' class="badge badge-dark ml-3 help"
title='Interval data has numeric value, with equal value between each point, but 0 does not mean absolute 0. An example could be temperature in Celcius (0°C does not mean absolute 0 since you can have negative degree Celcius)'>
Interval</span>`
const ratio = `<span data-toggle='tooltip' class="badge badge-dark ml-3 help"
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
    "info": `Kruskal Wallis test is commonly used to test the null hypothesis that the samples (groups) are from
            the same population. It tests one categorical variable against a measurable variable.
            The dependent variable must be ordinal, interval or ratio. Typically, this test is used to test when you have
            3 or more different groups in your independent variable, but can also be used for just 2 groups (examples could be
            3 groups: low/medium/high income, 2 groups: yes/no answers).`
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
    "info": `The Mann-Whitney U test is used to check if observations in one sample are larger
              than observations in the other sample. It requires that the independent variable
              consists of just 2 categorical groups (e.g. questions with yes/no answers). If your
              independent variable contains more groups then the Kruskall Wallis test should be used.`
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
              different categories in that variable follow the same distribution that you would expect.
              Assumes that the expected distribution is even accross groups, that each group is mutually
              exclusive from the next and each group contains at least 5 subjects.`
  }
]


if(statisticalTestList.value != ""){
  // Using Jquery, initialise Popper.js tooltips
  $(function () {
      $("[data-toggle='tooltip']").tooltip();
  });
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


// A function that hides some select options, preventing user from picking the same option for both variables
function setSelectOptions(currentSelect, otherSelect){
  let variable = currentSelect.value
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
    nextSection.classList.remove("hidden-down");
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
      independentVariables.classList.remove("hidden-down");
      dependentVariables.classList.add("hidden-down");
      revealHtml(independentVariableList, continueButton)
    }else{
      independentVariables.classList.remove("hidden-down");
      dependentVariables.classList.remove("hidden-down");
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
