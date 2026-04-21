function setCreateProjectStatus(message, isSuccess = false) {
    const statusElement = document.querySelector("[data-create-project-status]");

    if (!statusElement) {
        return;
    }

    statusElement.textContent = message;
    statusElement.classList.toggle("is-hidden", !message);
    statusElement.classList.toggle("is-success", Boolean(message) && isSuccess);
}

let projectCoverObjectUrl = null;
const projectGalleryPreviewUrls = new Map();

function revokeProjectCoverUrl() {
    if (!projectCoverObjectUrl) {
        return;
    }

    URL.revokeObjectURL(projectCoverObjectUrl);
    projectCoverObjectUrl = null;
}

function revokeGalleryPreviewForInput(input) {
    const existingUrl = projectGalleryPreviewUrls.get(input);

    if (!existingUrl) {
        return;
    }

    URL.revokeObjectURL(existingUrl);
    projectGalleryPreviewUrls.delete(input);
}

function revokeAllGalleryPreviewUrls() {
    projectGalleryPreviewUrls.forEach((url) => {
        URL.revokeObjectURL(url);
    });
    projectGalleryPreviewUrls.clear();
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

function updateProjectCoverPreview(form) {
    const image = document.querySelector("[data-project-cover-preview]");

    if (!(image instanceof HTMLImageElement)) {
        return;
    }

    const media = image.closest(".editor-media");

    if (!(media instanceof HTMLElement)) {
        return;
    }

    revokeProjectCoverUrl();

    const coverInput = form.elements.namedItem("cover_image");
    const file = coverInput instanceof HTMLInputElement && coverInput.files ? coverInput.files[0] : null;

    if (file instanceof File && file.size > 0) {
        projectCoverObjectUrl = URL.createObjectURL(file);
        image.src = projectCoverObjectUrl;
        image.classList.add("is-visible");
        media.classList.add("is-has-image");
        return;
    }

    image.removeAttribute("src");
    image.classList.remove("is-visible");
    media.classList.remove("is-has-image");
}

function updateGalleryImagePreview(input) {
    const item = input.closest(".project-gallery-item-form");

    if (!(item instanceof HTMLElement)) {
        return;
    }

    const image = item.querySelector("[data-gallery-image-preview]");

    if (!(image instanceof HTMLImageElement)) {
        return;
    }

    const media = image.closest(".editor-media");

    if (!(media instanceof HTMLElement)) {
        return;
    }

    revokeGalleryPreviewForInput(input);

    const file = input.files ? input.files[0] : null;

    if (file instanceof File && file.size > 0) {
        const objectUrl = URL.createObjectURL(file);
        projectGalleryPreviewUrls.set(input, objectUrl);

        image.src = objectUrl;
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

function addProjectImageForm() {
    const template = document.querySelector("[data-project-image-template]");
    const list = document.querySelector("[data-project-gallery-list]");

    if (!(template instanceof HTMLTemplateElement) || !(list instanceof HTMLElement)) {
        return;
    }

    const fragment = template.content.cloneNode(true);
    list.append(fragment);
}

function removeProjectImageForm(button) {
    const item = button.closest(".project-gallery-item-form");

    if (!(item instanceof HTMLElement)) {
        return;
    }

    const imageInput = item.querySelector('input[name="gallery_images"]');

    if (imageInput instanceof HTMLInputElement) {
        revokeGalleryPreviewForInput(imageInput);
    }

    item.remove();
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

        const galleryList = document.querySelector("[data-project-gallery-list]");

        form.reset();
        populateSections();
        revokeProjectCoverUrl();
        revokeAllGalleryPreviewUrls();

        if (galleryList instanceof HTMLElement) {
            galleryList.replaceChildren();
        }

        updateProjectCoverPreview(form);
        setCreateProjectStatus("Проект успешно сохранен", true);
    } catch (error) {
        console.error("Ошибка при создании проекта:", error);
        setCreateProjectStatus("Ошибка сети. Попробуйте еще раз");
    } finally {
        submitButton.disabled = false;
    }
}

function initProjectDropzones(form, galleryList) {
    form.addEventListener("dragover", (event) => {
        const target = event.target;

        if (!(target instanceof HTMLElement)) {
            return;
        }

        const dropzone = target.closest("[data-file-dropzone]");

        if (!(dropzone instanceof HTMLElement)) {
            return;
        }

        event.preventDefault();
        event.dataTransfer.dropEffect = "copy";
        dropzone.classList.add("is-dragover");
    });

    form.addEventListener("dragleave", (event) => {
        const target = event.target;

        if (!(target instanceof HTMLElement)) {
            return;
        }

        const dropzone = target.closest("[data-file-dropzone]");

        if (dropzone instanceof HTMLElement) {
            dropzone.classList.remove("is-dragover");
        }
    });

    form.addEventListener("drop", (event) => {
        const target = event.target;

        if (!(target instanceof HTMLElement)) {
            return;
        }

        const dropzone = target.closest("[data-file-dropzone]");

        if (!(dropzone instanceof HTMLElement) || !event.dataTransfer) {
            return;
        }

        event.preventDefault();
        dropzone.classList.remove("is-dragover");

        const input = dropzone.querySelector('input[type="file"]');

        if (!(input instanceof HTMLInputElement)) {
            return;
        }

        const droppedFile = getFirstImageFile(event.dataTransfer.files);

        if (!(droppedFile instanceof File)) {
            return;
        }

        assignFileToInput(input, droppedFile);
    });

    galleryList.addEventListener("click", (event) => {
        const target = event.target;

        if (!(target instanceof HTMLElement)) {
            return;
        }

        const removeButton = target.closest(".project-gallery-remove");

        if (removeButton instanceof HTMLButtonElement) {
            removeProjectImageForm(removeButton);
        }
    });
}

function initAdminCreateProjectPage() {
    if (document.body.dataset.page !== "admin-create-project") {
        return;
    }

    const form = document.querySelector("[data-create-project-form]");
    const addButton = document.querySelector("[data-add-project-image]");
    const galleryList = document.querySelector("[data-project-gallery-list]");

    if (
        !(form instanceof HTMLFormElement) ||
        !(addButton instanceof HTMLButtonElement) ||
        !(galleryList instanceof HTMLElement)
    ) {
        return;
    }

    populateSections();
    setCreateProjectStatus("");
    updateProjectCoverPreview(form);

    addButton.addEventListener("click", addProjectImageForm);

    form.addEventListener("change", (event) => {
        const target = event.target;

        if (!(target instanceof HTMLElement)) {
            return;
        }

        if (target instanceof HTMLInputElement && target.name === "cover_image") {
            updateProjectCoverPreview(form);
            return;
        }

        if (target instanceof HTMLInputElement && target.name === "gallery_images") {
            updateGalleryImagePreview(target);
        }
    });

    initProjectDropzones(form, galleryList);

    window.addEventListener("beforeunload", () => {
        revokeProjectCoverUrl();
        revokeAllGalleryPreviewUrls();
    });

    form.addEventListener("submit", handleCreateProjectSubmit);
}

initAdminCreateProjectPage();
