/**
 * @typedef {Object} Work
 * @property {number} id
 * @property {string} title
 * @property {string} caption
 * @property {string} img_name
 */

/**
 * @typedef {Object} Project
 * @property {number} id
 * @property {string} title
 * @property {string} caption
 * @property {string} img_name
 */

function revealImage(image, skeleton, fallbackSrc = null) {
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
        image.removeEventListener("error", handleError);
    };

    const handleError = () => {
        if (fallbackSrc && image.dataset.fallbackApplied !== "1") {
            image.dataset.fallbackApplied = "1";
            image.src = fallbackSrc;
            return;
        }

        skeleton.classList.add("is-hidden");
    };

    image.addEventListener("load", showImage, { once: true });
    image.addEventListener("error", handleError, { once: false });

    if (image.complete && image.naturalWidth > 0) {
        void showImage();
    }
}

function getThumbPathFromImageName(imageName) {
    const dotIndex = imageName.lastIndexOf(".");
    const baseName = dotIndex === -1 ? imageName : imageName.slice(0, dotIndex);
    return `${WORKS_THUMBS_PATH}/${baseName}.webp`;
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

function createInfoBadge() {
    const badge = document.createElement("span");

    badge.className = "project-info-badge";
    badge.setAttribute("aria-hidden", "true");
    badge.textContent = "i";

    return badge;
}

function createCardItem(entity, index, options = {}) {
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

    const {
        itemClassName = "work-item",
        href = null,
        showInfoBadge = false,
    } = options;

    workItem.className = itemClassName;
    workItem.style.animationDelay = `${index * 80}ms`;

    if (href) {
        workLink.href = href;
    }

    media.className = "work-media";
    image.className = "work-image";
    imageSkeleton.className = "work-image-skeleton skeleton-block";

    const originalSrc = `${WORKS_ASSETS_PATH}/${entity.img_name}`;
    const thumbSrc = getThumbPathFromImageName(entity.img_name);

    image.alt = entity.title;
    image.loading = "lazy";
    image.decoding = "async";
    image.src = thumbSrc;
    revealImage(image, imageSkeleton, originalSrc);

    title.textContent = entity.title;
    caption.textContent = entity.caption;
    details.className = "work-details";
    details.textContent = "подробнее";

    figcaption.append(title, caption);
    media.append(image, imageSkeleton);

    if (showInfoBadge) {
        media.append(createInfoBadge());
    }

    figure.append(media, figcaption);
    workLink.append(figure, details);
    workItem.append(workLink);

    return workItem;
}

function createWorkItem(work, index) {
    return createCardItem(work, index, {
        itemClassName: "work-item",
        href: `/work/${work.id}`,
    });
}

function createProjectItem(project, index) {
    return createCardItem(project, index, {
        itemClassName: "work-item project-item",
        href: `/project/${project.id}`,
        showInfoBadge: true,
    });
}
