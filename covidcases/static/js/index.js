function smoothScroll(target) {
    document.getElementById(target).scrollIntoView({
        behavior: 'smooth'
    });
}

function actionNav() {
  var x = document.getElementById("sidebar");
  if (x.style.left === "-240px") {
    openNav();
  } else {
    closeNav();
  }
}
function openNav() {
  document.getElementById("sidebar").style.left = "0";
}
function closeNav() {
  document.getElementById("sidebar").style.left = "-240px";
}