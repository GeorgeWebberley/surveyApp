"use strict";

const surveys = document.querySelectorAll(".survey");
const search =  document.getElementById("search");


search.addEventListener('keyup', function(){
  filterSurveys(search.value.toLowerCase())
});

function filterSurveys(searchValue){
  surveys.forEach(survey => {
    let name = survey.dataset.name.toLowerCase()
    if(name.includes(searchValue)){
      survey.style.display = "block";
    }else{
      survey.style.display = "none";
    }
  })
}
