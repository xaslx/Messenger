let socket;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
const reconnectInterval = 2000;

document.addEventListener("DOMContentLoaded", function() {
    const userCards = document.querySelectorAll('.user-card');
    userCards.forEach(card => {
        card.classList.remove('selected');
    });
});

function openDialog(element) {
    const userCards = document.querySelectorAll('.user-card');
    userCards.forEach(card => {
        card.classList.remove('selected');
    });

    element.classList.add('selected');
    const newUserId = element.getAttribute('data-id');

    connectWebSocket(newUserId);
    
    fetch(`/messages/${newUserId}`)
        .then(response => response.json())
        .then(data => {
            const dialogContainer = document.querySelector('.dialog-container');
            dialogContainer.innerHTML = '';

            const dialogContent = `
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
                <h2>
                    Диалог с ${data.partner.name} ${data.partner.surname}
                    <span style="color: ${data.partner.is_online ? 'green' : 'red'};">
                        (${data.partner.is_online ? 'В сети' : 'Не в сети'})
                    </span>
                </h2>
                <div class="messages">
                    ${data.messages.map(message => `
                        <div class="message ${message.senderId === data.user.id ? 'sender' : 'receiver'}">
                            <strong>${message.senderId === data.user.id ? 'Вы' : message.senderName}:</strong> ${message.text}
                            <div class="message-timestamp" style="color: rgb(91, 89, 89); font-size: 0.9em;">
                                ${message.timestamp}
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div style="display: flex; align-items: center;">
                    <label for="fileInput" class="file-label">
                        <i class="fas fa-paperclip"></i> <!-- Иконка скрепки -->
                    </label>
                    <input type="file" id="fileInput" class="file-input" />
                    <input type="text" placeholder="Введите сообщение..." id="messageInput" />
                    <button class="btn-send" onclick="sendMessage(${newUserId})">Отправить</button>
                </div>
            `;
            dialogContainer.innerHTML = dialogContent;

            const messagesContainer = dialogContainer.querySelector('.messages');
            messagesContainer.scrollTop = messagesContainer.scrollHeight;

            const sidebar = document.querySelector('.sidebar');
            sidebar.classList.add('hide');
            const dialogContainerMobile = document.querySelector('.dialog-container');
            dialogContainerMobile.classList.add('show');
            messageInput.addEventListener('keydown', (event) => {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    sendMessage(newUserId);
                }
            });
        })
        .catch(error => console.error('Ошибка:', error));
}

function connectWebSocket(userId) {
    if (socket) {
        socket.close();
        console.log('Предыдущее соединение закрыто');
    }
    socket = new WebSocket(`wss://messenger-hefw.onrender.com/ws/messages/${userId}`);

    socket.onopen = () => {
        console.log(`WebSocket соединение установлено для пользователя ${userId}`);
        reconnectAttempts = 0;
    };

    socket.onmessage = (event) => {
        const incomingMessage = JSON.parse(event.data);
        if (incomingMessage.recipient_id === currentUserId || incomingMessage.sender_id === currentUserId) {
            addMessageToDialog(incomingMessage);
        }
    };

    socket.onclose = () => {
        console.log('WebSocket соединение закрыто');
        attemptReconnect(userId);
    };

    socket.onerror = (error) => {
        console.error('Ошибка WebSocket:', error);
        attemptReconnect(userId);
    };
}

function attemptReconnect(userId) {
    if (reconnectAttempts < maxReconnectAttempts) {
        reconnectAttempts++;
        console.log(`Попытка переподключения (${reconnectAttempts}/${maxReconnectAttempts}) через ${reconnectInterval / 1000} секунд...`);
        setTimeout(() => connectWebSocket(userId), reconnectInterval);
    } else {
        console.log('Превышено количество попыток переподключения.');
    }
}

function sendMessage(recipientId) {
    const messageInput = document.querySelector('.dialog-container input[type="text"]');
    const messageContent = messageInput.value;

    if (messageContent.trim() === '') {
        return;
    }

    const message = {
        content: messageContent,
        recipient_id: recipientId
    };

    fetch('/messages', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(message)
    })
    .then(response => response.json())
    .then(data => {
        addMessageToDialog(data);
        messageInput.value = '';
        if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify(data));
        } else {
            console.log('Сообщение не может быть отправлено, WebSocket не открыт.');
        }
    })
    .catch(error => console.error('Ошибка:', error));
}

function addMessageToDialog(message) {
    const dialogContainer = document.querySelector('.dialog-container .messages');
    const messageElement = document.createElement('div');

    const isSender = message.sender_id === currentUserId;
    messageElement.className = `message ${isSender ? 'sender' : 'receiver'}`;
    messageElement.innerHTML = `
        <strong>${isSender ? 'Вы' : message.sender_name}:</strong> ${message.content}
        <div class="message-timestamp" style="color: rgb(91, 89, 89); font-size: 0.9em;">
            ${message.timestamp}
        </div>
    `;
    dialogContainer.appendChild(messageElement);
    dialogContainer.scrollTop = dialogContainer.scrollHeight;
}
