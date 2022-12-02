console.log("popup script running");

const html = document.querySelector("html");


function openLeaguePop(){
  let leaguePopup = document.getElementById("leaguepopup");
  leaguePopup.style.top = (document.body.scrollTop + document.documentElement.scrollTop + 300)+"px";
  leaguePopup.classList.add('open-popup');
  event.stopPropagation()
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


function closeAllPops(){
  console.log("closing pops...")
  let pops = document.getElementsByClassName("popup");
  for (let i = 0; i < pops.length; i++) {
    pops[i].classList.remove('open-popup');
  }
}