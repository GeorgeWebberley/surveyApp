"use strict";

// Function that auto creates dynamic grid depending on grid element size
var container = document.querySelector('.stats-grid');
var msnry = new Masonry( container, {

  columnWidth: '.grid-element',
  itemSelector: '.grid-element',
  gutter: 10
});
