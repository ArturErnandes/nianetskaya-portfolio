/**
 * @typedef {Object} Work
 * @property {number} id
 * @property {string} title
 * @property {string} caption
 * @property {string} img_name
 */

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

        for (const work of works) {
            const workItem = document.createElement("li");
            const workLink = document.createElement("a");
            const figure = document.createElement("figure");
            const image = document.createElement("img");
            const figcaption = document.createElement("figcaption");
            const title = document.createElement("h5");
            const caption = document.createElement("p");
            const details = document.createElement("span");

            workLink.href = `./work.html?work_id=${work.id}`;

            image.src = `${ASSETS_PATH}/${work.img_name}`;
            image.alt = work.title;

            title.textContent = work.title;
            caption.textContent = work.caption;
            details.textContent = "Подробнее";

            figcaption.append(title, caption);
            figure.append(image, figcaption);
            workLink.append(figure, details);
            workItem.append(workLink);
            worksList.append(workItem);
        }
    } catch (error) {
        console.error("Ошибка при загрузке работ:", error);
    }
}


void loadWorks();