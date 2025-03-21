document.addEventListener("DOMContentLoaded", () => {
    const signupForm = document.getElementById("signupForm");

    signupForm.addEventListener("submit", async (e) => {
        e.preventDefault(); // Prevent page refresh

        // Get input values
        let fullName = document.getElementById("fullName").value.trim();
        let age = document.getElementById("age").value.trim();
        let gender = document.getElementById("gender").value.trim();
        let email = document.getElementById("email").value.trim();
        let phoneNumber = document.getElementById("phoneNumber").value.trim();
        let password = document.getElementById("password").value.trim(); // ✅ Added password

        // Simple validation check
        if (!fullName || !age || !gender || !email || !phoneNumber || !password) {
            alert("Please fill all fields.");
            return;
        }

        try {
            let response = await fetch("http://127.0.0.1:5000/signup", { 
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ fullName, age, gender, email, phoneNumber, password }) // ✅ Sending password
            });

            let result = await response.json();

            if (response.ok) {
                alert(result.message);
                window.location.href = "details.html"; // Redirect on success
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error("Signup Error:", error);
            alert("Something went wrong. Please try again.");
        }
    });
});

