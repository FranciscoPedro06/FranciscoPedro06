-- Francisco's profile, as a database.
-- Edit this file to update what visitors can query.

CREATE TABLE projects (
  name         TEXT PRIMARY KEY,
  what_it_does TEXT NOT NULL,
  stack        TEXT,
  link         TEXT
);

INSERT INTO projects VALUES
  ('FastPass',             'You show up, the camera knows you, you''re in.',            'Laravel, React, Face Recognition API, QR Code, Pix', 'https://franciscopedro-dev.vercel.app/projetos/fastpass'),
  ('Face Recognition API', 'Never forgets a face. That''s literally its only job.',     'Python, FastAPI, DeepFace',                          'https://franciscopedro-dev.vercel.app/projetos/reconhecimento-facial'),
  ('Smart Cart',           'A shopping cart that sees what you drop in it.',            'ESP32-CAM, Spring Boot',                             'https://franciscopedro-dev.vercel.app/projetos/carrinho-inteligente'),
  ('EduPass',              'The school bus checks your face, not your excuses.',        'Face Recognition API',                               'https://franciscopedro-dev.vercel.app/projetos/edupass'),
  ('Reviva',               'Locks your memories until the date you pick. No peeking.',  'Android',                                            'https://franciscopedro-dev.vercel.app/projetos/reviva');

CREATE TABLE skills (
  name     TEXT PRIMARY KEY,
  category TEXT NOT NULL,
  used_in  TEXT
);

INSERT INTO skills VALUES
  ('Power BI',    'data',     NULL),
  ('Python',      'data',     'Face Recognition API'),
  ('SQL',         'data',     'this profile'),
  ('Laravel',     'back-end', 'FastPass'),
  ('FastAPI',     'back-end', 'Face Recognition API'),
  ('DeepFace',    'back-end', 'Face Recognition API, FastPass, EduPass'),
  ('Spring Boot', 'back-end', 'Smart Cart'),
  ('Node.js',     'back-end', NULL),
  ('React',       'front-end','FastPass'),
  ('Android',     'mobile',   'Reviva'),
  ('ESP32-CAM',   'hardware', 'Smart Cart');

CREATE TABLE contact (
  channel TEXT PRIMARY KEY,
  url     TEXT NOT NULL
);

INSERT INTO contact VALUES
  ('linkedin',  'https://www.linkedin.com/in/francisco-pedro-5150492ba/'),
  ('email',     'pedro2006francisco@gmail.com'),
  ('portfolio', 'https://franciscopedro-dev.vercel.app'),
  ('github',    'https://github.com/FranciscoPedro06');

CREATE TABLE facts (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

INSERT INTO facts VALUES
  ('role',           'Data Analyst x Full-Stack Developer'),
  ('currently',      'fix: check that stdin can be half-closed before writing any of it'),
  ('this_database',  'is real. you just queried it.'),
  ('write_access',   'denied. nice try though.'),
  ('favorite_query', 'SELECT * FROM francisco.projects');

CREATE VIEW things_i_built AS
  SELECT name AS project, what_it_does FROM projects;
