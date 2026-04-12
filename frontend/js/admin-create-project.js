function setCreateProjectStatus(message, isSuccess = false) {
    const statusElement = document.querySelector("[data-create-project-status]");

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

function addProjectImageForm() {
    const template = document.querySelector("[data-project-image-template]");
    const list = document.querySelector("[data-project-gallery-list]");

    if (!(template instanceof HTMLTemplateElement) || !(list instanceof HTMLElement)) {
        return;
    }

    const fragment = template.content.cloneNode(true);
    const item = fragment.querySelector(".project-gallery-item-form");
    const removeButton = fragment.querySelector(".project-gallery-remove");

    if (item instanceof HTMLElement && removeButton instanceof HTMLButtonElement) {
        removeButton.addEventListener("click", () => {
            item.remove();
        });
    }

    list.append(fragment);
}

async function handleCreateProjectSubmit(event) {
    event.preventDefault();

    const form = event.currentTarget;
    const submitButton = form.querySelector(".create-work-submit");

    if (!(form instanceof HTMLFormElement) || !(submitButton instanceof HTMLButtonElement)) {
        return;
    }

    const formData = new FormData(form);
    const coverImage = formData.get("cover_image");

    if (!(coverImage instanceof File) || coverImage.size === 0) {
        setCreateProjectStatus("Выберите обложку проекта");
        return;
    }

    setCreateProjectStatus("");
    submitButton.disabled = true;

    try {
        const response = await fetch("/api/projects/create", {
            method: "POST",
            body: formData,
        });

        if (response.status === 401) {
            window.location.assign("/admin/login");
            return;
        }

        if (!response.ok) {
            setCreateProjectStatus("Не удалось сохранить проект");
            return;
        }

        form.reset();
        populateSections();
        const list = document.querySelector("[data-project-gallery-list]");
        if (list instanceof HTMLElement) {
            list.replaceChildren();
        }
        setCreateProjectStatus("Проект успешно сохранен", true);
    } catch (error) {
        console.error("Ошибка при создании проекта:", error);
        setCreateProjectStatus("Ошибка сети. Попробуйте еще раз");
    } finally {
        submitButton.disabled = false;
    }
}

function initAdminCreateProjectPage() {
    if (document.body.dataset.page !== "admin-create-project") {
        return;
    }

    const form = document.querySelector("[data-create-project-form]");
    const addButton = document.querySelector("[data-add-project-image]");

    if (!(form instanceof HTMLFormElement) || !(addButton instanceof HTMLButtonElement)) {
        return;
    }

    populateSections();
    setCreateProjectStatus("");
    addButton.addEventListener("click", addProjectImageForm);
    form.addEventListener("submit", handleCreateProjectSubmit);
}

initAdminCreateProjectPage();
