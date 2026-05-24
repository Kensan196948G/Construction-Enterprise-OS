"""GIS空間演算サービス"""

from shapely import wkb, wkt
from shapely.geometry import mapping

from ..schemas import GeoJSONGeometry


def wkb_to_geojson_geometry(data: bytes | str | None) -> GeoJSONGeometry | None:
    """WKBまたはWKTをGeoJSON Geometry形式に変換"""
    if data is None:
        return None
    try:
        if isinstance(data, bytes):
            geom = wkb.loads(data)
        elif isinstance(data, str):
            clean = data
            if clean.startswith("SRID="):
                clean = clean.split(";", 1)[1]
            geom = wkt.loads(clean)
        else:
            return None
        geojson_dict = mapping(geom)
        return GeoJSONGeometry(
            type=geojson_dict["type"],
            coordinates=geojson_dict["coordinates"],
        )
    except Exception:
        return None


def geojson_to_wkt(geometry: GeoJSONGeometry) -> str:
    """GeoJSON GeometryからWKT文字列を生成"""
    coords = geometry.coordinates
    geom_type = geometry.type

    if geom_type == "Point":
        return f"SRID=4326;POINT({coords[0]} {coords[1]})"
    elif geom_type == "Polygon":
        rings = []
        for ring in coords:
            points = ", ".join(f"{p[0]} {p[1]}" for p in ring)
            rings.append(f"({points})")
        return f"SRID=4326;POLYGON({', '.join(rings)})"
    elif geom_type == "LineString":
        points = ", ".join(f"{p[0]} {p[1]}" for p in coords)
        return f"SRID=4326;LINESTRING({points})"
    elif geom_type == "MultiPoint":
        points = ", ".join(f"{p[0]} {p[1]}" for p in coords)
        return f"SRID=4326;MULTIPOINT({points})"
    else:
        raise ValueError(f"Unsupported geometry type: {geom_type}")
