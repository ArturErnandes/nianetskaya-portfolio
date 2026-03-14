const MAIN_PAGE_SECTION_NAME = "main_page";

function initMainPageImages() {
    revealStaticImage(document.getElementById("background_img"));
    revealStaticImage(document.getElementById("avatar_img"));
}

function createSectionLinkItem([slug, section]) {
    const item = document.createElement("li");
    const link = document.createElement("a");

    link.href = `/${slug}`;
    link.textContent = section.heading.toLowerCase();

    item.append(link);

    return item;
}

function renderSectionsList() {
    const sectionsList = document.querySelector("[data-sections-list]");

    if (!sectionsList || typeof SECTIONS_CONFIG !== "object" || SECTIONS_CONFIG === null) {
        return;
    }

    sectionsList.replaceChildren(
        ...Object.entries(SECTIONS_CONFIG).map(createSectionLinkItem),
    );
}

async function loadMainPageWorks() {
    const worksSection = document.querySelector(".works");
    const worksList = worksSection?.querySelector(".works-list");

    if (!worksList) {
        return;
    }

    worksSection.dataset.sectionName = MAIN_PAGE_SECTION_NAME;

    const requestUrl = `${API_ENDPOINTS.works}?section_name=${encodeURIComponent(MAIN_PAGE_SECTION_NAME)}`;

    try {
        const response = await fetch(requestUrl);

        if (!response.ok) {
            console.error(`Ошибка ответа API: ${response.status}`);
            return;
        }

        /** @type {Work[]} */
        const works = await response.json();

        if (!Array.isArray(works)) {
            console.error("Некорректный формат данных работ");
            return;
        }

        worksList.replaceChildren(...works.map(createWorkItem));
    } catch (error) {
        console.error("Ошибка при загрузке работ:", error);
    }
}

function initMainPage() {
    if (document.body.dataset.page !== "main") {
        return;
    }

    renderSectionsList();
    initMainPageImages();
    void loadMainPageWorks();
}

initMainPage();
