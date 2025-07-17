class CodeExecutionChatbot {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.messageHistory = [];
    }

    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.userInput = document.getElementById('userInput');
        this.sendButton = document.getElementById('sendButton');
        this.languageSelect = document.getElementById('languageSelect');
    }

    bindEvents() {
        this.sendButton.addEventListener('click', () => this.handleSend());
        this.userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSend();
            }
        });

        this.languageSelect.addEventListener('change', () => {
            this.updateInputPlaceholder();
        });

        // Auto-resize textarea
        this.userInput.addEventListener('input', () => {
            this.autoResizeTextarea();
        });
    }

    updateInputPlaceholder() {
        const language = this.languageSelect.value;
        const placeholders = {
            'chat': 'Type your message here...',
            'javascript': 'Enter JavaScript code (e.g., console.log("Hello World!"))',
            'python': 'Enter Python code (e.g., print("Hello World!"))'
        };
        this.userInput.placeholder = placeholders[language];
    }

    autoResizeTextarea() {
        this.userInput.style.height = 'auto';
        this.userInput.style.height = Math.min(this.userInput.scrollHeight, 120) + 'px';
    }

    async handleSend() {
        const message = this.userInput.value.trim();
        if (!message) return;

        const language = this.languageSelect.value;
        
        // Disable input while processing
        this.setInputDisabled(true);
        
        // Add user message to chat
        this.addMessage(message, 'user', language);
        
        // Clear input
        this.userInput.value = '';
        this.autoResizeTextarea();
        
        // Show typing indicator
        const typingId = this.showTypingIndicator();
        
        try {
            // Send to backend
            const response = await this.sendToBackend(message, language);
            this.removeTypingIndicator(typingId);
            this.addMessage(response.content, 'bot', null, response.type, response.error);
        } catch (error) {
            this.removeTypingIndicator(typingId);
            this.addMessage('Sorry, there was an error processing your request.', 'bot', null, 'error');
            console.error('Error:', error);
        }
        
        // Re-enable input
        this.setInputDisabled(false);
        this.userInput.focus();
    }

    async sendToBackend(message, language) {
        const payload = {
            message: message,
            language: language,
            history: this.messageHistory.slice(-10) // Send last 10 messages for context
        };

        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    addMessage(content, sender, language = null, type = 'text', isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        if (type === 'code' && language) {
            const codeBlock = document.createElement('div');
            codeBlock.className = 'code-block';
            const pre = document.createElement('pre');
            const code = document.createElement('code');
            code.className = `language-${language}`;
            code.textContent = content;
            pre.appendChild(code);
            codeBlock.appendChild(pre);
            messageContent.appendChild(codeBlock);
            
            // Highlight code
            if (window.hljs) {
                hljs.highlightElement(code);
            }
        } else if (type === 'result') {
            const resultDiv = document.createElement('div');
            resultDiv.className = isError ? 'execution-error' : 'execution-result';
            resultDiv.textContent = content;
            messageContent.appendChild(resultDiv);
        } else {
            const textSpan = document.createElement('span');
            textSpan.className = 'message-text';
            textSpan.textContent = content;
            messageContent.appendChild(textSpan);
        }
        
        messageDiv.appendChild(messageContent);
        this.chatMessages.appendChild(messageDiv);
        
        // Store in history
        this.messageHistory.push({
            content: content,
            sender: sender,
            language: language,
            type: type,
            timestamp: new Date().toISOString()
        });
        
        // Scroll to bottom
        this.scrollToBottom();
    }

    showTypingIndicator() {
        const typingId = 'typing-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        messageDiv.id = typingId;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        typingIndicator.innerHTML = '<span></span><span></span><span></span>';
        
        messageContent.appendChild(typingIndicator);
        messageDiv.appendChild(messageContent);
        this.chatMessages.appendChild(messageDiv);
        
        this.scrollToBottom();
        return typingId;
    }

    removeTypingIndicator(typingId) {
        const typingElement = document.getElementById(typingId);
        if (typingElement) {
            typingElement.remove();
        }
    }

    setInputDisabled(disabled) {
        this.userInput.disabled = disabled;
        this.sendButton.disabled = disabled;
        this.languageSelect.disabled = disabled;
    }

    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
}

// Initialize the chatbot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const chatbot = new CodeExecutionChatbot();
    
    // Set initial placeholder
    chatbot.updateInputPlaceholder();
    
    // Focus on input
    chatbot.userInput.focus();
});

// Initialize highlight.js when available
document.addEventListener('DOMContentLoaded', () => {
    if (window.hljs) {
        hljs.configure({
            languages: ['javascript', 'python', 'json', 'html', 'css']
        });
    }
});
