// frontend/app.js

const API = "http://localhost:8080";
let token = localStorage.getItem("torberry_token") || null;
let refreshTimer = null;

// --- Init ---

window.onload = () => {
    if (token) {
        showMain();
    }
};

function show(pageId) {
    ["login-page", "main-page"].forEach(id => {
        document.getElementById(id).classList.add("hidden");
    });
    document.getElementById(pageId).classList.remove("hidden");
}

// --- Auth ---

async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const res = await fetch(`${API}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    if (res.ok) {
        const data = await res.json();
        token = data.token;
        localStorage.setItem("torberry_token", token);
        showMain();
    } else {
        document.getElementById("login-error").textContent = "Incorrect username or password";
    }
}

function logout() {
    token = null;
    localStorage.removeItem("torberry_token");
    clearInterval(refreshTimer);
    show("login-page");
}

function authHeaders() {
    return {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
    };
}

// --- Main ---

function showMain() {
    show("main-page");
    refreshAll();
    refreshTimer = setInterval(refreshAll, 2000);
}

// --- Refresh ---

async function refreshAll() {
    await refreshTorrents();
    await refreshStatus();
}

// --- Torrents ---

async function refreshTorrents() {
    const res = await fetch(`${API}/torrents/`, {
        headers: authHeaders()
    });

    if (res.status === 401) {
        logout();
        return;
    }

    const torrents = await res.json();
    const list = document.getElementById("torrent-list");

    if (torrents.length === 0) {
        list.innerHTML = "<p class='empty'>No torrents yet.</p>";
        return;
    }

    list.innerHTML = torrents.map(t => `
        <div class="torrent-card status-${t.status}">
            <div class="torrent-name">${t.name || "Fetching metadata..."}</div>
            <div class="torrent-meta">
                <span>${t.status}</span>
                <span>${formatSize(t.size)}</span>
                <span>↓ ${formatSpeed(t.download_rate)}</span>
                <span>↑ ${formatSpeed(t.upload_rate)}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${t.progress}%"></div>
            </div>
            <div class="torrent-actions">
                ${t.status === "downloading" || t.status === "seeding"
                    ? `<button onclick="pauseTorrent(${t.id})">Pause</button>`
                    : ""}
                ${t.status === "paused"
                    ? `<button onclick="resumeTorrent(${t.id})">Resume</button>`
                    : ""}
                <button onclick="deleteTorrent(${t.id})">Delete</button>
            </div>
        </div>
    `).join("");
}

async function addMagnet() {
    const magnet = document.getElementById("magnet-input").value.trim();
    if (!magnet) return;

    const res = await fetch(`${API}/torrents/magnet`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ magnet })
    });

    if (res.ok) {
        document.getElementById("magnet-input").value = "";
        refreshTorrents();
    } else {
        alert("Invalid magnet link");
    }
}

async function addFile() {
    const file = document.getElementById("torrent-file").files[0];
    if (!file) return;

    const form = new FormData();
    form.append("file", file);

    const res = await fetch(`${API}/torrents/file`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` },
        body: form
    });

    if (res.ok) {
        document.getElementById("torrent-file").value = "";
        refreshTorrents();
    } else {
        alert("Failed to add torrent file");
    }
}

async function pauseTorrent(id) {
    await fetch(`${API}/torrents/${id}/pause`, {
        method: "POST",
        headers: authHeaders()
    });
    refreshTorrents();
}

async function resumeTorrent(id) {
    await fetch(`${API}/torrents/${id}/resume`, {
        method: "POST",
        headers: authHeaders()
    });
    refreshTorrents();
}

async function deleteTorrent(id) {
    if (!confirm("Delete this torrent?")) return;
    await fetch(`${API}/torrents/${id}`, {
        method: "DELETE",
        headers: authHeaders()
    });
    refreshTorrents();
}

// --- Status ---

async function refreshStatus() {
    const res = await fetch(`${API}/status/`, {
        headers: authHeaders()
    });
    if (!res.ok) return;
    const s = await res.json();
    document.getElementById("cpu").textContent = `CPU: ${s.cpu_percent}%`;
    document.getElementById("ram").textContent = `RAM: ${s.ram_percent}%`;
    document.getElementById("disk").textContent = `Disk: ${formatSize(s.disk_free)} free`;
}

// --- Helpers ---

function formatSize(bytes) {
    if (!bytes) return "-";
    if (bytes > 1e9) return (bytes / 1e9).toFixed(1) + " GB";
    if (bytes > 1e6) return (bytes / 1e6).toFixed(1) + " MB";
    return (bytes / 1e3).toFixed(1) + " KB";
}

function formatSpeed(bps) {
    if (!bps) return "0 KB/s";
    if (bps > 1e6) return (bps / 1e6).toFixed(1) + " MB/s";
    return (bps / 1e3).toFixed(1) + " KB/s";
}
