const statusEl = document.getElementById("status");
const countEl = document.getElementById("count");
const updatedEl = document.getElementById("updated");
const nextEl = document.getElementById("next");
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

function renderItems(items) {
  listEl.innerHTML = "";
  if (!items || items.length === 0) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = "No headlines yet. Check back after the next run.";
    listEl.appendChild(empty);
    return;
  }

  items.forEach((item, index) => {
    const card = document.createElement("article");
    card.className = "card";

    const badge = document.createElement("div");
    badge.className = "index";
    badge.textContent = String(index + 1);

    const body = document.createElement("div");

    const title = document.createElement("h3");
    const link = document.createElement("a");
    link.href = item.link || "#";
    link.target = "_blank";
    link.rel = "noopener";
    link.textContent = item.title || "Untitled";
    title.appendChild(link);

    const source = document.createElement("div");
    source.className = "source";
    source.textContent = item.source ? `Source: ${item.source}` : "Source: Unknown";

    body.appendChild(title);
    body.appendChild(source);

    card.appendChild(badge);
    card.appendChild(body);
    listEl.appendChild(card);
  });
}

async function loadData() {
  statusEl.textContent = "Loading...";
  try {
    const response = await fetch(`data.json?ts=${Date.now()}`);
    if (!response.ok) throw new Error("Failed to load data");
    const data = await response.json();
    const generatedAt = data.generated_at || "";
    countEl.textContent = data.count ?? 0;
    updatedEl.textContent = formatDate(generatedAt);

    if (generatedAt) {
      const next = new Date(generatedAt);
      if (!Number.isNaN(next.getTime())) {
        next.setHours(next.getHours() + 3);
        nextEl.textContent = formatDate(next.toISOString());
      } else {
        nextEl.textContent = "--";
      }
    } else {
      nextEl.textContent = "--";
    }

    renderItems(data.items || []);
    statusEl.textContent = "Updated";
  } catch (err) {
    statusEl.textContent = "Error loading data";
    countEl.textContent = "--";
    updatedEl.textContent = "--";
    nextEl.textContent = "--";
    renderItems([]);
  }
}

refreshBtn.addEventListener("click", loadData);
loadData();
