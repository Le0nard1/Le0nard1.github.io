// Renders the content sections from the JSON files in data/. To add a paper, a course or a
// CV entry, edit the JSON file; the HTML does not change.
//
// Theme preview: index.html?theme=<name> applies a theme from themes/themes.json for this
// visit only, without changing the published theme.

const esc = s => String(s ?? "").replace(/[&<>"']/g, c =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

async function load(path) {
  try {
    const r = await fetch(path, { cache: "no-cache" });
    return r.ok ? await r.json() : null;
  } catch { return null; }
}

function button(label, url, solid = false) {
  if (!url) return `<span class="btn disabled">${esc(label)}</span>`;
  return `<a class="btn${solid ? " solid" : ""}" href="${esc(url)}" target="_blank" rel="noopener">${esc(label)}</a>`;
}

function renderProfile(p) {
  const el = document.getElementById("profile-links");
  if (!p || !el) return;
  el.innerHTML = (p.links || []).filter(l => l.url).map(l => button(l.label, l.url)).join("");
}

function renderEnvironment(items) {
  const el = document.getElementById("environment-list");
  if (!items || !el) return;
  el.innerHTML = items.map(e => `
    <article class="card">
      ${e.image ? `<img class="shot" src="${esc(e.image)}" alt="${esc(e.title)}">` : ""}
      <span class="tag">${esc(e.kind)}</span>
      <h3 style="margin-top:10px">${esc(e.title)}</h3>
      <p class="muted">${esc(e.text)}</p>
      ${e.features ? `<ul class="ticks small">${e.features.map(f => `<li>${esc(f)}</li>`).join("")}</ul>` : ""}
      <div class="actions">${(e.links || []).map((l, i) => button(l.label, l.url, i === 0)).join("")}</div>
      ${e.note ? `<p class="muted small" style="margin-top:12px">${esc(e.note)}</p>` : ""}
    </article>`).join("");
}

function renderPublications(pubs, me) {
  const el = document.getElementById("publication-list");
  if (!pubs || !el) return;
  pubs.sort((a, b) => (b.year || 0) - (a.year || 0));
  el.innerHTML = pubs.map(p => `
    <article class="card">
      <span class="tag">${esc(p.status || p.year)}</span>
      <div class="pub-title">${esc(p.title)}</div>
      <div class="pub-authors muted">${p.authors.map(a => a === me ? `<span class="me">${esc(a)}</span>` : esc(a)).join(", ")}</div>
      <div class="muted small">${esc(p.venue)}${p.year ? `, ${esc(p.year)}` : ""}</div>
      ${p.abstract ? `<details class="abstract"><summary>Abstract</summary><p>${esc(p.abstract)}</p></details>` : ""}
      <div class="actions">${(p.links || []).map((l, i) => button(l.label, l.url, i === 0)).join("")}</div>
    </article>`).join("");
}

function renderTeaching(items) {
  const el = document.getElementById("teaching-list");
  if (!items || !el) return;
  el.innerHTML = items.map(t => `
    <article class="card">
      <span class="tag">${esc(t.when)}</span>
      <h3 style="margin-top:10px">${esc(t.title)}</h3>
      <div class="muted small">${esc(t.role)}${t.where ? ` · ${esc(t.where)}` : ""}</div>
      ${t.text ? `<p class="muted" style="margin-top:10px">${esc(t.text)}</p>` : ""}
    </article>`).join("");
}

function renderCV(cv) {
  const el = document.getElementById("cv-list");
  if (!cv || !el) return;
  document.getElementById("cv-download").innerHTML =
    cv.pdf ? `<div class="actions">${button("Download CV (PDF)", cv.pdf, true)}</div>` : "";
  el.innerHTML = cv.groups.map(g => `
    <div class="cv-group">
      <h3>${esc(g.title)}</h3>
      ${g.items.map(i => `
        <div class="cv-item">
          <div class="cv-when">${esc(i.when)}</div>
          <div><strong>${esc(i.what)}</strong>${i.where ? `<div class="muted small">${esc(i.where)}</div>` : ""}
          ${i.text ? `<div class="muted small">${esc(i.text)}</div>` : ""}</div>
        </div>`).join("")}
    </div>`).join("");
}

async function previewTheme() {
  const name = new URLSearchParams(location.search).get("theme");
  if (!name) return;
  const t = await load("themes/themes.json");
  const theme = t && t.themes[name];
  if (!theme) return;
  for (const [k, v] of Object.entries(theme.light)) document.documentElement.style.setProperty(`--${k}`, v);
}

(async () => {
  document.getElementById("year").textContent = new Date().getFullYear();
  previewTheme();
  const [profile, env, pubs, teaching, cv] = await Promise.all([
    load("data/profile.json"), load("data/environment.json"), load("data/publications.json"),
    load("data/teaching.json"), load("data/cv.json")]);
  renderProfile(profile);
  renderEnvironment(env);
  renderPublications(pubs, profile && profile.name);
  renderTeaching(teaching);
  renderCV(cv);
})();
