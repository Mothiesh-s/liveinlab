import { auth } from './firebaseConfig.js';
import { onAuthStateChanged, signOut } from 'https://www.gstatic.com/firebasejs/9.9.0/firebase-auth.js';

window.onload = function() {
    onAuthStateChanged(auth, (user) => {
        const userProfileElement = document.getElementById('user-profile');
        const welcomeMessage = document.getElementById('welcome-message');
        if (user) {
            userProfileElement.classList.remove('d-none');
            welcomeMessage.textContent = `Welcome, ${user.email}!`;
        } else {
            window.location.href = 'login.html';
        }
    });
};

document.getElementById('logout').onclick = function() {
    signOut(auth).then(() => {
        window.location.href = 'login.html';
    }).catch((error) => {
        console.error('Error during sign out:', error.message);
    });
};
