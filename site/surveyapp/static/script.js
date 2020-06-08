"use strict";

// ---- ASSIGNMENT OF VARIABLES TO QUERY SELECTORS ---- //

const addGraph = document.querySelector(".add-graph");
const dataTables = [...document.querySelectorAll(".dashboard-table")];
const overlay = document.querySelector(".overlay");
const close = document.querySelector(".close");



// Add graph alert
if (addGraph != null) {
  addGraph.addEventListener("click", () => {
    overlay.classList.add("show-overlay")
  });
}

// Add graph alert
if (close != null) {
  close.addEventListener("click", () => {
    overlay.classList.remove("show-overlay")
  });
}
