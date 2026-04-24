function setEditWorkStatus(message, isSuccess = false) {
    const statusElement = document.querySelector("[data-edit-work-status]");

    if (!statusElement) {
        return;
    }

    statusElement.textContent = message;
    statusElement.classList.toggle("is-hidden", !message);
    statusElement.classList.toggle("is-success", Boolean(message) && isSuccess);
}

let workPreviewObjectUrl = null;
let currentWorkImageName = null;

function getWorkIdFromPath() {
    const match = window.location.pathname.match(/\/admin\/edit-work\/(\d+)\/?$/);
    return match ? Number(match[1]) : null;
}

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

function populateSections(selectedSectionName = null) {
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

    if (selectedSectionName) {
        sectionSelect.value = selectedSectionName;
    }
}

function showWorkImage(source) {
    const image = document.querySelector("[data-work-image-preview]");

    if (!(image instanceof HTMLImageElement)) {
        return;
    }

    const media = image.closest(".editor-media");

    if (!(media instanceof HTMLElement)) {
        return;
    }

    image.src = source;
    image.classList.add("is-visible");
    media.classList.add("is-has-image");
}

function updateWorkImagePreview(form) {
    const imageInput = form.elements.namedItem("image");
    const file = imageInput instanceof HTMLInputElement && imageInput.files ? imageInput.files[0] : null;

    revokeWorkPreviewUrl();

    if (file instanceof File && file.size > 0) {
        workPreviewObjectUrl = URL.createObjectURL(file);
        showWorkImage(workPreviewObjectUrl);
        return;
    }

    if (currentWorkImageName) {
        showWorkImage(`${WORKS_ASSETS_PATH}/${currentWorkImageName}`);
    }
}

function fillEditWorkForm(form, work) {
    const title = form.elements.namedItem("title");
    const caption = form.elements.namedItem("caption");
    const description = form.elements.namedItem("description");

    if (title instanceof HTMLInputElement) {
        title.value = work.title || "";
    }

    if (caption instanceof HTMLTextAreaElement) {
        caption.value = work.caption || "";
    }

    if (description instanceof HTMLTextAreaElement) {
        description.value = work.description || "";
    }

    currentWorkImageName = work.img_name || null;

    if (currentWorkImageName) {
        showWorkImage(`${WORKS_ASSETS_PATH}/${currentWorkImageName}`);
    }
}

async function loadEditableWork(form, workId) {
    setEditWorkStatus("Загрузка работы...");

    try {
        const response = await fetch(`/api/admin/works/${workId}`);

        if (response.status === 401) {
            window.location.assign("/admin/login");
            return;
        }

        if (response.status === 404) {
            setEditWorkStatus("Работа не найдена");
            return;
        }

        if (!response.ok) {
            setEditWorkStatus("Не удалось загрузить работу");
            return;
        }

        const work = await response.json();

        populateSections(work.section_name);
        fillEditWorkForm(form, work);
        setEditWorkStatus("");
    } catch (error) {
        console.error("Ошибка при загрузке работы для редактирования:", error);
        setEditWorkStatus("Ошибка сети. Попробуйте еще раз");
    }
}

async function handleEditWorkSubmit(event) {
    event.preventDefault();

    const form = event.currentTarget;
    const submitButton = form.querySelector(".create-work-submit");
    const workId = getWorkIdFromPath();

    if (!(form instanceof HTMLFormElement) || !(submitButton instanceof HTMLButtonElement) || !workId) {
        return;
    }

    const formData = new FormData(form);
    const image = formData.get("image");

    if (!(image instanceof File) || image.size === 0) {
        formData.delete("image");
    }

    setEditWorkStatus("");
    submitButton.disabled = true;

    try {
        const response = await fetch(`/api/admin/works/${workId}`, {
            method: "PATCH",
            body: formData,
        });

        if (response.status === 401) {
            window.location.assign("/admin/login");
            return;
        }

        if (response.status === 404) {
            setEditWorkStatus("Работа не найдена");
            return;
        }

        if (!response.ok) {
            setEditWorkStatus("Не удалось сохранить изменения");
            return;
        }

        const imageInput = form.elements.namedItem("image");

        if (image instanceof File && image.size > 0) {
            currentWorkImageName = null;
            if (imageInput instanceof HTMLInputElement) {
                imageInput.value = "";
            }
        }

        setEditWorkStatus("Изменения сохранены", true);
    } catch (error) {
        console.error("Ошибка при сохранении работы:", error);
        setEditWorkStatus("Ошибка сети. Попробуйте еще раз");
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

function initAdminEditWorkPage() {
    if (document.body.dataset.page !== "admin-edit-work") {
        return;
    }

    const form = document.querySelector("[data-edit-work-form]");
    const workId = getWorkIdFromPath();

    if (!(form instanceof HTMLFormElement) || !workId) {
        setEditWorkStatus("Некорректный адрес страницы");
        return;
    }

    populateSections();
    initWorkDropzone(form);
    void loadEditableWork(form, workId);

    form.addEventListener("change", (event) => {
        const target = event.target;

        if (target instanceof HTMLInputElement && target.name === "image") {
            updateWorkImagePreview(form);
        }
    });

    window.addEventListener("beforeunload", revokeWorkPreviewUrl);
    form.addEventListener("submit", handleEditWorkSubmit);
}

initAdminEditWorkPage();
