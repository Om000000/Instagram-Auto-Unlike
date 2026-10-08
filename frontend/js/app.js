const $ = id => document.getElementById(id);
let currentPost = null;

async function api(url, options) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}

async function loadStats() {
  const stats = await api("/api/stats");
  ["total", "pending", "unliked", "kept", "skipped"].forEach(k => $(k).textContent = stats[k] ?? 0);
  $("progressText").textContent = `${stats.total - stats.pending} reviewed • ${stats.pending} pending`;
}

function badge(status) {
  const cls = {pending:"text-bg-warning", unliked:"text-bg-danger", kept:"text-bg-success", skipped:"text-bg-secondary"}[status] || "text-bg-secondary";
  return `<span class="badge ${cls}">${status.toUpperCase()}</span>`;
}

async function loadPosts() {
  const status = encodeURIComponent($("statusFilter").value);
  const search = encodeURIComponent($("searchInput").value.trim());
  const posts = await api(`/api/posts?limit=100&status=${status}&search=${search}`);
  const body = $("postsBody"); body.replaceChildren();
  if (!posts.length) { const row=document.createElement("tr"); const cell=document.createElement("td"); cell.colSpan=4; cell.className="text-secondary"; cell.textContent="No matching posts."; row.appendChild(cell); body.appendChild(row); return; }
  posts.forEach(post => {
    const row=document.createElement("tr");
    const title=document.createElement("td"); title.className="post-title"; title.textContent=post.post_title || post.post_url || "Instagram post";
    const date=document.createElement("td"); date.textContent=post.liked_at || "Unknown";
    const statusCell=document.createElement("td"); statusCell.innerHTML=badge(post.status);
    const linkCell=document.createElement("td"); const link=document.createElement("a"); link.href=post.post_url; link.target="_blank"; link.rel="noopener noreferrer"; link.textContent="Open"; linkCell.appendChild(link);
    row.append(title,date,statusCell,linkCell); body.appendChild(row);
  });
}

function renderReview(post) {
  currentPost = post;
  $("reviewCard").classList.toggle("d-none", !post);
  $("reviewEmpty").classList.toggle("d-none", !!post);
  if (!post) { $("progressText").textContent = "No pending posts"; return; }
  $("reviewStatus").textContent = post.status.toUpperCase();
  $("reviewDate").textContent = post.liked_at || "Unknown like date";
  $("reviewTitle").textContent = post.post_title || "Instagram post / reel";
  $("reviewCaption").textContent = post.post_title || "No caption available in the export.";
  $("reviewUrl").textContent = post.post_url;
  $("openInstagram").href = post.post_url;
}

async function loadNext() {
  const post = await api("/api/review/next");
  renderReview(post);
}

async function changeStatus(status) {
  if (!currentPost) return;
  const id = currentPost.id;
  try {
    await api(`/api/posts/${id}/status`, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({status})});
    await Promise.all([loadStats(), loadPosts()]);
    await loadNext();
  } catch (e) { alert(e.message); }
}

$("importForm").addEventListener("submit", async event => {
  event.preventDefault();
  const form = event.currentTarget;
  const formData = new FormData(form);
  $("importMessage").textContent = "Importing…";
  try {
    const result = await api("/api/import", {method:"POST", body:formData});
    $("importMessage").textContent = `Found ${result.found}; imported ${result.imported}; already present ${result.duplicates_or_existing}.`;
    form.reset();
    await Promise.all([loadStats(), loadPosts(), loadNext()]);
  } catch (e) { $("importMessage").textContent = e.message; }
});

document.querySelectorAll("[data-action]").forEach(button => button.addEventListener("click", () => changeStatus(button.dataset.action)));
$("refreshButton").addEventListener("click", async () => { await Promise.all([loadStats(),loadPosts()]); await loadNext(); });
$("reloadReview").addEventListener("click", loadNext);
$("statusFilter").addEventListener("change", loadPosts);
let searchTimer; $("searchInput").addEventListener("input", () => { clearTimeout(searchTimer); searchTimer=setTimeout(loadPosts,250); });

(async function init(){ try { await Promise.all([loadStats(),loadPosts(),loadNext()]); } catch(e) { console.error(e); $("progressText").textContent=e.message; } })();
