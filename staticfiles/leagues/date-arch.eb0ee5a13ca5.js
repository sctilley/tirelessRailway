document.getElementById('datebutton1').onclick = openDate;
document.getElementById('datebutton2').onclick = openDate;
document.getElementById('datebutton3').onclick = openDate;
document.getElementById('datebutton4').onclick = openDate;
document.getElementById('datebutton5').onclick = openDate;


function openDate(){
  console.log("button clicked, id "+this.id);
  this.classList.toggle('hidden');
  this.nextElementSibling.classList.toggle('hidden');
  this.nextElementSibling.nextElementSibling.classList.toggle('hidden');
}

document.getElementById('archbutton1').onclick = openArch;
document.getElementById('archbutton2').onclick = openArch;
document.getElementById('archbutton3').onclick = openArch;
document.getElementById('archbutton4').onclick = openArch;
document.getElementById('archbutton5').onclick = openArch;

function openArch(){
  console.log("Arch button clicked, id "+this.id);
  this.classList.toggle('hidden');
  this.nextElementSibling.classList.toggle('hidden');
}


console.log("javascrip working now");

