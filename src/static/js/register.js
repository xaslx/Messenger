document.getElementById('registration-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const data = {
        name: document.getElementById('first_name').value,
        surname: document.getElementById('last_name').value,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
    };

    try {
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка регистрации');
        }

        const result = await response.json();
        console.log('Пользователь зарегистрирован:', result);
        window.location.href = '/auth/after_register';
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка: ' + error.message);
    }
});
