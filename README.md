# Le0nard1.github.io

Personal research website of Leonard Schroven, served by GitHub Pages at
<https://le0nard1.github.io>. Plain HTML, CSS and JavaScript: no build step and no
dependencies.

## Structure

```
index.html            page layout: intro, research environment, publications, teaching, CV
assets/style.css      layout and components, colours only through variables
assets/theme.css      the active colour scheme (written by tools/set_theme.py)
assets/site.js        renders the sections from data/
data/*.json           content: profile links, environment, publications, teaching, CV
papers/               PDFs of papers
files/                CV and other downloads
images/               screenshots of the environment
themes/themes.json    stored colour schemes
tools/set_theme.py    derives and publishes colour schemes
theme-lab.html        live colour playground (not linked from the site)
```

## Editing content

Everything below the intro is data. Edit the JSON file and push:

- **New paper:** add an entry to `data/publications.json`, put the PDF in `papers/`.
  Papers are sorted by year.
- **Teaching:** `data/teaching.json`.
- **CV:** `data/cv.json`; set `"pdf": "files/cv.pdf"` to show a download button.
- **Links (Scholar, ORCID, email):** `data/profile.json`; empty links are hidden.
- **Environment:** `data/environment.json`; add a screenshot path under `"image"`.

An empty `url` shows a greyed-out button, so a link can be prepared before it exists.

## Colour schemes

```bash
python tools/set_theme.py list                              # stored schemes, * = active
python tools/set_theme.py add calm "#2a9d8f,#e76f51"        # derive and store from colours
python tools/set_theme.py add calm "#2a9d8f,#e76f51" --use  # ... and publish
python tools/set_theme.py use forest                        # publish a stored scheme
python tools/set_theme.py check                             # contrast of all schemes
```

Two to six colours are enough: a very light colour becomes the background, a very dark one
the text, and the most saturated ones primary and accent. Roles can also be named, as in
`"primary=#7a1f5c,accent=#f2b134,bg=#fbf8f3"`. Light and dark mode are derived, and text
and link colours are corrected until they reach a contrast of 4.5:1 (WCAG AA).

**Preview without publishing:** open `index.html?theme=forest`.
**Play with colours:** open `theme-lab.html`, pick colours, and copy the generated command.

## Local preview

```bash
python -m http.server 8000      # then open http://localhost:8000
```

Opening `index.html` directly from disk does not load the data files; use the server.
