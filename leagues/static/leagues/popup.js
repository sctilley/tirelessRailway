console.log("popup script running");

const html = document.querySelector("html");


function openLeaguePop(){
  let leaguePopup = document.getElementById("leaguepopup");
  leaguePopup.style.top = (document.body.scrollTop + document.documentElement.scrollTop + 300)+"px";
  leaguePopup.classList.add('open-popup');
  event.stopPropagation()
  html.addEventListener("click", function (e){
    if (e.target !== leaguePopup)
      leaguePopup.classList.remove('open-popup')
  })
}

function openDropPop(){
  let dropPopup = document.getElementById("droppopup");
  console.log("openDropPop function");
  dropPopup.classList.add('open-popup')
  event.stopPropagation()
  html.addEventListener("click", function (e) {
    if (e.target !== dropPopup)
      dropPopup.classList.remove('open-popup');
  })
}

function openDeletePop(){
  let deletePopup = document.getElementById("deletepopup");
  deletePopup.classList.add('open-popup')
  event.stopPropagation()
  html.addEventListener("click", function (e) {
    if (e.target !== deletePopup)
      deletePopup.classList.remove('open-popup')
  })
}

// Add an event listener for a
        // click to the html document
// html.addEventListener("click", function (e) {
//   if (e.target !== dropPopup)
//     dropPopup.classList.remove('open-popup');

//   if (e.target !== deletePopup)
//     deletePopup.classList.remove('open-popup')
  
//   let leaguePopup = document.getElementById("leaguepopup");
//   if (e.target !== leaguePopup)
//     leaguePopup.classList.remove('open-popup')
// });