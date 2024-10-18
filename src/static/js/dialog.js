function openDialog(element) {

    const userId = element.getAttribute('data-id');

 
    fetch(`/dialogs/${userId}`)
        .then(response => response.json())
        .then(data => {

            const dialogContainer = document.querySelector('.dialog-container');
            dialogContainer.innerHTML = '';

            const dialogContent = `
                <h2>Диалог с ${data.user.name} ${data.user.surname}</h2>
                <div class="messages">
                    ${data.messages.map(message => `
                        <div class="message">
                            <strong>${message.senderName}:</strong> ${message.text}
                        </div>
                    `).join('')}
                </div>
                <input type="text" placeholder="Введите сообщение..." />
                <button onclick="sendMessage(${userId})">Отправить</button>
            `;
            dialogContainer.innerHTML = dialogContent;
        })
        .catch(error => console.error('Ошибка:', error));
}
