document.getElementById('login-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const data = {
        email: email,
        password: password
    };

    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Ошибка от сервера:', errorData);
            alert('Ошибка: ' + (errorData.detail || 'Ошибка входа'));
            return;
        }

        const result = await response.json();
        window.location.href = '/messages';
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка: ' + error.message);
    }
});
