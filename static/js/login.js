let passwordInput = document.getElementById('password');
let usernameInput = document.getElementById('username');

function openForm() {
    document.getElementById('fromLogin').style.display = 'block';
    document.getElementById('loginBtn').disabled = true;
}

function closeForm() {
    document.getElementById('fromLogin').style.display = 'none';
    document.getElementById('loginBtn').disabled = false;
}

async function login() {
    let username = usernameInput.value;
    let password = passwordInput.value;

    const response = await fetch('/login', {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    const data = await response.json();
    if (data === true) {
        window.location.replace('/');
    } else {
        passwordInput.value = '';
    }
}

passwordInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        login().then(r => {});
    }
});
