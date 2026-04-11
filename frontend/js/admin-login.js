function setLoginError(message) {
    const errorElement = document.querySelector("[data-login-error]");

    if (!errorElement) {
        return;
    }

    errorElement.textContent = message;
    errorElement.classList.toggle("is-hidden", !message);
}

async function handleLoginSubmit(event) {
    event.preventDefault();

    const form = event.currentTarget;
    const submitButton = form.querySelector(".login-submit");
    const passwordInput = form.querySelector('input[name="password"]');

    if (!(passwordInput instanceof HTMLInputElement) || !submitButton) {
        return;
    }

    const password = passwordInput.value.trim();

    if (!password) {
        setLoginError("Введите пароль");
        passwordInput.focus();
        return;
    }

    setLoginError("");
    submitButton.disabled = true;

    try {
        const response = await fetch("/api/admin/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ password }),
        });

        if (response.status === 401) {
            setLoginError("Неверный пароль");
            passwordInput.select();
            return;
        }

        if (!response.ok) {
            setLoginError("Не удалось выполнить вход");
            return;
        }

        window.location.assign("/admin/create-work");
    } catch (error) {
        console.error("Ошибка при авторизации:", error);
        setLoginError("Ошибка сети. Попробуйте еще раз");
    } finally {
        submitButton.disabled = false;
    }
}

function initAdminLoginPage() {
    if (document.body.dataset.page !== "admin-login") {
        return;
    }

    const form = document.querySelector("[data-login-form]");

    if (!(form instanceof HTMLFormElement)) {
        return;
    }

    setLoginError("");
    form.addEventListener("submit", handleLoginSubmit);
}

initAdminLoginPage();
