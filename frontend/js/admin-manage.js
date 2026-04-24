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

function createWorkManageItem(work) {
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
    media.className = "manage-card-media";
    body.className = "manage-card-body";
    link.className = "manage-card-action";

    image.src = getThumbPathFromImageName(work.img_name);
    image.alt = work.title;
    image.loading = "lazy";
    image.decoding = "async";
    image.addEventListener("error", () => {
        if (image.dataset.fallbackApplied === "1") {
            return;
        }

        image.dataset.fallbackApplied = "1";
        image.src = `${WORKS_ASSETS_PATH}/${work.img_name}`;
    });

    title.textContent = work.title;
    caption.textContent = work.caption;
    link.href = `/admin/edit-work/${work.id}`;
    link.textContent = "редактировать";

    media.append(image);
    body.append(title, caption, link);
    article.append(media, body);
    item.append(article);

    return item;
}

function renderEmptyState(worksList, message) {
    const item = document.createElement("li");
    const emptyState = document.createElement("p");

    item.className = "manage-empty-item";
    emptyState.className = "manage-empty";
    emptyState.textContent = message;
    item.append(emptyState);
    worksList.replaceChildren(item);
}

async function loadManageWorks(sectionName) {
    const worksList = document.querySelector("[data-works-list]");

    if (!(worksList instanceof HTMLElement) || !sectionName) {
        return;
    }

    setManageStatus("Загрузка работ...");

    try {
        const response = await fetch(`${API_ENDPOINTS.works}?section_name=${encodeURIComponent(sectionName)}`);

        if (response.status === 401) {
            window.location.assign("/admin/login");
            return;
        }

        if (!response.ok) {
            setManageStatus("Не удалось загрузить работы");
            renderEmptyState(worksList, "Работы не загружены");
            return;
        }

        const works = await response.json();

        if (!Array.isArray(works)) {
            setManageStatus("Некорректный ответ сервера");
            renderEmptyState(worksList, "Работы не загружены");
            return;
        }

        if (works.length === 0) {
            setManageStatus("Работы в выбранной тематике не найдены", true);
            renderEmptyState(worksList, "В этой тематике пока нет работ");
            return;
        }

        worksList.replaceChildren(...works.map(createWorkManageItem));
        setManageStatus(`Найдено работ: ${works.length}`, true);
    } catch (error) {
        console.error("Ошибка при загрузке работ для редактирования:", error);
        setManageStatus("Ошибка сети. Попробуйте еще раз");
        renderEmptyState(worksList, "Работы не загружены");
    }
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
    void loadManageWorks(sectionSelect.value);

    sectionSelect.addEventListener("change", () => {
        void loadManageWorks(sectionSelect.value);
    });
}

initAdminManagePage();
