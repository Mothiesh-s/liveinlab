import { auth } from './firebaseConfig.js';
import { signInWithEmailAndPassword } from 'https://www.gstatic.com/firebasejs/9.9.0/firebase-auth.js';

document.getElementById('loginButton').addEventListener('click', (e) => {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    signInWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            // User is logged in
            alert('Login successful! Redirecting to home page.');
            window.location.href = 'index.html';
        })
        .catch((error) => {
            console.error("Error:", error.message);
            alert(error.message);
        });
});
