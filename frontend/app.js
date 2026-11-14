const API = window.location.origin;
let token = localStorage.getItem("torberry_token") || null;
let refreshTimer = null;
let toastTimer = null;

window.addEventListener("load", () => {
    document.getElementById("login-form").addEventListener("submit", (event) => {
        event.preventDefault();
        login();
    });
    document.getElementById("magnet-form").addEventListener("submit", (event) => {
        event.preventDefault();
        addMagnet();
    });
    document.getElementById("torrent-file").addEventListener("change", addFile);
    document.getElementById("logout-button").addEventListener("click", logout);
    document.getElementById("refresh-button").addEventListener("click", refreshAll);
    token ? showMain() : show("login-page");
});

function show(pageId) {
    ["login-page", "main-page"].forEach((id) => document.getElementById(id).classList.add("hidden"));
    document.getElementById(pageId).classList.remove("hidden");
}

async function login() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;
    const error = document.getElementById("login-error");
    error.textContent = "";
    try {
        const res = await fetch(`${API}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });
        if (!res.ok) throw new Error("Incorrect username or password");
        const data = await res.json();
        token = data.token;
        localStorage.setItem("torberry_token", token);
        showMain();
    } catch (requestError) {
        error.textContent = requestError.message || "Unable to sign in";
    }
}

function logout() {
    token = null;
    localStorage.removeItem("torberry_token");
    clearInterval(refreshTimer);
    refreshTimer = null;
    show("login-page");
}

function authHeaders() {
    return { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
}

function showMain() {
    show("main-page");
    clearInterval(refreshTimer);
    refreshAll().catch(() => {
        document.getElementById("library-summary").textContent = "Unable to reach the downloader";
    });
    refreshTimer = setInterval(refreshAll, 3000);
}

async function refreshAll() {
    if (!token) return;
    await Promise.all([refreshTorrents(), refreshStatus()]);
}

async function refreshTorrents() {
    const res = await fetch(`${API}/torrents/`, { headers: authHeaders() });
    if (res.status === 401) return logout();
    if (!res.ok) throw new Error("Unable to load torrents");
    const torrents = await res.json();
    const list = document.getElementById("torrent-list");
    const summary = document.getElementById("library-summary");
    summary.textContent = `${torrents.length} ${torrents.length === 1 ? "download" : "downloads"} in your library`;
    if (!torrents.length) {
        list.innerHTML = "<div class=\"empty\"><strong>Your library is empty</strong>Add a magnet link or torrent file above to get started.</div>";
        return;
    }
    list.innerHTML = torrents.map(renderTorrent).join("");
}

function renderTorrent(torrent) {
    const status = torrent.status || "queued";
    const progress = Math.max(0, Math.min(100, Number(torrent.progress) || 0));
    const action = status === "downloading" || status === "seeding"
        ? `<button class="action-button" onclick="pauseTorrent(${torrent.id})">Pause</button>`
        : status === "paused"
            ? `<button class="action-button" onclick="resumeTorrent(${torrent.id})">Resume</button>`
            : "";
    return `<article class="torrent-card status-${escapeHtml(status)}">
        <div class="torrent-card-head">
            <div class="torrent-name" title="${escapeHtml(torrent.name || "Fetching metadata…")}">${escapeHtml(torrent.name || "Fetching metadata…")}</div>
            <span class="torrent-status status-${escapeHtml(status)}">${escapeHtml(status)}</span>
        </div>
        <div class="torrent-meta"><span>${formatSize(torrent.size)}</span><span>↓ ${formatSpeed(torrent.download_rate)}</span><span>↑ ${formatSpeed(torrent.upload_rate)}</span></div>
        <div class="progress-track"><div class="progress-fill" style="width: ${progress}%"></div></div>
        <div class="torrent-footer"><span class="progress-label">${progress.toFixed(1)}% complete</span><div class="torrent-actions">${action}<button class="action-button" onclick="deleteTorrent(${torrent.id})">Delete</button></div></div>
    </article>`;
}

async function addMagnet() {
    const input = document.getElementById("magnet-input");
    const magnet = input.value.trim();
    if (!magnet) return;
    await submitTorrent("/torrents/magnet", { magnet }, input);
}

async function addFile() {
    const input = document.getElementById("torrent-file");
    const file = input.files[0];
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    await submitTorrent("/torrents/file", form, input);
}

async function submitTorrent(endpoint, body, input) {
    const headers = body instanceof FormData ? { Authorization: `Bearer ${token}` } : authHeaders();
    try {
        const res = await fetch(`${API}${endpoint}`, { method: "POST", headers, body: body instanceof FormData ? body : JSON.stringify(body) });
        if (!res.ok) {
            const details = await res.json().catch(() => ({}));
            throw new Error(details.detail || "Could not add torrent");
        }
        input.value = "";
        document.getElementById("add-error").textContent = "";
        showToast("Download added to your library");
        await refreshTorrents();
    } catch (error) {
        document.getElementById("add-error").textContent = error.message;
    }
}

async function pauseTorrent(id) {
    await torrentAction(id, "pause");
}

async function resumeTorrent(id) {
    await torrentAction(id, "resume");
}

async function torrentAction(id, action) {
    const res = await fetch(`${API}/torrents/${id}/${action}`, { method: "POST", headers: authHeaders() });
    if (res.ok) await refreshTorrents();
}

async function deleteTorrent(id) {
    if (!confirm("Remove this torrent from your library?")) return;
    const res = await fetch(`${API}/torrents/${id}`, { method: "DELETE", headers: authHeaders() });
    if (res.ok) {
        showToast("Torrent removed");
        await refreshTorrents();
    }
}

async function refreshStatus() {
    const res = await fetch(`${API}/status/`, { headers: authHeaders() });
    if (!res.ok) return;
    const status = await res.json();
    document.getElementById("cpu").textContent = `${status.cpu_percent}%`;
    document.getElementById("ram").textContent = `${status.ram_percent}%`;
    document.getElementById("disk").textContent = formatSize(status.disk_free);
}

function formatSize(bytes) {
    if (!bytes) return "—";
    const units = ["B", "KB", "MB", "GB", "TB"];
    const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1000)), units.length - 1);
    return `${(bytes / (1000 ** index)).toFixed(index ? 1 : 0)} ${units[index]}`;
}

function formatSpeed(bps) {
    return `${formatSize(bps || 0)}/s`;
}

function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[character]));
}

function showToast(message) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.classList.add("visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("visible"), 2600);
}
