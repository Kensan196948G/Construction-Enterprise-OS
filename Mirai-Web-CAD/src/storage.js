const STORAGE_KEY = "mirai-web-cad-mvp";

export function loadDrawing() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function saveDrawing(drawing) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(drawing));
}

export function clearDrawing() {
  localStorage.removeItem(STORAGE_KEY);
}

export function exportDrawingFile(drawing) {
  const blob = new Blob([JSON.stringify(drawing, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `${drawing.name.replace(/[^\w-]+/g, "_")}_v${drawing.version}.json`;
  anchor.click();
  URL.revokeObjectURL(url);
}
