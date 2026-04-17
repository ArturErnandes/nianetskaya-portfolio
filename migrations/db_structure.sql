CREATE TABLE public.works (
    work_id serial PRIMARY KEY,
    section_name text NOT NULL,
    title text NOT NULL,
    caption text NOT NULL,
    description text NOT NULL,
    img_name text NOT NULL
);

CREATE TABLE public.projects (
    project_id serial PRIMARY KEY,
    section_name text NOT NULL,
    title text NOT NULL,
    caption text NOT NULL,
    cover_img_name text NOT NULL,
    description text
);

CREATE TABLE public.project_images (
    image_id serial PRIMARY KEY,
    project_id integer NOT NULL,
    description text,
    img_name text NOT NULL,
    order_index integer NOT NULL,
    CONSTRAINT project_images_project_order_key UNIQUE (project_id, order_index),
    CONSTRAINT project_images_project_id_fkey
        FOREIGN KEY (project_id)
        REFERENCES public.projects (project_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_projects_section_name ON public.projects USING btree (section_name);
CREATE INDEX idx_project_images_project_id ON public.project_images USING btree (project_id);
