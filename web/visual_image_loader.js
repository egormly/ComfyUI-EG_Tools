// Visual Image Loader front-end
// Renamed from Image Folder Picker
// Features: Auto-apply on click, Flexbox layout

(function () {
  // 1. UPDATED ENDPOINTS TO MATCH PYTHON
  const ENDPOINT_LIST = "/visual_image_loader/list";
  const ENDPOINT_THUMB = "/visual_image_loader/thumb";
  
  const GRID_THUMB_SIZE = 224;
  const PREVIEW_SIZE   = 768;

  function el(tag, attrs = {}, children = []) {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "class") n.className = v;
      else if (k === "style") Object.assign(n.style, v);
      else n.setAttribute(k, v);
    }
    for (const c of [].concat(children)) {
      if (typeof c === "string") n.appendChild(document.createTextNode(c));
      else if (c) n.appendChild(c);
    }
    return n;
  }

  // Unique Style ID for this specific node
  const styleId = "vil-styles-v1";
  if (!document.getElementById(styleId)) {
    const st = el("style", { id: styleId }, [`
      /* Renamed classes from .ifp- to .vil- (Visual Image Loader) */
      .vil-panel {
        position: fixed; top: 72px; right: 16px; bottom: 16px; width: 420px;
        background: var(--comfy-menu-bg); color: var(--fg);
        border: 1px solid var(--border-color); border-radius: 8px;
        box-shadow: 0 6px 24px rgba(0,0,0,0.3);
        display: none; flex-direction: column; overflow: hidden; z-index: 9999;
      }
      .vil-header { padding: 8px 10px; border-bottom: 1px solid var(--border-color); font-weight: 600; display:flex; align-items:center; gap:8px;}
      .vil-close { margin-left: auto; cursor: pointer; opacity: 0.8; }
      .vil-toolbar { display:flex; gap:6px; padding: 8px; border-bottom: 1px solid var(--border-color);}
      .vil-toolbar input { width: 100%; }
      
      .vil-grid {
        display: flex; 
        flex-wrap: wrap; 
        align-content: flex-start;
        gap: 8px; padding: 8px; overflow-y: auto; flex: 1;
      }
      
      .vil-card {
        position: relative;
        width: 116px; flex-grow: 1; max-width: 160px;
        border: 1px solid var(--border-color); border-radius: 6px; overflow: hidden;
        cursor: pointer; background: #111; display:flex; flex-direction:column;
        transition: transform .06s ease-in-out, border-color .06s ease-in-out, box-shadow .06s ease-in-out;
      }
      
      .vil-card:hover { transform: translateY(-1px); }
      .vil-card.selected { border-color: #6aa3ff; box-shadow: 0 0 0 2px rgba(106,163,255,0.25) inset; }
      .vil-thumb { width: 100%; aspect-ratio: 1 / 1; object-fit: cover; display:block; }
      .vil-name {
        font-size: 11px; padding: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        border-top: 1px solid var(--border-color);
        background: rgba(255,255,255,0.02);
      }
      .vil-footer {
        border-top: 1px solid var(--border-color); padding: 8px;
        display:flex; gap:8px; align-items:center; justify-content: space-between;
      }
      .vil-left { display:flex; gap:8px; align-items:center; }
      .vil-right { opacity: 0.75; }
      .vil-empty { padding: 16px; opacity: 0.7; }
      .vil-btn { padding: 6px 10px; border: 1px solid var(--border-color); border-radius: 6px; background: var(--comfy-input-bg); cursor: pointer; }
      .vil-btn:hover { filter: brightness(1.1); }

      .vil-preview {
        position: fixed; pointer-events: none; border: 1px solid var(--border-color);
        background: #000; border-radius: 8px; padding: 4px; box-shadow: 0 6px 24px rgba(0,0,0,0.35);
        display: none; z-index: 10000;
      }
      .vil-preview img { max-width: ${PREVIEW_SIZE}px; max-height: ${PREVIEW_SIZE}px; display: block; }
    `]);
    document.head.appendChild(st);
  }

  const panel = el("div", { class: "vil-panel", id: "vil-panel" }, [
    el("div", { class: "vil-header" }, [
      el("span", {}, ["Visual Image Loader"]),
      el("span", { class: "vil-close", title: "Close" }, ["✕"])
    ]),
    el("div", { class: "vil-toolbar" }, [
      el("input", { id: "vil-folder", placeholder: "Folder path (must match node 'folder')" }),
      el("input", { id: "vil-pattern", placeholder: "Pattern(s): *.png;*.jpg", value: "*.png;*.jpg;*.jpeg;*.webp;*.bmp" }),
    ]),
    el("div", { class: "vil-grid", id: "vil-grid" }),
    el("div", { class: "vil-footer" }, [
      el("div", { class: "vil-left" }, [
        el("button", { class: "vil-btn", id: "vil-refresh" }, ["Refresh"]),
        el("button", { class: "vil-btn", id: "vil-apply", title: "Write selection to node" }, ["Apply"]),
      ]),
      el("div", { class: "vil-right" }, [
        el("span", { id: "vil-status" }, ["Idle"]),
      ]),
    ]),
  ]);
  document.body.appendChild(panel);

  const preview = el("div", { class: "vil-preview", id: "vil-preview" }, [
    el("img", { id: "vil-preview-img" })
  ]);
  document.body.appendChild(preview);

  const closeBtn = panel.querySelector(".vil-close");
  const folderInput = panel.querySelector("#vil-folder");
  const patternInput = panel.querySelector("#vil-pattern");
  const grid = panel.querySelector("#vil-grid");
  const refreshBtn = panel.querySelector("#vil-refresh");
  const applyBtn = panel.querySelector("#vil-apply");
  const statusSpan = panel.querySelector("#vil-status");
  const previewImg = preview.querySelector("#vil-preview-img");

  let currentNode = null;
  let pendingPath = "";

  function openPanel(node, folder, pattern) {
    currentNode = node;
    folderInput.value = folder || "";
    if (pattern) patternInput.value = pattern;

    pendingPath = "";
    if (currentNode && currentNode.widgets) {
      const w = currentNode.widgets.find(w => w.name === "selected");
      if (w && typeof w.value === "string" && w.value.trim()) {
        pendingPath = w.value.trim();
      }
    }

    panel.style.display = "flex";
    loadList();
  }
  function closePanel() {
    panel.style.display = "none";
    currentNode = null;
    pendingPath = "";
    hidePreview();
  }
  closeBtn.addEventListener("click", closePanel);

  function showPreview(src, x, y) {
    previewImg.src = src;
    preview.style.display = "block";
    positionPreview(x, y);
  }
  function positionPreview(x, y) {
    const margin = 16;
    const pw = PREVIEW_SIZE + 12;
    const ph = PREVIEW_SIZE + 12;
    let left = x + margin;
    let top = y + margin;
    if (left + pw > window.innerWidth) left = x - pw - margin;
    if (top + ph > window.innerHeight) top = y - ph - margin;
    preview.style.left = `${Math.max(0, left)}px`;
    preview.style.top = `${Math.max(0, top)}px`;
  }
  function hidePreview() {
    preview.style.display = "none";
    previewImg.removeAttribute("src");
  }

  function markSelectedCard(path) {
    for (const c of grid.querySelectorAll(".vil-card.selected")) c.classList.remove("selected");
    const card = grid.querySelector(`.vil-card[data-path="${CSS.escape(path)}"]`);
    if (card) card.classList.add("selected");
  }

  async function loadList() {
    grid.innerHTML = "";
    statusSpan.textContent = "Loading...";
    const params = new URLSearchParams({
      folder: folderInput.value || "",
      pattern: patternInput.value || "",
      sort: "Date ↓",
      limit: "512",
    });
    try {
      const r = await fetch(`${ENDPOINT_LIST}?${params.toString()}`);
      const js = await r.json();
      if (!js.ok) throw new Error("Server returned not ok");
      const files = js.files || [];
      if (!files.length) {
        grid.appendChild(el("div", { class: "vil-empty" }, ["No images found."]));
      } else {
        for (const f of files) {
          const card = el("div", { class: "vil-card", title: f.path });
          card.dataset.path = f.path;
          const thumbSrc = `${ENDPOINT_THUMB}?path=${encodeURIComponent(f.path)}&size=${GRID_THUMB_SIZE}`;
          const img = el("img", { class: "vil-thumb", src: thumbSrc, draggable: "false" });
          const name = el("div", { class: "vil-name" }, [f.name]);

          card.addEventListener("click", () => {
            pendingPath = f.path;
            markSelectedCard(pendingPath);
            applySelection(); 
          });

          card.addEventListener("mouseenter", (ev) => {
            const bigSrc = `${ENDPOINT_THUMB}?path=${encodeURIComponent(f.path)}&size=${PREVIEW_SIZE}`;
            showPreview(bigSrc, ev.clientX, ev.clientY);
          });
          card.addEventListener("mousemove", (ev) => positionPreview(ev.clientX, ev.clientY));
          card.addEventListener("mouseleave", hidePreview);

          card.appendChild(img);
          card.appendChild(name);
          grid.appendChild(card);
        }
        if (pendingPath) markSelectedCard(pendingPath);
      }
      statusSpan.textContent = `Loaded ${grid.children.length} items`;
    } catch (e) {
      console.error(e);
      statusSpan.textContent = "Error";
      grid.appendChild(el("div", { class: "vil-empty" }, ["Error loading list. Check console."]));
    }
  }

  function applySelection() {
    if (!currentNode) return;
    if (!pendingPath) {
      statusSpan.textContent = "No image selected";
      return;
    }
    if (!currentNode.widgets) return;
    const w = currentNode.widgets.find(w => w.name === "selected");
    if (!w) return;

    w.value = pendingPath;
    statusSpan.textContent = "Applied: " + pendingPath.split(/[/\\]/).pop();
  }

  applyBtn.addEventListener("click", applySelection);
  refreshBtn.addEventListener("click", loadList);

  // 2. HOOK INTO THE NEW NODE NAME
  const _origAdd = LGraph.prototype.add;
  LGraph.prototype.add = function(node) {
    const ret = _origAdd.apply(this, arguments);
    try {
      // MUST MATCH THE NODE_NAME IN PYTHON
      if (node && node.type === "Visual Image Loader") {
        if (!node.widgets) node.widgets = [];
        if (!node.widgets.find(w => w.name === "Browse")) {
          node.addWidget("button", "Browse", "open", () => {
            const folderW = node.widgets.find(w => w.name === "folder");
            const patternW = node.widgets.find(w => w.name === "pattern");
            const folder = folderW ? folderW.value : "";
            const pattern = patternW ? patternW.value : "";
            openPanel(node, folder, pattern);
          });
        }
      }
    } catch (e) {
      console.warn("Visual Image Loader add hook error:", e);
    }
    return ret;
  };

  console.log("[Visual Image Loader] front-end loaded");
})();