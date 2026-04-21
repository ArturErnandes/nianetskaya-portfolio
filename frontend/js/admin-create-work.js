function setCreateWorkStatus(message, isSuccess = false) {
    const statusElement = document.querySelector("[data-create-work-status]");

    if (!statusElement) {
        return;
    }

    statusElement.textContent = message;
    statusElement.classList.toggle("is-hidden", !message);
    statusElement.classList.toggle("is-success", Boolean(message) && isSuccess);
}

let workPreviewObjectUrl = null;

function revokeWorkPreviewUrl() {
    if (!workPreviewObjectUrl) {
        return;
    }

    URL.revokeObjectURL(workPreviewObjectUrl);
    workPreviewObjectUrl = null;
}

function getFirstImageFile(fileList) {
    if (!(fileList instanceof FileList)) {
        return null;
    }

    for (const file of fileList) {
        if (file instanceof File && file.type.startsWith("image/")) {
            return file;
        }
    }

    return null;
}

function assignFileToInput(input, file) {
    const transfer = new DataTransfer();
    transfer.items.add(file);
    input.files = transfer.files;
    input.dispatchEvent(new Event("change", { bubbles: true }));
}

function updateWorkImagePreview(form) {
    const image = document.querySelector("[data-work-image-preview]");

    if (!(image instanceof HTMLImageElement)) {
        return;
    }

    const media = image.closest(".editor-media");

    if (!(media instanceof HTMLElement)) {
        return;
    }

    revokeWorkPreviewUrl();

    const imageInput = form.elements.namedItem("image");
    const file = imageInput instanceof HTMLInputElement && imageInput.files ? imageInput.files[0] : null;

    if (file instanceof File && file.size > 0) {
        workPreviewObjectUrl = URL.createObjectURL(file);
        image.src = workPreviewObjectUrl;
        image.classList.add("is-visible");
        media.classList.add("is-has-image");
        return;
    }

    image.removeAttribute("src");
    image.classList.remove("is-visible");
    media.classList.remove("is-has-image");
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
        updateWorkImagePreview(form);
        setCreateWorkStatus("Работа успешно сохранена", true);
    } catch (error) {
        console.error("Ошибка при создании работы:", error);
        setCreateWorkStatus("Ошибка сети. Попробуйте еще раз");
    } finally {
        submitButton.disabled = false;
    }
}

function initWorkDropzone(form) {
    const media = form.querySelector("[data-file-dropzone]");

    if (!(media instanceof HTMLElement)) {
        return;
    }

    media.addEventListener("dragover", (event) => {
        event.preventDefault();
        event.dataTransfer.dropEffect = "copy";
        media.classList.add("is-dragover");
    });

    media.addEventListener("dragleave", () => {
        media.classList.remove("is-dragover");
    });

    media.addEventListener("drop", (event) => {
        event.preventDefault();
        media.classList.remove("is-dragover");

        const input = media.querySelector('input[name="image"]');

        if (!(input instanceof HTMLInputElement) || !event.dataTransfer) {
            return;
        }

        const droppedFile = getFirstImageFile(event.dataTransfer.files);

        if (!(droppedFile instanceof File)) {
            return;
        }

        assignFileToInput(input, droppedFile);
    });
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
    updateWorkImagePreview(form);
    initWorkDropzone(form);

    form.addEventListener("change", (event) => {
        const target = event.target;

        if (target instanceof HTMLInputElement && target.name === "image") {
            updateWorkImagePreview(form);
        }
    });

    window.addEventListener("beforeunload", revokeWorkPreviewUrl);
    form.addEventListener("submit", handleCreateWorkSubmit);
}

initAdminCreateWorkPage();
