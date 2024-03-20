

// region DOMContentLoaded
// document.addEventListener("DOMContentLoaded", function() {
//     var form = document.getElementById('new-message-form');
//     var input = document.getElementById('new-message-input');
//
//     if (/iPhone/i.test(navigator.userAgent)) {
//         if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
//
//
//             form.style.backgroundColor = "rgb(55,55,55)";
//             input.style.backgroundColor = "rgb(77,77,77)";
//             input.style.color = "rgb(255,255,255)";
//             input.style.borderColor = "rgb(90,90,90)";
//         } else {
//             form.style.backgroundColor = "rgb(239,240,245)";
//             input.style.backgroundColor = "rgb(255,255,255)";
//             input.style.color = "rgb(0,0,0)";
//             input.style.borderColor = "rgb(200,200,200)";
//         }
//     }
// });
// endregion DOMContentLoaded


// region Copy Email Functionality
var notificationActive = false;

document.getElementById('emailToCopy').onclick = function() {

    if (notificationActive) return;

    notificationActive = true;

    var email = 'neuronalnid@gmail.com';
    var el = document.createElement('textarea');
    el.value = email;
    el.setAttribute('readonly', '');
    el.style.position = 'absolute';
    el.style.left = '-9999px';
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);

    var emailElement = document.getElementById('emailToCopy');
    emailElement.style.color = '#21c0c5';
    setTimeout(function() {
        emailElement.style.color = 'rgba(41,213,218,0.8)';
    }, 200);

    var notification = document.getElementById('copyNotification');
    notification.style.display = 'block';
    notification.style.opacity = '1';
    setTimeout(function() {
        notification.style.opacity = '0';
        setTimeout(function() {
            notification.style.display = 'none';
            notificationActive = false;
        }, 500);
    }, 300);
};
// endregion Copy Email Functionality


// region Form Height Adjustment
function updateFormHeight() {
    const formHeight = document.getElementById('new-message-form').offsetHeight;
    document.documentElement.style.setProperty('--form-height', `${formHeight}px`);
}

window.onload = function() {
    updateFormHeight();
    setTimeout(() => {
        window.scrollTo(0, 0);
    }, 100);
};
window.onresize = updateFormHeight;
// endregion Form Height Adjustment


// region Smooth Scrolling for Navigation Links
document.querySelectorAll('nav a').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const targetId = e.target.getAttribute('href');
        const targetElement = document.querySelector(targetId);

        const offsetTop = targetElement.offsetTop - 75;

        window.scrollTo({
            top: offsetTop,
            behavior: 'smooth'
        });
    });
});
// endregion Smooth Scrolling for Navigation Links


// region Message Submission and Response Handling
const links = {
    'chat-link': 'chat-container',
    'teams-link': 'teams',
    'about-link': 'about-us',
    'contact-link': 'contacts',
};

document.getElementById('new-message-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const messageInput = document.getElementById('new-message-input');
    const sendButton = document.getElementById('send-message-button');
    const messageText = messageInput.value.trim();
    const messageList = document.getElementById('message-list');

    if (messageText) {
        sendButton.disabled = true;
        messageInput.value = '';

        const userMessageElement = document.createElement('div');
        userMessageElement.classList.add('message', 'user');
        userMessageElement.innerHTML = `<div class="text">${messageText}</div>`;
        messageList.appendChild(userMessageElement);
        const messageListRect = messageList.getBoundingClientRect();
        const userMessageRect = userMessageElement.getBoundingClientRect();
        const scrollOffset = userMessageRect.top - messageListRect.top + messageList.scrollTop;
        messageList.scrollTo({ top: scrollOffset, behavior: 'smooth' });

        setTimeout(() => {
            window.scrollTo({
                top: messageList.offsetTop,
                behavior: 'smooth'
            });
        }, 100);

        const loadingElement = document.createElement('div');
        loadingElement.classList.add('loading-spinner');
        messageList.appendChild(loadingElement);


        fetch('https://neuronalnid.com/api/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({message: messageText}),
        })

            .then(response => response.json())
            .then(data => {

                messageList.removeChild(loadingElement);

                const botMessageElement = document.createElement('div');
                botMessageElement.classList.add('message', 'bot');
                botMessageElement.innerHTML = `<div class="text">${data.reply}</div>`;

                messageList.appendChild(botMessageElement);
                const messageListRect = messageList.getBoundingClientRect();
                const messageRect = botMessageElement.getBoundingClientRect();
                const scrollOffset = messageRect.top - messageListRect.top + messageList.scrollTop;
                messageList.scrollTo({ top: scrollOffset, behavior: 'smooth' });
                const lastUserMessage = messageList.querySelector('.message.user:last-of-type');
                if (lastUserMessage) {
                    setTimeout(() => {
                        lastUserMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }, 100);
                }

                sendButton.disabled = false;
            })
            .catch((error) => {
                console.error('Error:', error);
                messageList.removeChild(loadingElement);
                sendButton.disabled = false;


                const errorBotMessageElement = document.createElement('div');
                errorBotMessageElement.classList.add('message', 'bot');
                errorBotMessageElement.innerHTML = `<div class="text">Sorry, I'm still in maintenance for a while...</div>`;
                messageList.appendChild(errorBotMessageElement);
                errorBotMessageElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
    }
});
// endregion Message Submission and Response Handling
