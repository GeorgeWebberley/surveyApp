"use strict";

// ---- ASSIGNMENT OF VARIABLES TO QUERY SELECTORS ---- //

const addGraph = document.querySelector(".add-graph");
const dataTables = [...document.querySelectorAll(".dashboard-table")];
const overlay = document.querySelector(".overlay");
const close = document.querySelector(".close");
const graphType = document.querySelector(".graph-type");
const saveGraphTitle = document.querySelector(".save-graph-title");
const editGraphTitle = document.querySelector(".edit-graph-title");



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


if (saveGraphTitle != null) {
  saveGraphTitle.addEventListener("click", () => {
    editGraphTitle.classList.remove("hide-title")
    saveGraphTitle.classList.add("hide-title")
  });
}
