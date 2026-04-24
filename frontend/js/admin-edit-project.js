function setEditProjectStatus(message, isSuccess = false) {
    const statusElement = document.querySelector("[data-edit-project-status]");

    if (!statusElement) {
        return;
    }

    statusElement.textContent = message;
    statusElement.classList.toggle("is-hidden", !message);
    statusElement.classList.toggle("is-success", Boolean(message) && isSuccess);
}

function setGalleryStatus(item, message, isSuccess = false) {
    const statusElement = item.querySelector("[data-gallery-status]");

    if (!(statusElement instanceof HTMLElement)) {
        return;
    }

    statusElement.textContent = message;
    statusElement.classList.toggle("is-hidden", !message);
    statusElement.classList.toggle("is-success", Boolean(message) && isSuccess);
}

let projectCoverObjectUrl = null;
const projectGalleryPreviewUrls = new Map();
let currentProjectCoverName = null;
let nextGalleryOrderIndex = 1;

function getProjectIdFromPath() {
    const match = window.location.pathname.match(/\/admin\/edit-project\/(\d+)\/?$/);
    return match ? Number(match[1]) : null;
}

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

function showProjectCover(source) {
    const image = document.querySelector("[data-project-cover-preview]");

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

function updateProjectCoverPreview(form) {
    const coverInput = form.elements.namedItem("cover_image");
    const file = coverInput instanceof HTMLInputElement && coverInput.files ? coverInput.files[0] : null;

    revokeProjectCoverUrl();

    if (file instanceof File && file.size > 0) {
        projectCoverObjectUrl = URL.createObjectURL(file);
        showProjectCover(projectCoverObjectUrl);
        return;
    }

    if (currentProjectCoverName) {
        showProjectCover(`${WORKS_ASSETS_PATH}/${currentProjectCoverName}`);
    }
}

function updateGalleryImagePreview(input) {
    const item = input.closest("[data-new-project-image]");

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

function fillEditProjectForm(form, project) {
    const title = form.elements.namedItem("title");
    const caption = form.elements.namedItem("caption");
    const description = form.elements.namedItem("description");

    if (title instanceof HTMLInputElement) {
        title.value = project.title || "";
    }

    if (caption instanceof HTMLTextAreaElement) {
        caption.value = project.caption || "";
    }

    if (description instanceof HTMLTextAreaElement) {
        description.value = project.description || "";
    }

    currentProjectCoverName = project.cover_img_name || null;

    if (currentProjectCoverName) {
        showProjectCover(`${WORKS_ASSETS_PATH}/${currentProjectCoverName}`);
    }
}

function createExistingProjectImageItem(imageData) {
    const template = document.querySelector("[data-project-existing-image-template]");

    if (!(template instanceof HTMLTemplateElement)) {
        return null;
    }

    const fragment = template.content.cloneNode(true);
    const item = fragment.querySelector("[data-project-image-item]");
    const image = fragment.querySelector("[data-gallery-image-preview]");
    const description = fragment.querySelector("[data-gallery-description]");

    if (!(item instanceof HTMLElement) || !(image instanceof HTMLImageElement) || !(description instanceof HTMLTextAreaElement)) {
        return null;
    }

    item.dataset.imageId = String(imageData.image_id);
    item.dataset.orderIndex = String(imageData.order_index);
    image.src = `${WORKS_ASSETS_PATH}/${imageData.img_name}`;
    image.classList.add("is-visible");
    description.value = imageData.description || "";

    const media = image.closest(".editor-media");

    if (media instanceof HTMLElement) {
        media.classList.add("is-has-image");
    }

    return item;
}

function renderProjectImages(images) {
    const galleryList = document.querySelector("[data-project-gallery-list]");

    if (!(galleryList instanceof HTMLElement)) {
        return;
    }

    const items = images
        .map(createExistingProjectImageItem)
        .filter((item) => item instanceof HTMLElement);

    galleryList.replaceChildren(...items);
    nextGalleryOrderIndex = images.reduce((maxIndex, image) => Math.max(maxIndex, image.order_index || 0), 0) + 1;
}

function createNewProjectImageItem() {
    const template = document.querySelector("[data-project-new-image-template]");

    if (!(template instanceof HTMLTemplateElement)) {
        return null;
    }

    const fragment = template.content.cloneNode(true);
    const item = fragment.querySelector("[data-new-project-image]");

    if (!(item instanceof HTMLElement)) {
        return null;
    }

    item.dataset.orderIndex = String(nextGalleryOrderIndex);
    nextGalleryOrderIndex += 1;

    return item;
}

async function loadEditableProject(form, projectId) {
    setEditProjectStatus("Загрузка проекта...");

    try {
        const response = await fetch(`/api/admin/projects/${projectId}`);

        if (response.status === 401) {
            window.location.assign("/admin/login");
            return;
        }

        if (response.status === 404) {
            setEditProjectStatus("Проект не найден");
            return;
        }

        if (!response.ok) {
            setEditProjectStatus("Не удалось загрузить проект");
            return;
        }

        const project = await response.json();

        populateSections(project.section_name);
        fillEditProjectForm(form, project);
        renderProjectImages(Array.isArray(project.images) ? project.images : []);
        setEditProjectStatus("");
    } catch (error) {
        console.error("Ошибка при загрузке проекта для редактирования:", error);
        setEditProjectStatus("Ошибка сети. Попробуйте еще раз");
    }
}

async function handleEditProjectSubmit(event) {
    event.preventDefault();

    const form = event.currentTarget;
    const submitButton = form.querySelector(".create-work-submit");
    const projectId = getProjectIdFromPath();

    if (!(form instanceof HTMLFormElement) || !(submitButton instanceof HTMLButtonElement) || !projectId) {
        return;
    }

    const formData = new FormData(form);
    const coverImage = formData.get("cover_image");

    formData.delete("new_gallery_image");

    if (!(coverImage instanceof File) || coverImage.size === 0) {
        formData.delete("cover_image");
    }

    setEditProjectStatus("");
    submitButton.disabled = true;

    try {
        const response = await fetch(`/api/admin/projects/${projectId}`, {
            method: "PATCH",
            body: formData,
        });

        if (response.status === 401) {
            window.location.assign("/admin/login");
            return;
        }

        if (response.status === 404) {
            setEditProjectStatus("Проект не найден");
            return;
        }

        if (!response.ok) {
            setEditProjectStatus("Не удалось сохранить изменения");
            return;
        }

        const coverWasChanged = coverImage instanceof File && coverImage.size > 0;
        const coverInput = form.elements.namedItem("cover_image");

        if (coverInput instanceof HTMLInputElement) {
            coverInput.value = "";
        }

        if (coverWasChanged) {
            await loadEditableProject(form, projectId);
        }

        setEditProjectStatus("Изменения сохранены", true);
    } catch (error) {
        console.error("Ошибка при сохранении проекта:", error);
        setEditProjectStatus("Ошибка сети. Попробуйте еще раз");
    } finally {
        submitButton.disabled = false;
    }
}

async function saveExistingProjectImage(item) {
    const imageId = Number(item.dataset.imageId);
    const orderIndex = Number(item.dataset.orderIndex);
    const description = item.querySelector("[data-gallery-description]");
    const saveButton = item.querySelector("[data-save-project-image]");

    if (!imageId || !orderIndex || !(description instanceof HTMLTextAreaElement) || !(saveButton instanceof HTMLButtonElement)) {
        return;
    }

    const formData = new FormData();
    formData.set("description", description.value);
    formData.set("order_index", String(orderIndex));
    saveButton.disabled = true;
    setGalleryStatus(item, "");

    try {
        const response = await fetch(`/api/admin/project-images/${imageId}`, {
            method: "PATCH",
            body: formData,
        });

        if (response.status === 401) {
            window.location.assign("/admin/login");
            return;
        }

        if (!response.ok) {
            setGalleryStatus(item, "Не удалось сохранить описание");
            return;
        }

        setGalleryStatus(item, "Описание сохранено", true);
    } catch (error) {
        console.error("Ошибка при сохранении изображения проекта:", error);
        setGalleryStatus(item, "Ошибка сети. Попробуйте еще раз");
    } finally {
        saveButton.disabled = false;
    }
}

async function deleteExistingProjectImage(item) {
    const imageId = Number(item.dataset.imageId);
    const deleteButton = item.querySelector("[data-delete-project-image]");

    if (!imageId || !(deleteButton instanceof HTMLButtonElement)) {
        return;
    }

    deleteButton.disabled = true;
    setGalleryStatus(item, "");

    try {
        const response = await fetch(`/api/admin/project-images/${imageId}`, {
            method: "DELETE",
        });

        if (response.status === 401) {
            window.location.assign("/admin/login");
            return;
        }

        if (!response.ok) {
            setGalleryStatus(item, "Не удалось удалить изображение");
            return;
        }

        item.remove();
    } catch (error) {
        console.error("Ошибка при удалении изображения проекта:", error);
        setGalleryStatus(item, "Ошибка сети. Попробуйте еще раз");
    } finally {
        deleteButton.disabled = false;
    }
}

async function createProjectImage(item) {
    const projectId = getProjectIdFromPath();
    const imageInput = item.querySelector('input[name="new_gallery_image"]');
    const description = item.querySelector("[data-gallery-description]");
    const saveButton = item.querySelector("[data-create-project-image]");
    const file = imageInput instanceof HTMLInputElement && imageInput.files ? imageInput.files[0] : null;

    if (!projectId || !(description instanceof HTMLTextAreaElement) || !(saveButton instanceof HTMLButtonElement)) {
        return;
    }

    if (!(file instanceof File) || file.size === 0) {
        setGalleryStatus(item, "Выберите изображение");
        return;
    }

    const formData = new FormData();
    formData.set("image", file);
    formData.set("description", description.value);
    formData.set("order_index", item.dataset.orderIndex || String(nextGalleryOrderIndex));
    saveButton.disabled = true;
    setGalleryStatus(item, "");

    try {
        const response = await fetch(`/api/admin/projects/${projectId}/images`, {
            method: "POST",
            body: formData,
        });

        if (response.status === 401) {
            window.location.assign("/admin/login");
            return;
        }

        if (!response.ok) {
            setGalleryStatus(item, "Не удалось сохранить изображение");
            return;
        }

        const form = document.querySelector("[data-edit-project-form]");

        if (form instanceof HTMLFormElement) {
            await loadEditableProject(form, projectId);
        }

        setEditProjectStatus("Изображение добавлено", true);
    } catch (error) {
        console.error("Ошибка при добавлении изображения проекта:", error);
        setGalleryStatus(item, "Ошибка сети. Попробуйте еще раз");
    } finally {
        saveButton.disabled = false;
    }
}

function removeNewProjectImage(item) {
    const imageInput = item.querySelector('input[name="new_gallery_image"]');

    if (imageInput instanceof HTMLInputElement) {
        revokeGalleryPreviewForInput(imageInput);
    }

    item.remove();
}

function initProjectDropzones(form) {
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
}

function initGalleryActions(galleryList) {
    galleryList.addEventListener("click", (event) => {
        const target = event.target;

        if (!(target instanceof HTMLElement)) {
            return;
        }

        const existingItem = target.closest("[data-project-image-item]");
        const newItem = target.closest("[data-new-project-image]");

        if (target.closest("[data-save-project-image]") && existingItem instanceof HTMLElement) {
            void saveExistingProjectImage(existingItem);
            return;
        }

        if (target.closest("[data-delete-project-image]") && existingItem instanceof HTMLElement) {
            void deleteExistingProjectImage(existingItem);
            return;
        }

        if (target.closest("[data-create-project-image]") && newItem instanceof HTMLElement) {
            void createProjectImage(newItem);
            return;
        }

        if (target.closest("[data-remove-new-project-image]") && newItem instanceof HTMLElement) {
            removeNewProjectImage(newItem);
        }
    });
}

function initAdminEditProjectPage() {
    if (document.body.dataset.page !== "admin-edit-project") {
        return;
    }

    const form = document.querySelector("[data-edit-project-form]");
    const addButton = document.querySelector("[data-add-project-image]");
    const galleryList = document.querySelector("[data-project-gallery-list]");
    const projectId = getProjectIdFromPath();

    if (
        !(form instanceof HTMLFormElement) ||
        !(addButton instanceof HTMLButtonElement) ||
        !(galleryList instanceof HTMLElement) ||
        !projectId
    ) {
        setEditProjectStatus("Некорректный адрес страницы");
        return;
    }

    populateSections();
    initProjectDropzones(form);
    initGalleryActions(galleryList);
    void loadEditableProject(form, projectId);

    addButton.addEventListener("click", () => {
        const item = createNewProjectImageItem();

        if (item instanceof HTMLElement) {
            galleryList.append(item);
        }
    });

    form.addEventListener("change", (event) => {
        const target = event.target;

        if (!(target instanceof HTMLElement)) {
            return;
        }

        if (target instanceof HTMLInputElement && target.name === "cover_image") {
            updateProjectCoverPreview(form);
            return;
        }

        if (target instanceof HTMLInputElement && target.name === "new_gallery_image") {
            updateGalleryImagePreview(target);
        }
    });

    window.addEventListener("beforeunload", () => {
        revokeProjectCoverUrl();
        revokeAllGalleryPreviewUrls();
    });

    form.addEventListener("submit", handleEditProjectSubmit);
}

initAdminEditProjectPage();
