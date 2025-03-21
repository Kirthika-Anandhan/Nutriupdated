document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("healthForm");
    const responseMsg = document.getElementById("responseMsg");

    form.addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent default form submission

        const formData = {
            name: document.getElementById("name").value.trim(),
            age: parseInt(document.getElementById("age").value) || null,
            weight: parseFloat(document.getElementById("weight").value) || null,
            height: parseFloat(document.getElementById("height").value) || null,
            blood_pressure: document.getElementById("blood_pressure").value.trim(),
            cholesterol: document.getElementById("cholesterol").value.trim(),
            sugar_level: document.getElementById("sugar_level").value.trim()
        };

        console.log("Submitting Data:", formData); // Debugging

        try {
            const response = await fetch("http://127.0.0.1:5000/submit", { // Ensure correct API URL
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const result = await response.json();
            responseMsg.textContent = result.message;
            responseMsg.style.color = "green";
            setTimeout(() => {
                window.location.href = "home.html";  // Change "/home" to your actual home page URL
            }, 2000);

            // Clear form after successful submission
            form.reset();
        } catch (error) {
            responseMsg.textContent = "Error submitting data.";
            responseMsg.style.color = "red";
            console.error("Error:", error);
        }
    });
});
