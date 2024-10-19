function toggleLoginModal() {
    var modal = document.getElementById('loginModal');
    modal.style.display = modal.style.display === 'none' ? 'block' : 'none';
}

function checkSession() {
    const token = document.cookie.split('; ').find(row => row.startsWith('access_token='));
    if (token) {
        const username = token.split('=')[1];  // Décoder correctement pour récupérer le nom d'utilisateur
        document.getElementById('loginModal').innerHTML = 'Bienvenue, ' + username + ' <button onclick="logout()">Déconnexion</button>';
    }
}

function logout() {
    fetch('/logout', {
        method: 'POST'
    }).then(() => {
        window.location.reload();  // Recharge la page pour réinitialiser l'état
    });
}
