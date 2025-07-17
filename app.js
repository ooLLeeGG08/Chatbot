const submitButton = document.getElementById('submitButton');
const chatbotInput = document.getElementById('chatbotInput');
const chatbotOutput = document.getElementById('chatbotOutput');

submitButton.onclick = userSubmitEventHandler;
chatbotInput.onkeyup = userSubmitEventHandler;

// Focus on input when page loads
chatbotInput.focus();

function userSubmitEventHandler(event) {
    if (
        (event.keyCode && event.keyCode === 13) ||
        event.type === 'click'
    ) {
        const userInput = chatbotInput.value.trim();
        
        if (!userInput) {
            chatbotOutput.innerText = 'Please ask me something!';
            return;
        }
        
        chatbotOutput.innerText = 'Thinking...';
        submitButton.disabled = true;
        askChatBot(userInput);
    }
}

function askChatBot(userInput) {
    const myRequest = new Request('/', {
        method: 'POST',
        body: userInput,
        headers: {
            'Content-Type': 'text/plain'
        }
    });

    fetch(myRequest)
        .then(function(response) {
            if (!response.ok) {
                throw new Error(`HTTP error, status = ${response.status}`);
            }
            return response.text();
        })
        .then(function(text) {
            chatbotInput.value = '';
            chatbotOutput.innerText = text || 'Sorry, I got an empty response.';
        })
        .catch((err) => {
            console.error('Error:', err);
            chatbotOutput.innerText = 'Sorry, I encountered an error. Please try again.';
        })
        .finally(() => {
            submitButton.disabled = false;
            chatbotInput.focus();
        });
}
