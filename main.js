document.addEventListener('DOMContentLoaded', function() {
    var toggleDarkModeButton = document.getElementById('mode-switch');
   
    toggleDarkModeButton.addEventListener('click', function() {
       document.body.classList.toggle('dark');
    });
   });
   