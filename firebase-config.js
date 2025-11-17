<script>
    // 🛑 PASTE YOUR CORRECT FIREBASE WEB API KEY HERE 🛑
    const CORRECT_API_KEY = "AIzaSyAtphL89Hn9xLiPm1UIkBnHR_sCt0M5h34"; 

    const firebaseConfig = {
        apiKey: CORRECT_API_KEY, 
        authDomain: "ai-based-loan-prediction.firebaseapp.com",
        projectId: "ai-based-loan-prediction",
        storageBucket: "ai-based-loan-prediction.firebasestorage.app",
        messagingSenderId: "159133794874",
        appId: "1:159133794874:web:2b48ab0913fcfcbefe6b03", // NOTE: Using the key from the first successful image
        measurementId: "G-SCCV9C7GTL"
    };
    
    // Initialize Firebase
    const app = firebase.initializeApp(firebaseConfig);
    const auth = app.auth();

    // ... (rest of the page's JavaScript continues here) ...
</script>