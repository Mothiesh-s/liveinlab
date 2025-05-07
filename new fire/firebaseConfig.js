// Your Firebase configuration here
import { initializeApp } from 'https://www.gstatic.com/firebasejs/9.9.0/firebase-app.js';
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, onAuthStateChanged } from 'https://www.gstatic.com/firebasejs/9.9.0/firebase-auth.js';

const firebaseConfig = {
    apiKey: "AIzaSyBiC6wU34g3SsuIg5Q00powYyXbH1rF-Tw",
    authDomain: "login-example-99a66.firebaseapp.com",
    projectId: "login-example-99a66",
    storageBucket: "login-example-99a66.firebasestorage.app",
    messagingSenderId: "1051671940995",
    appId: "1:1051671940995:web:61c4f9e688b5d01b7630b6"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
export { auth };
