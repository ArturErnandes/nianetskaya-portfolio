function getSectionSlugFromPath() {
    const pathname = window.location.pathname.replace(/^\/+|\/+$/g, "");

    return pathname || null;
}

function showMissingSectionState() {
    const heading = document.querySelector("[data-section-heading]");
    const worksList = document.querySelector(".works-list");

    if (heading) {
        heading.textContent = "Раздел не найден";
    }

    if (worksList) {
        worksList.replaceChildren();
    }
}

async function loadSectionWorks(sectionName) {
    const worksSection = document.querySelector(".works");
    const worksList = worksSection?.querySelector(".works-list");

    if (!worksList || !sectionName) {
        return;
    }

    worksSection.dataset.sectionName = sectionName;

    const requestUrl = `${API_ENDPOINTS.works}?section_name=${encodeURIComponent(sectionName)}`;

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

function initSectionPage() {
    if (document.body.dataset.page !== "section") {
        return;
    }

    const heading = document.querySelector("[data-section-heading]");
    const sectionSlug = getSectionSlugFromPath();
    const section = sectionSlug ? SECTIONS_CONFIG?.[sectionSlug] : null;

    if (!heading || !section) {
        showMissingSectionState();
        return;
    }

    heading.textContent = section.heading;
    void loadSectionWorks(sectionSlug);
}

initSectionPage();
