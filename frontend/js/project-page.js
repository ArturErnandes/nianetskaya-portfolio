/**
 * @typedef {Object} ProjectImage
 * @property {string} img_name
 * @property {string | null} description
 */

/**
 * @typedef {Object} OpenedProject
 * @property {string} section_name
 * @property {string} title
 * @property {string} description
 * @property {string} cover_img_name
 * @property {ProjectImage[]} images
 */

function getProjectIdFromPath() {
    const match = window.location.pathname.match(/^\/project\/(\d+)\/?$/);

    if (!match) {
        return null;
    }

    const projectId = Number(match[1]);

    if (!Number.isInteger(projectId) || projectId <= 0) {
        return null;
    }

    return projectId;
}

function getCategoryPath(sectionName) {
    return SECTIONS_CONFIG?.[sectionName] ? `/${sectionName}` : null;
}

function getReferrerPath() {
    if (!document.referrer) {
        return null;
    }

    const referrerUrl = new URL(document.referrer);

    if (referrerUrl.origin !== window.location.origin) {
        return null;
    }

    const referrerPath = referrerUrl.pathname;

    if (referrerPath === "/") {
        return referrerPath;
    }

    const sectionSlug = referrerPath.replace(/^\/+|\/+$/g, "");

    if (SECTIONS_CONFIG?.[sectionSlug]) {
        return `/${sectionSlug}`;
    }

    return null;
}

function getReturnPath(sectionName) {
    const referrerPath = getReferrerPath();

    if (referrerPath) {
        sessionStorage.setItem("projectReturnPath", referrerPath);
        return referrerPath;
    }

    const storedPath = sessionStorage.getItem("projectReturnPath");

    if (storedPath === "/" || storedPath === getCategoryPath(sectionName)) {
        return storedPath;
    }

    return getCategoryPath(sectionName);
}

async function fetchJson(url, errorMessage) {
    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`${errorMessage}: ${response.status}`);
    }

    return response.json();
}

function createProjectMediaFigure(titleText, descriptionText, imageName, figureClassName) {
    const figure = document.createElement("figure");
    const media = document.createElement("div");
    const image = document.createElement("img");
    const imageSkeleton = document.createElement("div");
    const caption = document.createElement("figcaption");

    const titleTag = titleText ? document.createElement("h1") : null;
    const descriptionTag = descriptionText ? document.createElement("p") : null;

    figure.className = figureClassName;
    media.className = "work-media";
    image.className = "work-image";
    imageSkeleton.className = "work-image-skeleton skeleton-block";

    image.alt = titleText || "Изображение проекта";
    image.decoding = "async";

    if (titleText) {
        image.loading = "eager";
        image.fetchPriority = "high";
    } else {
        image.loading = "lazy";
    }

    image.src = `${WORKS_ASSETS_PATH}/${imageName}`;
    revealImage(image, imageSkeleton);

    media.append(image, imageSkeleton);
    figure.append(media);

    if (titleTag || descriptionTag) {
        if (titleTag) {
            titleTag.textContent = titleText;
            caption.append(titleTag);
        }

        if (descriptionTag) {
            descriptionTag.textContent = descriptionText;
            caption.append(descriptionTag);
        }

        figure.append(caption);
    }

    return figure;
}

function showMissingProjectState(projectCard, worksList) {
    const title = document.createElement("h1");
    const description = document.createElement("p");

    title.textContent = "Проект не найден";
    description.textContent = "Не удалось загрузить данные проекта.";

    projectCard.replaceChildren(title, description);
    worksList.replaceChildren();
}

function renderProjectLoadingState(projectCard) {
    const figure = document.createElement("figure");
    const media = document.createElement("div");
    const imageSkeleton = document.createElement("div");

    figure.className = "project-content";
    media.className = "work-media";
    imageSkeleton.className = "skeleton-image skeleton-block";

    media.append(imageSkeleton);
    figure.append(media);
    projectCard.replaceChildren(figure);
}

function renderProject(projectCard, project) {
    const fragment = document.createDocumentFragment();
    const coverFigure = createProjectMediaFigure(
        project.title,
        project.description,
        project.cover_img_name,
        "project-content",
    );

    fragment.append(coverFigure);

    if (Array.isArray(project.images) && project.images.length > 0) {
        const gallery = document.createElement("section");
        gallery.className = "project-gallery";

        const figures = project.images.map((image) => createProjectMediaFigure(
            null,
            image.description,
            image.img_name,
            "project-gallery-item",
        ));

        gallery.append(...figures);
        fragment.append(gallery);
    }

    projectCard.replaceChildren(fragment);
}

async function initProjectPage() {
    if (document.body.dataset.page !== "project") {
        return;
    }

    const projectId = getProjectIdFromPath();
    const projectCard = document.querySelector(".project-card");
    const worksList = document.querySelector(".works-list");
    const backLink = document.querySelector(".back-link");

    if (!projectId || !projectCard || !worksList || !backLink) {
        if (projectCard && worksList) {
            showMissingProjectState(projectCard, worksList);
        }

        return;
    }

    renderProjectLoadingState(projectCard);
    renderWorksLoadingState(worksList, 5);

    /** @type {OpenedProject | null} */
    let project = null;

    try {
        project = await fetchJson(
            `${API_ENDPOINTS.projects}/${projectId}`,
            "Ошибка ответа API",
        );

        if (!project || typeof project !== "object") {
            throw new Error("Некорректный формат данных проекта");
        }
    } catch (error) {
        console.error("Ошибка при загрузке страницы проекта:", error);
        showMissingProjectState(projectCard, worksList);
        return;
    }

    const returnTo = getReturnPath(project.section_name);

    backLink.href = returnTo || `/${project.section_name}`;
    backLink.setAttribute(
        "aria-label",
        returnTo === "/" ? "Назад на главную" : "Назад к категории",
    );

    // Start loading full cover/gallery images immediately after project metadata is received.
    renderProject(projectCard, project);

    try {
        /** @type {Work[]} */
        const works = await fetchJson(
            `${API_ENDPOINTS.works}?section_name=${encodeURIComponent(project.section_name)}`,
            "Ошибка ответа API",
        );

        if (!Array.isArray(works)) {
            throw new Error("Некорректный формат данных работ");
        }

        worksList.replaceChildren(...works.map(createWorkItem));
    } catch (error) {
        console.error("Ошибка при загрузке списка похожих работ:", error);
        worksList.replaceChildren();
    }
}

initProjectPage();
