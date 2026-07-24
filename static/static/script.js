const heartsContainer = document.getElementById('hearts');
for (let i = 0; i < 35; i++) {
    const heart = document.createElement('div');
    heart.className = 'heart-float';
    heart.textContent = ['❤️', '💕', '💖', '✨', '🌸', '🌹'][Math.floor(Math.random() * 6)];
    heart.style.left = Math.random() * 100 + '%';
    heart.style.fontSize = (12 + Math.random() * 24) + 'px';
    heart.style.animationDuration = (12 + Math.random() * 20) + 's';
    heart.style.animationDelay = (Math.random() * 15) + 's';
    heartsContainer.appendChild(heart);
}

const msgInput = document.getElementById('msgInput');
const nameInput = document.getElementById('nameInput');
const sendBtn = document.getElementById('sendBtn');
const messagesDiv = document.getElementById('messages');

function addMessage(name, text, time) {
    const div = document.createElement('div');
    div.className = 'message love';
    div.innerHTML = `
        <span class="name">${name} ❤️</span>
        <span class="text">${text}</span>
        <span class="time">${time || 'همین الان'}</span>
    `;
    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

sendBtn.addEventListener('click', sendMessage);
msgInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendMessage();
});

function sendMessage() {
    const msg = msgInput.value.trim();
    const name = nameInput.value.trim() || 'عاشق';
    if (!msg) return;
    const now = new Date();
    const time = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');
    addMessage(name, msg, time);
    fetch('/api/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, message: msg })
    }).then(() => {
        msgInput.value = '';
        msgInput.focus();
    }).catch(() => {});
}

fetch('/api/messages')
    .then(r => r.json())
    .then(data => {
        data.forEach(m => {
            addMessage(m.name, m.message, m.time);
        });
    });
