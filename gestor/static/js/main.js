window.addEventListener("load", () => {
    const loader = document.querySelector(".loader");

    loader.classList.add("loader--hidden");

    loader.addEventListener("transitionend", () => {
        document.body.removeChild(loader);
    });
});

// Hide loader when page is fully loaded
window.onload = function () {
    document.querySelector('.loader').classList.add('loader--hidden');
}

// TOAST DE NOTIFICACIONES
$(document).ready(function () {
    $('.toast').toast('show');
});