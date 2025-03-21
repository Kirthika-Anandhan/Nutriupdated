document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");

    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault(); // Prevent page refresh

        // Get input values
        let email = document.getElementById("email").value;
        let password = document.getElementById("password").value;

        // Send data to the backend
        let response = await fetch("http://127.0.0.1:5000/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password }) // Convert to JSON
        });

        let result = await response.json();
        alert(result.message); // Show response message

        if (response.ok) {
            window.location.href = "details.html"; // Redirect on success
        }
    });
});
