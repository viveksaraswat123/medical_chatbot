const API = "";

async function login() {
    const email    = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!email || !password) {
        document.getElementById("msg").textContent = "All fields are required.";
        return;
    }

    try {
        const res  = await fetch(`${API}/api/login`, {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({ email, password })
        });

        let data;
        const text = await res.text();
        try {
            data = JSON.parse(text);
        } catch {
            console.error("Non-JSON response:", text);
            document.getElementById("msg").textContent = "Server error: " + text;
            return;
        }

        if (!res.ok || data.error) {
            document.getElementById("msg").textContent = data.error || data.detail || "Login failed.";
            return;
        }

        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("token",   data.token);

        window.location.href = "/chat";

    } catch (err) {
        console.error("Login Error:", err);
        document.getElementById("msg").textContent = "Server not responding.";
    }
}

async function signup() {
    const name     = document.getElementById("name").value.trim();
    const email    = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!name || !email || !password) {
        document.getElementById("msg").textContent = "All fields are required.";
        return;
    }

    try {
        const res  = await fetch(`${API}/api/signup`, {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({ name, email, password })
        });

        const data = await res.json();

        if (!res.ok || data.error) {
            document.getElementById("msg").textContent = data.error || data.detail || "Signup failed.";
            return;
        }

        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("token",   data.token);

        window.location.href = "/chat";

    } catch (err) {
        console.error("Signup Error:", err);
        document.getElementById("msg").textContent = "Server not responding.";
    }
}