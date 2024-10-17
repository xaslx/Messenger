function toggleMenu() {
    var menu = document.getElementById("dropdown-menu");
    menu.classList.toggle("show");
}


window.onclick = function(event) {
    if (!event.target.matches('.avatar img')) {
        var dropdowns = document.getElementsByClassName("dropdown-menu");
        for (var i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}

function logout(event) {
    event.preventDefault(); 

    fetch('/auth/logout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (response.ok) {
            window.location.href = '/auth/login';
        } else {
            return response.text().then(text => {
                throw new Error(text);
            });
        }
    })
    .catch(error => {
        Swal.fire('Ошибка', 'Не удалось выполнить выход', 'error');
    });
}