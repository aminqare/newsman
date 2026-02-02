const statusEl = document.getElementById("status");
const updatedEl = document.getElementById("updated");
const listEl = document.getElementById("list");
const iranEl = document.getElementById("iran");
const refreshBtn = document.getElementById("refresh");
const searchInput = document.getElementById("search");
const showBriefsInput = document.getElementById("showBriefs");

let allSources = [];
let iranItems = [];

function formatDate(value) {
  if (!value) return "--";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "--";
  return date.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function matchesQuery(item, query) {
  if (!query) return true;
  const haystack = `${item.title || ""} ${item.summary || ""}`.toLowerCase();
  return haystack.includes(query);
}

function renderIran(items, query) {
  iranEl.innerHTML = "";
  const filtered = items.filter((item) => matchesQuery(item, query));
  if (!filtered.length) return;

  const box = document.createElement("section");
  box.className = "iran-box";

  const heading = document.createElement("div");
  heading.className = "source-header";

  const title = document.createElement("h2");
  title.textContent = "Iran mentions";

  heading.appendChild(title);
  box.appendChild(heading);

  const list = document.createElement("ol");
  list.className = "items";

  filtered.slice(0, 15).forEach((item) => {
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.href = item.link || "#";
    a.target = "_blank";
    a.rel = "noopener";
    a.textContent = item.title || "Untitled";
    li.appendChild(a);

    if (showBriefsInput.checked && item.summary) {
      const brief = document.createElement("div");
      brief.className = "brief";
      brief.textContent = item.summary;
      li.appendChild(brief);
    }

    list.appendChild(li);
  });

  box.appendChild(list);
  iranEl.appendChild(box);
}

function renderSources(sources, query) {
  listEl.innerHTML = "";
  const normalized = sources
    .map((group) => {
      const items = (group.items || []).filter((item) => matchesQuery(item, query));
      return { ...group, items };
    })
    .filter((group) => group.items.length > 0 || !query);

  if (!normalized.length) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = "No sources match the filter.";
    listEl.appendChild(empty);
    return;
  }

  normalized.forEach((group) => {
    const box = document.createElement("section");
    box.className = "source";

    const heading = document.createElement("div");
    heading.className = "source-header";

    const title = document.createElement("h2");
    title.textContent = group.source || "Untitled Source";

    const count = document.createElement("span");
    count.className = "source-link";
    count.textContent = `${group.items.length} items`;

    heading.appendChild(title);
    heading.appendChild(count);

    const list = document.createElement("ol");
    list.className = "items";

    if (group.items && group.items.length) {
      group.items.forEach((item) => {
        const li = document.createElement("li");
        const a = document.createElement("a");
        a.href = item.link || "#";
        a.target = "_blank";
        a.rel = "noopener";
        a.textContent = item.title || "Untitled";
        li.appendChild(a);

        if (showBriefsInput.checked && item.summary) {
          const brief = document.createElement("div");
          brief.className = "brief";
          brief.textContent = item.summary;
          li.appendChild(brief);
        }

        list.appendChild(li);
      });
    } else {
      const emptyItem = document.createElement("div");
      emptyItem.className = "empty-item";
      emptyItem.textContent = "No headlines.";
      list.appendChild(emptyItem);
    }

    box.appendChild(heading);
    box.appendChild(list);
    listEl.appendChild(box);
  });
}

function applyFilters() {
  const query = (searchInput.value || "").trim().toLowerCase();
  renderIran(iranItems, query);
  renderSources(allSources, query);
}

async function loadData() {
  statusEl.textContent = "Loading...";
  try {
    const response = await fetch(`data.json?ts=${Date.now()}`);
    if (!response.ok) throw new Error("Failed to load data");
    const data = await response.json();
    updatedEl.textContent = formatDate(data.generated_at || "");
    allSources = data.sources || [];
    iranItems = data.iran || [];
    applyFilters();
    statusEl.textContent = "Updated";
  } catch (err) {
    statusEl.textContent = "Error loading data";
    updatedEl.textContent = "--";
    allSources = [];
    iranItems = [];
    applyFilters();
  }
}

refreshBtn.addEventListener("click", loadData);
searchInput.addEventListener("input", applyFilters);
showBriefsInput.addEventListener("change", applyFilters);
loadData();
