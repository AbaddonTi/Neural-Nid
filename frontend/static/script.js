const form = document.getElementById('new-message-form');
const messageInput = document.getElementById('new-message-input');
const sendButton = document.getElementById('send-message-button');
const messageList = document.getElementById('message-list');

function init() {
    form.addEventListener('submit', handleFormSubmit);
}

function handleFormSubmit(event) {
    event.preventDefault();
    const messageText = messageInput.value.trim();

    if (!messageText) return;

    disableUI();
    clearInput();
    const userMessageElement = appendMessage(messageText, 'user');
    scrollToMessage(userMessageElement);
    sendUserMessage(messageText)
        .then(handleBotResponse)
        .catch(handleError)
        .finally(() => enableUI());
}

function sendUserMessage(messageText) {
    const userInfo = getUserInfo(messageText);
    const loadingElement = appendLoadingSpinner();
    return fetch('https://neuronalnid.com/api/send_message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userInfo)
    })
        .then(response => response.json())
        .finally(() => messageList.removeChild(loadingElement));
}

function handleBotResponse(data) {
    const botMessageElement = appendMessage(data.reply, 'bot');
    scrollToMessage(botMessageElement);
}

function handleError(error) {
    console.error('Error:', error);
    appendMessage("Sorry, I'm still in maintenance for a while...", 'bot', true);
}

function disableUI() {
    sendButton.disabled = true;
    messageInput.value = '';
}

function enableUI() {
    sendButton.disabled = false;
}

function appendMessage(messageText, messageType, isError = false) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', messageType);
    if (isError && window.innerWidth <= 600) {
        messageElement.style.scrollBehavior = 'smooth';
        messageElement.style.block = 'start';
    }
    messageElement.innerHTML = `<div class="text">${messageText}</div>`;
    messageList.appendChild(messageElement);
    return messageElement;
}

function scrollToMessage(messageElement) {
    setTimeout(() => {
        messageElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

function appendLoadingSpinner() {
    const loadingElement = document.createElement('div');
    loadingElement.classList.add('loading-spinner');
    messageList.appendChild(loadingElement);
    return loadingElement;
}

function getUserInfo(messageText) {
    const parser = new UAParser();
    const result = parser.getResult();
    return {
        message: messageText,
        browser: `${result.browser.name} ${result.browser.version}`,
        os: `${result.os.name} ${result.os.version}`,
        device: result.device.model ? `${result.device.vendor} ${result.device.model}` : 'Unknown device'
    };
}

function clearInput() {
    messageInput.value = '';
}

init();
