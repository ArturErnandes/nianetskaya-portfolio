function getSectionSlugFromPath() {
    const pathname = window.location.pathname.replace(/^\/+|\/+$/g, "");

    return pathname || null;
}

function toSentenceCase(value) {
    if (typeof value !== "string" || value.length === 0) {
        return "";
    }

    return value.charAt(0).toUpperCase() + value.slice(1);
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
    renderWorksLoadingState(worksList, 9);

    const worksRequestUrl = `${API_ENDPOINTS.works}?section_name=${encodeURIComponent(sectionName)}`;
    const projectsRequestUrl = `${API_ENDPOINTS.projects}?section_name=${encodeURIComponent(sectionName)}`;

    try {
        const [projectsResponse, worksResponse] = await Promise.all([
            fetch(projectsRequestUrl),
            fetch(worksRequestUrl),
        ]);

        if (!projectsResponse.ok) {
            console.error("Ошибка ответа API проектов: " + projectsResponse.status);
            worksList.replaceChildren();
            return;
        }

        if (!worksResponse.ok) {
            console.error("Ошибка ответа API работ: " + worksResponse.status);
            worksList.replaceChildren();
            return;
        }

        /** @type {Project[]} */
        const projects = await projectsResponse.json();
        /** @type {Work[]} */
        const works = await worksResponse.json();

        if (!Array.isArray(projects)) {
            console.error("Некорректный формат данных проектов");
            worksList.replaceChildren();
            return;
        }

        if (!Array.isArray(works)) {
            console.error("Некорректный формат данных работ");
            worksList.replaceChildren();
            return;
        }

        const projectItems = projects.map(createProjectItem);
        const workItems = works.map((work, index) => createWorkItem(work, index + projectItems.length));

        worksList.replaceChildren(...projectItems, ...workItems);
    } catch (error) {
        console.error("Ошибка при загрузке работ и проектов:", error);
        worksList.replaceChildren();
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
    document.title = toSentenceCase(section.heading);
    void loadSectionWorks(sectionSlug);
}

initSectionPage();
