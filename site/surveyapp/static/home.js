const surveysDOM = document.querySelectorAll(".home-table")
const graphsDOM = document.querySelectorAll(".home-graph")
const testsDOM = document.querySelectorAll(".home-test")
const noGraphs = document.querySelector(".no-graphs")
const yesGraphs = document.querySelector(".yes-graphs")
const noTests = document.querySelector(".no-tests")
const yesTests = document.querySelector(".yes-tests")
const graphsSection = document.querySelector(".home-graphs")
const testsSection = document.querySelector(".home-stats")


surveysDOM.forEach(survey=> {
  survey.addEventListener("click", (event)=> {
    // if(event.target.class != "home-table") return;
    graphsSection.classList.remove("no-display")
    testsSection.classList.remove("no-display")
    fetch("/home/" + survey.dataset.id)
      .then(response => response.json())
      .then(data => {
        // Get the graphs data (in string format) and convert back to json array
        let graphs = JSON.parse(data.graphs)
        let tests = data.tests
        populateGraphGrid(graphs, survey.dataset.id)
        // populateTestGrid(tests, survey.dataset.id)
        // console.log(data.graphs);
        // console.log(data.tests);
      })
  })
})

function populateGraphGrid (graphs, id){
  if(graphs.length == 0){
    console.log("lol1");
    noGraphs.classList.remove("no-display")
    yesGraphs.classList.add("no-display")
  } else{
    noGraphs.classList.add("no-display")
    yesGraphs.classList.remove("no-display")
    graphsDOM.forEach(graph => {
      if(graph.dataset.survey != id){
        // hide any graphs not related to that survey
        graph.classList.add("no-display")
      }
    })
  }
}

// function populateTestGrid (tests, id){
//   if(tests.length == 0){
//     testContainer.innerHTML = `
//     <div class="no-graphs-container">
//       <div class="empty add-graph">
//         <p>You have no graphs.</p>
//         <p>Click here to get started.</p>
//         <i class="fa fa-plus-circle fa-lg" aria-hidden="true"></i>
//       </div>
//     </div>
//     `
//   } else{
//     graphs.forEach(graph => {
//       if(graph["surveyId"] != id){
//         console.log(graph["title"]);
//         // hide any graphs not related to that survey
//         graph.classList.add("no-display")
//       }
//     })
//   }
// }
