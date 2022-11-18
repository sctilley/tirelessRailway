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






console.log("javascrip working now");