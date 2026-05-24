"""BIMサービス ユーティリティ"""

from geoalchemy2 import WKTElement


def geojson_to_wkt_element(geometry: dict) -> WKTElement | None:
    """Convert GeoJSON geometry dict to WKTElement for PostGIS insert."""
    if not geometry:
        return None
    geom_type = geometry.get("type", "").upper()
    coords = geometry.get("coordinates", [])

    if geom_type == "POINT":
        return WKTElement(f"POINT({coords[0]} {coords[1]})", srid=4326)
    elif geom_type == "POLYGON":
        rings = []
        for ring in coords:
            pts = ", ".join(f"{p[0]} {p[1]}" for p in ring)
            rings.append(f"({pts})")
        return WKTElement(f"POLYGON({', '.join(rings)})", srid=4326)
    elif geom_type == "POINTZ":
        return WKTElement(f"POINT Z({coords[0]} {coords[1]} {coords[2]})", srid=4326)

    return None
