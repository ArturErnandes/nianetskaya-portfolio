/**
 * @typedef {Object} OpenedWork
 * @property {string} section_name
 * @property {string} title
 * @property {string} description
 * @property {string} img_name
 */

function getWorkIdFromPath() {
    const match = window.location.pathname.match(/^\/work\/(\d+)\/?$/);

    if (!match) {
        return null;
    }

    const workId = Number(match[1]);

    if (!Number.isInteger(workId) || workId <= 0) {
        return null;
    }

    return workId;
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
        sessionStorage.setItem("workReturnPath", referrerPath);
        return referrerPath;
    }

    const storedPath = sessionStorage.getItem("workReturnPath");

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

function showMissingWorkState(workCard, worksList) {
    const title = document.createElement("h1");
    const description = document.createElement("p");

    title.textContent = "Работа не найдена";
    description.textContent = "Не удалось загрузить данные работы.";

    workCard.replaceChildren(title, description);
    worksList.replaceChildren();
}

function renderWorkCard(workCard, work) {
    const figure = document.createElement("figure");
    const media = document.createElement("div");
    const image = document.createElement("img");
    const imageSkeleton = document.createElement("div");
    const caption = document.createElement("figcaption");
    const title = document.createElement("h1");
    const description = document.createElement("p");

    figure.className = "work-content";
    media.className = "work-media";
    image.className = "work-image";
    imageSkeleton.className = "work-image-skeleton skeleton-block";

    image.alt = work.title;
    image.decoding = "async";
    image.src = `${WORKS_ASSETS_PATH}/${work.img_name}`;
    revealImage(image, imageSkeleton);

    title.textContent = work.title;
    description.textContent = work.description;

    caption.append(title, description);
    media.append(image, imageSkeleton);
    figure.append(media, caption);
    workCard.replaceChildren(figure);
}

async function initWorkPage() {
    if (document.body.dataset.page !== "work") {
        return;
    }

    const workId = getWorkIdFromPath();
    const workCard = document.querySelector(".work-card");
    const worksList = document.querySelector(".works-list");
    const backLink = document.querySelector(".back-link");

    if (!workId || !workCard || !worksList || !backLink) {
        if (workCard && worksList) {
            showMissingWorkState(workCard, worksList);
        }

        return;
    }

    try {
        /** @type {OpenedWork} */
        const work = await fetchJson(
            `${API_ENDPOINTS.works}/${workId}`,
            "Ошибка ответа API",
        );

        /** @type {Work[]} */
        const works = await fetchJson(
            `${API_ENDPOINTS.works}?section_name=${encodeURIComponent(work.section_name)}`,
            "Ошибка ответа API",
        );

        if (!work || typeof work !== "object" || !Array.isArray(works)) {
            throw new Error("Некорректный формат данных");
        }

        const returnTo = getReturnPath(work.section_name);

        backLink.href = returnTo || `/${work.section_name}`;
        backLink.setAttribute(
            "aria-label",
            returnTo === "/" ? "Назад на главную" : "Назад к категории",
        );

        renderWorkCard(workCard, work);
        worksList.replaceChildren(
            ...works
                .filter((item) => item.id !== workId)
                .map(createWorkItem),
        );
    } catch (error) {
        console.error("Ошибка при загрузке страницы работы:", error);
        showMissingWorkState(workCard, worksList);
    }
}

initWorkPage();
