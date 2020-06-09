"use strict";

// ---- ASSIGNMENT OF VARIABLES TO QUERY SELECTORS ---- //

const addGraph = document.querySelector(".add-graph");
const dataTables = [...document.querySelectorAll(".dashboard-table")];
const overlay = document.querySelector(".overlay");
const close = document.querySelector(".close");
const graphType = document.querySelector(".graph-type");



// Add graph alert
if (addGraph != null) {
  addGraph.addEventListener("click", () => {
    overlay.classList.add("show-overlay")
  });
}

// Close alert box
if (close != null) {
  close.addEventListener("click", () => {
    overlay.classList.remove("show-overlay")
  });
}


if (graphType != null) {
  graphType.addEventListener("click", () => {
    overlay.classList.add("show-overlay")
  });
}
