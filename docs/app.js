const statusEl = document.getElementById("status");
const updatedEl = document.getElementById("updated");
const listEl = document.getElementById("list");
const refreshBtn = document.getElementById("refresh");

function formatDate(value) {
  if (!value) return "--";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "--";
  return date.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function renderSources(sources) {
  listEl.innerHTML = "";
  if (!sources || sources.length === 0) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = "No sources yet.";
    listEl.appendChild(empty);
    return;
  }

  sources.forEach((group) => {
    const box = document.createElement("section");
    box.className = "source";

    const heading = document.createElement("div");
    heading.className = "source-header";

    const title = document.createElement("h2");
    title.textContent = group.source || "Untitled Source";

    if (group.source_url) {
      const link = document.createElement("a");
      link.href = group.source_url;
      link.target = "_blank";
      link.rel = "noopener";
      link.className = "source-link";
      link.textContent = "RSS";
      heading.appendChild(title);
      heading.appendChild(link);
    } else {
      heading.appendChild(title);
    }

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

async function loadData() {
  statusEl.textContent = "Loading...";
  try {
    const response = await fetch(`data.json?ts=${Date.now()}`);
    if (!response.ok) throw new Error("Failed to load data");
    const data = await response.json();
    updatedEl.textContent = formatDate(data.generated_at || "");
    renderSources(data.sources || []);
    statusEl.textContent = "Updated";
  } catch (err) {
    statusEl.textContent = "Error loading data";
    updatedEl.textContent = "--";
    renderSources([]);
  }
}

refreshBtn.addEventListener("click", loadData);
loadData();
