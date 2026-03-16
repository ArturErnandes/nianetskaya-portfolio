/**
 * @typedef {Object} Work
 * @property {number} id
 * @property {string} title
 * @property {string} caption
 * @property {string} img_name
 */

function revealImage(image, skeleton) {
    const showImage = async () => {
        try {
            if (typeof image.decode === "function") {
                await image.decode();
            }
        } catch (error) {
            // Ignore decode failures and reveal the loaded image anyway.
        }

        image.classList.add("is-loaded");
        skeleton.classList.add("is-hidden");
    };

    image.addEventListener("load", showImage, { once: true });
    image.addEventListener("error", () => {
        skeleton.classList.add("is-hidden");
    }, { once: true });

    if (image.complete && image.naturalWidth > 0) {
        void showImage();
    }
}

function revealStaticImage(image) {
    if (!image) {
        return;
    }

    const showImage = async () => {
        try {
            if (typeof image.decode === "function") {
                await image.decode();
            }
        } catch (error) {
            // Ignore decode failures and reveal the loaded image anyway.
        }

        image.classList.add("is-loaded");
    };

    image.addEventListener("load", showImage, { once: true });

    if (image.complete && image.naturalWidth > 0) {
        void showImage();
    }
}

function createWorkItem(work, index) {
    const workItem = document.createElement("li");
    const workLink = document.createElement("a");
    const figure = document.createElement("figure");
    const media = document.createElement("div");
    const image = document.createElement("img");
    const imageSkeleton = document.createElement("div");
    const figcaption = document.createElement("figcaption");
    const title = document.createElement("h5");
    const caption = document.createElement("p");
    const details = document.createElement("span");

    workItem.className = "work-item";
    workItem.style.animationDelay = `${index * 80}ms`;
    workLink.href = `/frontend/html/work-page.html?work_id=${work.id}`;

    media.className = "work-media";
    image.className = "work-image";
    imageSkeleton.className = "work-image-skeleton skeleton-block";

    image.alt = work.title;
    image.loading = "lazy";
    image.decoding = "async";
    image.src = `${WORKS_ASSETS_PATH}/${work.img_name}`;
    revealImage(image, imageSkeleton);

    title.textContent = work.title;
    caption.textContent = work.caption;
    details.textContent = "подробнее";

    figcaption.append(title, caption);
    media.append(image, imageSkeleton);
    figure.append(media, figcaption);
    workLink.append(figure, details);
    workItem.append(workLink);

    return workItem;
}
