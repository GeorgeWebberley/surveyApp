"use strict";

// Select DOM elements
const total = document.querySelector(".chi-total")
const inputs = document.querySelectorAll("input[type=text]")
const submit = document.querySelector(".analyse-continue")


inputs.forEach(input => {
  input.addEventListener('keyup', function(){
    checkTotal()
  });
})


function getSumOfInputs(){
  let total = 0;
  inputs.forEach(input => {
    let expected = parseInt(input.value)
    if (Number.isNaN(expected)){
      expected=0
    }
    total += expected
  })
  return total
}

function checkTotal(){
  let sum = getSumOfInputs()
  total.innerHTML = sum;
  if(sum == totalChi || sum == 0){
    total.style.color = "LightGreen"
    submit.classList.remove("hidden-axis")
  }else{
    total.style.color = "LightPink"
    submit.classList.add("hidden-axis")
  }
}

checkTotal()
