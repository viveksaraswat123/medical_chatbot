document.addEventListener('DOMContentLoaded', () => {
    const chatBox   = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn   = document.getElementById('send-btn');

    let conversationId = null;

    const API_BASE_URL = "";  // relative — works locally and on Render

    // Auth headers for protected endpoints
    const authHeaders = () => ({
        "Content-Type": "application/json",
        "Authorization": `Bearer ${localStorage.getItem("token")}`
    });

    // Redirect to login if no token
    if (!localStorage.getItem("token")) {
        window.location.href = "/login";
        return;
    }

    sendBtn.disabled  = true;
    userInput.disabled = true;

    // ── Start a new conversation ──
    const startConversation = async () => {
        try {
            showLoading();
            const response = await fetch(`${API_BASE_URL}/api/new_chat`, {
                method:  "POST",
                headers: authHeaders()
            });
            hideLoading();

            if (response.status === 401) {
                window.location.href = "/login";
                return;
            }
            if (!response.ok) throw new Error("Failed to start conversation");

            const data = await response.json();
            conversationId = data.chat_id;  // API returns chat_id, not conversation_id

            sendBtn.disabled   = false;
            userInput.disabled = false;
            addMessage("Hello! I am MediBot. How can I help you today?", "bot");

        } catch (error) {
            hideLoading();
            console.error("Error starting conversation:", error);
            addMessage("Sorry, I am unable to connect right now. Please try again later.", "bot");
        }
    };

    // ── Add a message bubble ──
    const addMessage = (text, sender) => {
        const el = document.createElement("div");
        el.classList.add("message", `${sender}-message`);
        el.innerHTML = marked.parse(text);
        chatBox.appendChild(el);
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    // ── Typing indicator ──
    const showLoading = () => {
        const el = document.createElement("div");
        el.classList.add("message", "bot-message", "loading-indicator");
        el.innerHTML = "<span></span><span></span><span></span>";
        chatBox.appendChild(el);
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    const hideLoading = () => {
        const el = document.querySelector(".loading-indicator");
        if (el) el.remove();
    };

    // ── Send a message ──
    const handleSendMessage = async () => {
        const messageText = userInput.value.trim();
        if (!messageText || !conversationId) return;

        sendBtn.disabled   = true;
        userInput.disabled = true;

        addMessage(messageText, "user");
        userInput.value = "";
        showLoading();

        try {
            const response = await fetch(`${API_BASE_URL}/api/chat`, {
                method:  "POST",
                headers: authHeaders(),
                body:    JSON.stringify({
                    conversation_id: conversationId,
                    message:         messageText
                }),
            });

            hideLoading();

            if (response.status === 401) {
                window.location.href = "/login";
                return;
            }
            if (!response.ok) throw new Error("Server returned an error");

            const data = await response.json();
            addMessage(data.response, "bot");

        } catch (error) {
            console.error("Error sending message:", error);
            hideLoading();
            addMessage("I encountered an error. Please try your question again.", "bot");
        } finally {
            sendBtn.disabled   = false;
            userInput.disabled = false;
            userInput.focus();
        }
    };

    // ── Event listeners ──
    sendBtn.addEventListener("click", handleSendMessage);
    userInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    // ── Init ──
    startConversation();
});