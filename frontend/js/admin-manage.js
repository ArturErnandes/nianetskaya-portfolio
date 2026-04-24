function setManageStatus(message, isSuccess = false) {
    const statusElement = document.querySelector("[data-manage-status]");

    if (!statusElement) {
        return;
    }

    statusElement.textContent = message;
    statusElement.classList.toggle("is-hidden", !message);
    statusElement.classList.toggle("is-success", Boolean(message) && isSuccess);
}

function getThumbPathFromImageName(imageName) {
    const dotIndex = imageName.lastIndexOf(".");
    const baseName = dotIndex === -1 ? imageName : imageName.slice(0, dotIndex);
    return `${WORKS_THUMBS_PATH}/${baseName}.webp`;
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

function createManageItem(entity, editHref, isProject = false) {
    const item = document.createElement("li");
    const article = document.createElement("article");
    const media = document.createElement("div");
    const image = document.createElement("img");
    const body = document.createElement("div");
    const title = document.createElement("h2");
    const caption = document.createElement("p");
    const link = document.createElement("a");

    item.className = "manage-item";
    article.className = "manage-card";
    article.classList.toggle("is-project", isProject);
    media.className = "manage-card-media";
    body.className = "manage-card-body";
    link.className = "manage-card-action";

    image.src = getThumbPathFromImageName(entity.img_name);
    image.alt = entity.title;
    image.loading = "lazy";
    image.decoding = "async";
    image.addEventListener("error", () => {
        if (image.dataset.fallbackApplied === "1") {
            return;
        }

        image.dataset.fallbackApplied = "1";
        image.src = `${WORKS_ASSETS_PATH}/${entity.img_name}`;
    });

    title.textContent = entity.title;
    caption.textContent = entity.caption;
    link.href = editHref;
    link.textContent = "редактировать";

    media.append(image);
    body.append(title, caption, link);
    article.append(media, body);
    item.append(article);

    return item;
}

function createWorkManageItem(work) {
    return createManageItem(work, `/admin/edit-work/${work.id}`);
}

function createProjectManageItem(project) {
    return createManageItem(project, `/admin/edit-project/${project.id}`, true);
}

function renderEmptyState(listElement, message) {
    const item = document.createElement("li");
    const emptyState = document.createElement("p");

    item.className = "manage-empty-item";
    emptyState.className = "manage-empty";
    emptyState.textContent = message;
    item.append(emptyState);
    listElement.replaceChildren(item);
}

async function loadManageEntityList(sectionName, endpoint, listSelector, createItem, emptyMessage) {
    const listElement = document.querySelector(listSelector);

    if (!(listElement instanceof HTMLElement) || !sectionName) {
        return false;
    }

    setManageStatus("Загрузка...");

    try {
        const response = await fetch(`${endpoint}?section_name=${encodeURIComponent(sectionName)}`);

        if (response.status === 401) {
            window.location.assign("/admin/login");
            return false;
        }

        if (!response.ok) {
            renderEmptyState(listElement, "Не удалось загрузить список");
            return false;
        }

        const entities = await response.json();

        if (!Array.isArray(entities)) {
            renderEmptyState(listElement, "Некорректный ответ сервера");
            return false;
        }

        if (entities.length === 0) {
            renderEmptyState(listElement, emptyMessage);
            return true;
        }

        listElement.replaceChildren(...entities.map(createItem));
        return true;
    } catch (error) {
        console.error("Ошибка при загрузке списка для редактирования:", error);
        renderEmptyState(listElement, "Ошибка сети. Попробуйте еще раз");
        return false;
    }
}

async function loadManageEntities(sectionName) {
    setManageStatus("Загрузка...");

    const results = await Promise.all([
        loadManageEntityList(sectionName, API_ENDPOINTS.projects, "[data-projects-list]", createProjectManageItem, "В этой тематике пока нет проектов"),
        loadManageEntityList(sectionName, API_ENDPOINTS.works, "[data-works-list]", createWorkManageItem, "В этой тематике пока нет работ"),
    ]);

    setManageStatus(results.every(Boolean) ? "Список загружен" : "Список загружен не полностью", results.every(Boolean));
}

function initAdminManagePage() {
    if (document.body.dataset.page !== "admin-manage") {
        return;
    }

    const sectionSelect = document.querySelector("[data-section-select]");

    if (!(sectionSelect instanceof HTMLSelectElement)) {
        return;
    }

    populateSections();
    void loadManageEntities(sectionSelect.value);

    sectionSelect.addEventListener("change", () => {
        void loadManageEntities(sectionSelect.value);
    });
}

initAdminManagePage();
