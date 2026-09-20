export interface MapSitePin {
  id: number;
  name: string;
  lat: number;
  lng: number;
  status: string;
  workers: number;
  alerts: number;
}

export function buildSitePopup(pin: MapSitePin): HTMLElement {
  const root = document.createElement("div");
  root.style.minWidth = "160px";
  root.style.fontFamily = "sans-serif";

  const name = document.createElement("p");
  name.style.cssText = "font-weight:700;font-size:13px;margin:0 0 4px";
  name.textContent = pin.name;
  root.appendChild(name);

  if (pin.workers > 0) {
    const workers = document.createElement("p");
    workers.style.cssText = "font-size:12px;color:#6b7280;margin:2px 0";
    workers.textContent = `作業員: ${pin.workers}名`;
    root.appendChild(workers);
  }

  if (pin.alerts > 0) {
    const alerts = document.createElement("p");
    alerts.style.cssText = "font-size:12px;color:#dc2626;margin:2px 0";
    alerts.textContent = `⚠ ${pin.alerts}件 アラート`;
    root.appendChild(alerts);
  }

  const coords = document.createElement("p");
  coords.style.cssText = "font-size:11px;color:#9ca3af;margin:4px 0 0";
  coords.textContent = `${pin.lat.toFixed(4)}, ${pin.lng.toFixed(4)}`;
  root.appendChild(coords);

  return root;
}
