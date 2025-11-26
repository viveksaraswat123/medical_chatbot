const API = "https://nonshrinkable-sumiko-unapprehendably.ngrok-free.dev/api"; 
// ↑ Change only when ngrok URL changes


//login fucntion
async function login() {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!email || !password) {
        document.getElementById("msg").textContent = "All fields are required.";
        return;
    }

    try {
        const res = await fetch(`${API}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (!res.ok || data.error) {
            document.getElementById("msg").textContent = data.error || "Login failed.";
            return;
        }

        // Store token + user_id
        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("token", data.token);

        // Redirect to chatbot
        window.location.href = "/chat";

    } catch (err) {
        console.error("Login Error:", err);
        document.getElementById("msg").textContent = "Server not responding.";
    }
}



//SIGNUP FUNCTION (Auto-Login & Redirect)
async function signup() {
    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!name || !email || !password) {
        document.getElementById("msg").textContent = "All fields are required.";
        return;
    }

    try {
        const res = await fetch(`${API}/signup`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, email, password })
        });

        const data = await res.json();

        if (!res.ok || data.error) {
            document.getElementById("msg").textContent = data.error || "Signup failed.";
            return;
        }

        // Auto-login after signup
        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("token", data.token);

        // Redirect directly to chat
        window.location.href = "/login";

    } catch (err) {
        console.error("Signup Error:", err);
        document.getElementById("msg").textContent = "Server not responding.";
    }
}
