const form = document.getElementById('new-message-form');
const messageInput = document.getElementById('new-message-input');
const sendButton = document.getElementById('send-message-button');
const messageList = document.getElementById('message-list');


// region Google Analytics
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-B9SZ2PRDMG');


function handleBotResponse(data) {
    const botMessageElement = appendMessage(data.reply, 'bot');
    scrollToMessage(botMessageElement);
    // Имя события обновлено для согласованности
    gtag('event', 'message_receive', {
        'event_category': 'Message',
        'event_label': 'Message Received'
    });
}


const aboutUsLink = document.querySelector('.about-us-link');
if (aboutUsLink) {
    aboutUsLink.addEventListener('click', function() {
        gtag('event', 'about_us_clicked', {
            'event_category': 'About Us Link',
            'event_label': 'About Us Page Visited'
        });
    });
}


function init() {
    if (form) {
        form.addEventListener('submit', function(event) {
            handleFormSubmit(event);
            gtag('event', 'message_sent', {
                'event_category': 'Message',
                'event_label': 'Message Sent'
            });
        });
    }
}
// endregion Google Analytics


document.addEventListener('DOMContentLoaded', (event) => {
    setTimeout(showWelcomeMessage, 500);
});


function showWelcomeMessage() {
    const welcomeText = "Bonjour, <br><br>Je suis votre assistant personnel à Montpellier. <br><br>N'hésitez pas à me poser des questions dans n'importe quelle langue.";
    const loadingElement = appendLoadingSpinner();

    setTimeout(() => {
        messageList.removeChild(loadingElement);
        appendMessage(welcomeText, 'bot');
        scrollToMessage(messageList.lastChild);
    }, 2500);
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
