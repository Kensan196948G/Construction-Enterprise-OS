"use client";

import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { buildSitePopup, type MapSitePin } from "./map-popup";

export type { MapSitePin };

interface LeafletMapProps {
  sitePins: MapSitePin[];
  height?: string;
}

function pinColor(status: string): string {
  if (status === "alert") return "#ef4444";
  if (status === "planning") return "#93c5fd";
  return "#2563eb";
}

function createDivIcon(status: string): L.DivIcon {
  const color = pinColor(status);
  const icon = status === "alert" ? "⚠" : status === "planning" ? "📋" : "🏗";
  return L.divIcon({
    className: "",
    html: `<div style="
      background:${color};
      width:32px;height:32px;
      border-radius:50%;
      display:flex;align-items:center;justify-content:center;
      font-size:14px;
      box-shadow:0 2px 6px rgba(0,0,0,0.3);
      border:2px solid white;
      cursor:pointer;
    ">${icon}</div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -34],
  });
}

export default function LeafletMap({
  sitePins,
  height = "480px",
}: LeafletMapProps) {
  const mapRef = useRef<L.Map | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const markersRef = useRef<L.Marker[]>([]);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    // Center on Tokyo construction area
    mapRef.current = L.map(containerRef.current, {
      center: [35.6, 139.7],
      zoom: 11,
      zoomControl: false,
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(mapRef.current);

    L.control.zoom({ position: "topright" }).addTo(mapRef.current);

    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    // Clear old markers
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    sitePins.forEach((pin) => {
      if (!pin.lat || !pin.lng) return;
      const marker = L.marker([pin.lat, pin.lng], {
        icon: createDivIcon(pin.status),
      }).addTo(map);

      marker.bindPopup(buildSitePopup(pin));

      markersRef.current.push(marker);
    });

    // Fit bounds if we have pins
    if (sitePins.length > 0 && sitePins.every((p) => p.lat && p.lng)) {
      const bounds = L.latLngBounds(sitePins.map((p) => [p.lat, p.lng]));
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 13 });
    }
  }, [sitePins]);

  return <div ref={containerRef} style={{ height, width: "100%" }} />;
}
