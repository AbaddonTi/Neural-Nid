const form = document.getElementById('new-message-form');
const messageInput = document.getElementById('new-message-input');
const sendButton = document.getElementById('send-message-button');
const messageList = document.getElementById('message-list');


// region Google Analytics
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-B9SZ2PRDMG');
// endregion Google Analytics


// region Event Handlers

let lastUserMessage = null;
let lastBotResponse = null;

function handleBotResponse(data) {
    const botMessageElement = appendMessage(data.reply, 'bot');
    scrollToMessage(botMessageElement);
    lastBotResponse = data.reply;
    gtag('event', 'message_receive', {
        'event_category': 'Message',
        'event_label': 'Message Received'
    });
}


function handleFormSubmit(event) {
    event.preventDefault();
    const messageText = messageInput.value.trim();

    if (!messageText) return;

    disableUI();
    clearInput();
    updateCharactersLeft();
    const userMessageElement = appendMessage(messageText, 'user');
    scrollToMessage(userMessageElement);
    sendUserMessage(messageText)
        .catch(handleError)
        .finally(() => enableUI());
}


function handleError(error) {
    console.error('Error:', error);
    appendMessage("Sorry, I'm still in maintenance for a while...", 'bot', true);
}
// endregion Event Handlers

// region UI Updates
function disableUI() {
    sendButton.disabled = true;
    messageInput.value = '';
}


function enableUI() {
    sendButton.disabled = false;
}


function updateCharactersLeft() {
    var currentLength = messageInput.value.length;
    var maxLength = messageInput.maxLength; 
    var charactersLeft = maxLength - currentLength;
    var charactersLeftSpan = document.getElementById('characters-left');
    charactersLeftSpan.textContent = `${charactersLeft}/${maxLength}`;
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


function applyBackgroundTheme() {
    const urlParams = new URLSearchParams(window.location.search);
    const theme = urlParams.get('theme');
    const backgroundElement = document.getElementById('background-image-1');
    let welcomeText;

    switch (theme) {
        case 'tourism':
            backgroundElement.className = 'background background-image-1';
            welcomeText = "Bonjour, <br><br>Je suis votre guide touristique virtuel pour Montpellier. <br><br>N'hésitez pas à me poser des questions pour planifier votre visite dans n'importe quelle langue.!";
            break;
        case 'charity':
            backgroundElement.className = 'background background-image-2';
            welcomeText = "Bonjour, <br><br>Si vous avez besoin d'aide ou de ressources fournies par des organisations caritatives, n'hésitez pas à me demander dans n'importe quelle langue.";
            break;
        default:
            backgroundElement.className = 'background background-image-3';
            welcomeText = "Bonjour, <br><br>Je suis votre assistant personnel à Montpellier. <br><br>N'hésitez pas à me poser des questions dans n'importe quelle langue.";
    }

    showWelcomeMessage(welcomeText);
}


function showWelcomeMessage(welcomeText) {
    const loadingElement = appendLoadingSpinner();

    setTimeout(() => {
        messageList.removeChild(loadingElement);
        appendMessage(welcomeText, 'bot');
        scrollToMessage(messageList.lastChild);
    }, 2500);
}


function clearInput() {
    messageInput.value = '';
}
// endregion UI Updates


// region Network Requests
function sendUserMessage(messageText) {
    const userInfo = getUserInfo(messageText);
    const theme = new URLSearchParams(window.location.search).get('theme');
    userInfo.theme = theme;

    if (lastUserMessage && lastBotResponse) {
        userInfo.context = {
            lastUserMessage,
            lastBotResponse
        };
    }

    const loadingElement = appendLoadingSpinner();
    return fetch('https://neuronalnid.com/api/send_message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userInfo)
    })
        .then(response => response.json())
        .then(data => {
            handleBotResponse(data);
            return data;
        })
        .finally(() => {
            messageList.removeChild(loadingElement);
            lastUserMessage = messageText;
        });
}
// endregion Network Requests


// region Setup
document.addEventListener('DOMContentLoaded', function() {
    applyBackgroundTheme();
    updateCharactersLeft();
    messageInput.addEventListener('input', updateCharactersLeft);
});


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
// endregion Setup


init();
