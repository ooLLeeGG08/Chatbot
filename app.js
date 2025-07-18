const submitButton = document.getElementById('submitButton');
const chatbotInput = document.getElementById('chatbotInput');
const chatbotOutput = document.getElementById('chatbotOutput');

submitButton.onclick = userSubmitEventHandler;
chatbotInput.onkeyup = userSubmitEventHandler;

function userSubmitEventHandler(event) {
    if (
        (event.keyCode && event.keyCode === 13) ||
        event.type === 'click'
    ) {
        const userInput = chatbotInput.value.trim();
        if (userInput) {
            chatbotOutput.innerText = 'thinking...';
            askChatBot(userInput);
        }
    }
}

function askChatBot(userInput) {
    const myRequest = new Request('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userInput })
    });

    fetch(myRequest)
        .then(function(response) {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(function(data) {
            chatbotInput.value = '';
            if (data.status === 'success') {
                chatbotOutput.innerText = data.response;
            } else {
                chatbotOutput.innerText = data.error || 'Sorry, something went wrong.';
            }
        })
        .catch((err) => {
            console.error('Error:', err);
            chatbotOutput.innerText = 'Sorry, I\'m having trouble connecting. Please try again.';
        });
}
