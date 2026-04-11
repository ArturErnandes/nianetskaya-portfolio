function setCreateWorkStatus(message, isSuccess = false) {
    const statusElement = document.querySelector("[data-create-work-status]");

    if (!statusElement) {
        return;
    }

    statusElement.textContent = message;
    statusElement.classList.toggle("is-hidden", !message);
    statusElement.classList.toggle("is-success", Boolean(message) && isSuccess);
}

function populateSections() {
    const sectionSelect = document.querySelector("[data-section-select]");

    if (!(sectionSelect instanceof HTMLSelectElement) || typeof SECTIONS_CONFIG !== "object" || SECTIONS_CONFIG === null) {
        return;
    }

    const options = Object.entries(SECTIONS_CONFIG).map(([slug, section]) => {
        const option = document.createElement("option");
        option.value = slug;
        option.textContent = section.heading;
        return option;
    });

    sectionSelect.replaceChildren(...options);
}

async function handleCreateWorkSubmit(event) {
    event.preventDefault();

    const form = event.currentTarget;
    const submitButton = form.querySelector(".create-work-submit");

    if (!(form instanceof HTMLFormElement) || !(submitButton instanceof HTMLButtonElement)) {
        return;
    }

    const formData = new FormData(form);
    const image = formData.get("image");

    if (!(image instanceof File) || image.size === 0) {
        setCreateWorkStatus("Выберите изображение");
        return;
    }

    setCreateWorkStatus("");
    submitButton.disabled = true;

    try {
        const response = await fetch("/api/works/create", {
            method: "POST",
            body: formData,
        });

        if (response.status === 401) {
            window.location.assign("/admin/login");
            return;
        }

        if (!response.ok) {
            setCreateWorkStatus("Не удалось сохранить работу");
            return;
        }

        form.reset();
        populateSections();
        setCreateWorkStatus("Работа успешно сохранена", true);
    } catch (error) {
        console.error("Ошибка при создании работы:", error);
        setCreateWorkStatus("Ошибка сети. Попробуйте еще раз");
    } finally {
        submitButton.disabled = false;
    }
}

function initAdminCreateWorkPage() {
    if (document.body.dataset.page !== "admin-create-work") {
        return;
    }

    const form = document.querySelector("[data-create-work-form]");

    if (!(form instanceof HTMLFormElement)) {
        return;
    }

    populateSections();
    setCreateWorkStatus("");
    form.addEventListener("submit", handleCreateWorkSubmit);
}

initAdminCreateWorkPage();
