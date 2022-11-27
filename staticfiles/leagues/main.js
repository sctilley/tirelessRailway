const hamburger = document.querySelector('.hamburger');
const mobile_menu = document.querySelector('.mobile-menu');

hamburger.addEventListener('click', function () {
    this.classList.toggle('is-active');
    mobile_menu.classList.toggle('is-open');
});


const menu = document.querySelector('.menu');

menu.addEventListener('click', function() {

})

document.querySelectorAll('.nav-link').forEach(link => {
    if(link.href === window.location.href){
      link.classList.add('is-active')
    }
  })

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

