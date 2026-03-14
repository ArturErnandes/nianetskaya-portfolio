/**
 * @typedef {Object} Work
 * @property {number} id
 * @property {string} title
 * @property {string} caption
 * @property {string} img_name
 */

function renderSkeletons(worksList, count) {
    worksList.innerHTML = "";

    for (let index = 0; index < count; index += 1) {
        const skeletonItem = document.createElement("li");
        const skeletonCard = document.createElement("div");
        const skeletonFigure = document.createElement("figure");
        const skeletonImage = document.createElement("div");
        const skeletonCaption = document.createElement("figcaption");
        const skeletonTitle = document.createElement("div");
        const skeletonText = document.createElement("div");
        const skeletonButton = document.createElement("div");

        skeletonItem.className = "skeleton-item";
        skeletonCard.className = "skeleton-card";
        skeletonImage.className = "skeleton-block skeleton-image";
        skeletonTitle.className = "skeleton-block skeleton-title";
        skeletonText.className = "skeleton-block skeleton-text";
        skeletonButton.className = "skeleton-block skeleton-button";

        skeletonCaption.append(skeletonTitle, skeletonText);
        skeletonFigure.append(skeletonImage, skeletonCaption);
        skeletonCard.append(skeletonFigure, skeletonButton);
        skeletonItem.append(skeletonCard);
        worksList.append(skeletonItem);
    }
}

function createWorkItem(work, index) {
    const workItem = document.createElement("li");
    const workLink = document.createElement("a");
    const figure = document.createElement("figure");
    const image = document.createElement("img");
    const figcaption = document.createElement("figcaption");
    const title = document.createElement("h5");
    const caption = document.createElement("p");
    const details = document.createElement("span");

    workItem.className = "work-item";
    workItem.style.animationDelay = `${index * 80}ms`;
    workLink.href = `./work.html?work_id=${work.id}`;

    image.src = `${WORKS_ASSETS_PATH}/${work.img_name}`;
    image.alt = work.title;

    title.textContent = work.title;
    caption.textContent = work.caption;
    details.textContent = "подробнее";

    figcaption.append(title, caption);
    figure.append(image, figcaption);
    workLink.append(figure, details);
    workItem.append(workLink);

    return workItem;
}

async function loadWorks() {
    const worksSection = document.querySelector(".works");

    if (!worksSection) {
        return;
    }

    const sectionName = worksSection.dataset.sectionName;
    const worksList = worksSection.querySelector(".works-list");

    if (!sectionName || !worksList) {
        return;
    }

    const requestUrl = `${API_ENDPOINTS.works}?section_name=${encodeURIComponent(sectionName)}`;

    try {
        renderSkeletons(worksList, 6);

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

        worksList.innerHTML = "";

        for (const [index, work] of works.entries()) {
            worksList.append(createWorkItem(work, index));
        }
    } catch (error) {
        worksList.innerHTML = "";
        console.error("Ошибка при загрузке работ:", error);
    }
}


void loadWorks();
