console.log("popup script running");

let dropPopup = document.getElementById("droppopup");
let deletePopup = document.getElementById("deletepopup");

function openDropPop(){
  console.log("openDropPop function");
  dropPopup.classList.add('open-popup')

}

function openDeletePop(){
  deletePopup.classList.add('open-popup')

}