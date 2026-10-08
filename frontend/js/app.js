const $ = id => document.getElementById(id);

async function loadStats() {
  const response = await fetch("/api/stats");
  if (!response.ok) throw new Error("Could not load statistics");
  const stats = await response.json();
  ["total", "pending", "unliked", "skipped"].forEach(key => {
    $(key).textContent = stats[key] ?? 0;
  });
}

async function loadPosts() {
  const response = await fetch("/api/posts?limit=50");
  if (!response.ok) throw new Error("Could not load posts");
  const posts = await response.json();
  const body = $("postsBody");
  body.replaceChildren();

  if (!posts.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 4;
    cell.className = "text-secondary";
    cell.textContent = "No imported posts yet.";
    row.appendChild(cell);
    body.appendChild(row);
    return;
  }

  posts.forEach(post => {
    const row = document.createElement("tr");
    const title = document.createElement("td");
    title.className = "post-title";
    title.textContent = post.post_title || "Instagram post";
    const date = document.createElement("td");
    date.textContent = post.liked_at || "Unknown";
    const status = document.createElement("td");
    status.textContent = post.status;
    const linkCell = document.createElement("td");
    const link = document.createElement("a");
    link.href = post.post_url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = "Open";
    linkCell.appendChild(link);
    row.append(title, date, status, linkCell);
    body.appendChild(row);
  });
}

async function refresh() {
  try {
    await Promise.all([loadStats(), loadPosts()]);
  } catch (error) {
    console.error(error);
  }
}

$("importForm").addEventListener("submit", async event => {
  event.preventDefault();
  const form = event.currentTarget;
  const formData = new FormData(form);
  $("importMessage").textContent = "Importing…";
  try {
    const response = await fetch("/api/import", { method: "POST", body: formData });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Import failed");
    $("importMessage").textContent =
      `Found ${result.found}; imported ${result.imported}; already present ${result.duplicates_or_existing}.`;
    form.reset();
    await refresh();
  } catch (error) {
    $("importMessage").textContent = error.message;
  }
});

$("refreshButton").addEventListener("click", refresh);
refresh();
