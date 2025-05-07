import { auth } from './firebaseConfig.js';
import { createUserWithEmailAndPassword } from 'https://www.gstatic.com/firebasejs/9.9.0/firebase-auth.js';

document.getElementById('submit').addEventListener('click', () => {
    const name = document.getElementById('signUpName').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    createUserWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            alert('Account created successfully! Redirecting to login.');
            window.location.href = 'login.html';
        })
        .catch((error) => {
            console.error("Error:", error.message);
            alert(error.message);
        });
});
