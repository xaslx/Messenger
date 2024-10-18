let socket;


function openDialog(element) {
    const newUserId = element.getAttribute('data-id');

 
    if (socket) {
        socket.close();
        console.log('Предыдущее соединение закрыто');
    }

    socket = new WebSocket(`ws://127.0.0.1:8000/ws/messages/${newUserId}`);

    socket.onopen = () => {
        console.log(`WebSocket соединение установлено для пользователя ${newUserId}`);
    };
    
    socket.onmessage = (event) => {
        const incomingMessage = JSON.parse(event.data);
        console.log(incomingMessage);
        if (incomingMessage.recipient_id === currentUserId || incomingMessage.sender_id === currentUserId) {
            addMessageToDialog(incomingMessage);
        }
    };
    
    

    socket.onclose = () => console.log('WebSocket соединение закрыто');
    
 
    fetch(`/messages/${newUserId}`)
        .then(response => response.json())
        .then(data => {
            const dialogContainer = document.querySelector('.dialog-container');
            dialogContainer.innerHTML = '';
            console.log(data);
            const dialogContent = `
                <h2>Диалог с ${data.partner.name} ${data.partner.surname} (${data.partner.is_online})</h2>
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
                <input type="text" placeholder="Введите сообщение..." id="messageInput" />
                <button onclick="sendMessage(${newUserId})">Отправить</button>
            `;
            dialogContainer.innerHTML = dialogContent;
            const messagesContainer = dialogContainer.querySelector('.messages');
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            const messageInput = document.querySelector('.dialog-container input[type="text"]');
            messageInput.addEventListener('keydown', (event) => {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    sendMessage(newUserId);
                }
            });
        })
        .catch(error => console.error('Ошибка:', error));
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
 
        socket.send(JSON.stringify(data));
 
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
