document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    let conversationId = null;
    // Allow overriding API base URL from the page (useful in deployments).
    // Defaults to a relative path so the frontend can be served from the same origin as the API.
    const API_BASE_URL = window.__API_BASE__ || '/api';

    // Disable UI until conversation is ready
    sendBtn.disabled = true;
    userInput.disabled = true;

    // --- Function to start a new conversation ---
    const startConversation = async () => {
        try {
            showLoading();
            const response = await fetch(`${API_BASE_URL}/start_conversation`);
            hideLoading();
            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();
            conversationId = data.conversation_id;
            // Enable input now that we have a conversation
            sendBtn.disabled = false;
            userInput.disabled = false;
            addMessage('Hello! I am MediBot. How can I help you today?', 'bot');
        } catch (error) {
            hideLoading();
            console.error('Error starting conversation:', error);
            addMessage('Sorry, I am unable to connect right now. Please try again later.', 'bot');
        }
    };

    // --- Function to add a message to the UI ---
    const addMessage = (text, sender) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        messageElement.innerHTML = marked.parse(text);

        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll
    };

    // --- Function to show loading indicator ---
    const showLoading = () => {
        const loadingElement = document.createElement('div');
        loadingElement.classList.add('message', 'bot-message', 'loading-indicator');
        loadingElement.innerHTML = '<span></span><span></span><span></span>';
        chatBox.appendChild(loadingElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    // --- Function to remove loading indicator ---
    const hideLoading = () => {
        const loadingElement = document.querySelector('.loading-indicator');
        if (loadingElement) {
            loadingElement.remove();
        }
    };

    // --- Function to handle sending a message ---
    const handleSendMessage = async () => {
        const messageText = userInput.value.trim();
        if (!messageText || !conversationId) return;

        // Disable UI while sending to avoid duplicate requests
        sendBtn.disabled = true;
        userInput.disabled = true;

        addMessage(messageText, 'user');
        userInput.value = '';
        showLoading();

        try {
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    conversation_id: conversationId,
                    message: messageText
                }),
            });

            hideLoading();

            if (!response.ok) throw new Error('Server returned an error');
            const data = await response.json();
            addMessage(data.response, 'bot');

        } catch (error) {
            console.error('Error sending message:', error);
            hideLoading();
            addMessage('I encountered an error. Please try your question again.', 'bot');
        } finally {
            // Re-enable UI
            sendBtn.disabled = false;
            userInput.disabled = false;
            userInput.focus();
        }
    };

    // --- Event Listeners ---
    sendBtn.addEventListener('click', handleSendMessage);
    // Use keydown to handle Enter; support Shift+Enter for newlines in textareas
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    // --- Initialize ---
    startConversation();
});