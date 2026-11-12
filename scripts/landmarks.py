# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy"]
# ///
"""Named places of Helenaveen: style overrides and extra geometry for buildings, plus the viewer's place list.

Sources: Monumenten in Nederland, Noord-Brabant (1997), Rijksmonumenten photos on Wikimedia Commons,
OpenStreetMap, and AHN for tower positions and heights.

Output: data/build/landmarks.json
"""

import json

import numpy as np

from config import BUILD, RAW
from geo import wgs_to_rd

# Local stories will be added after residents identify the places.
BUILDINGS = [{'name': 'Eben Haëzer-Rehobothkerk', 'latlon': (52.76146586875, 5.07985165), 'kind': 'Plek in Opperdoes', 'text': 'Deze kerk in Opperdoes wordt gebruikt door de Gereformeerde Gemeenten.', 'more': 'https://www.openstreetmap.org/way/277043588'}, {'name': 'Hervormde kerk', 'latlon': (52.7611191633803, 5.0797889845070445), 'kind': 'Plek in Opperdoes', 'text': 'De Hervormde kerk vormt een herkenningspunt in de dorpskern van Opperdoes. Rond de kerk ligt het kerkhof.', 'more': 'https://www.openstreetmap.org/way/277044675'}]
POINTS = [{'name': 'Opperdoes', 'at': (134006.545, 530038.617), 'kind': 'Dorp', 'text': 'Opperdoes in de gemeente Medemblik, Noord-Holland. Verken het dorp en het omringende landschap.', 'more': 'https://www.medemblik.nl/'}, {'name': 'De Skoôt', 'latlon': (52.7661243, 5.0727513), 'kind': 'Plek in Opperdoes', 'text': 'Een informatiebord vertelt hier over natuur- en waterbeheergebied De Skoôt in Opperdoes.', 'more': 'https://www.openstreetmap.org/node/2379590416'}, {'name': 'Startpunt Opperdoes', 'latlon': (52.7590762, 5.0732294), 'kind': 'Plek in Opperdoes', 'text': 'Vanaf dit informatiepunt kun je het wandelnetwerk van Noord-Holland verkennen.', 'more': 'https://www.openstreetmap.org/node/12296803599'}]
CATEGORIES = [("opperdoes", "Plekken in Opperdoes", ["Hervormde kerk", "Eben Haëzer-Rehobothkerk", "De Skoôt", "Startpunt Opperdoes"])]
INFO = ("note", "kind", "text", "address", "web", "more", "photo", "stop")
MASTS = []


def point_in_ring(x, y, ring):
    inside = False
    for (x1, y1), (x2, y2) in zip(ring, np.roll(ring, -1, axis=0)):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


ADDRESSES = None


def address_xy(name):
    """RD position of a BAG address such as "Geldersestraat 3" (data/raw/addresses.json, from scripts/fetch.py)."""
    global ADDRESSES
    if ADDRESSES is None:
        ADDRESSES = {label.replace(", Helenaveen", "").split(", ")[0]: (x, y) for x, y, label in json.loads((RAW / "addresses.json").read_text())}
    return ADDRESSES[name]


def building_at(rings, x, y):
    for rid, ring, a in rings:
        if point_in_ring(x, y, ring):
            return rid, a
    return None, None


def main():
    feats = [json.loads(line) for line in open(RAW / "3dbag.jsonl")]
    rings = []
    for f in feats:
        t = f["transform"]
        V = np.array(f["vertices"], dtype=np.float64) * t["scale"] + t["translate"]
        co = f["CityObjects"][f["id"]]
        rings.append((f["id"], V[co["geometry"][0]["boundaries"][0][0]][:, :2], co["attributes"]))

    out = {"buildings": {}, "places": [], "masts": [], "hotspots": [], "categories": []}
    for b in BUILDINGS:
        if "addrs" in b:
            pts = [address_xy(a) for a in b["addrs"]]
            pids = [building_at(rings, *pt)[0] for pt in pts]
            assert all(pids), f"{b['name']}: no building at {b['addrs']}"
            x, y = np.mean(pts, axis=0)
            out["places"].append({"name": b["name"], "note": b.get("note"), "x": x, "y": y, "h": 4.0})
            out["hotspots"].append({"name": b["name"], "pids": pids, "x": x, "y": y, **{k: b[k] for k in INFO if k in b}})
            print(f"{b['name']}: {', '.join(pids)}")
            continue
        x, y = b["at"] if "at" in b else wgs_to_rd(*b["latlon"])
        pid, attrs = None, None
        for rid, ring, a in rings:
            if point_in_ring(x, y, ring):
                pid, attrs = rid, a
                break
        if pid is None:
            d = [(np.hypot(*(ring.mean(0) - (x, y))), rid, a) for rid, ring, a in rings]
            dist, pid, attrs = min(d, key=lambda t: t[0])
            if dist > 20:
                pid = None
        height = ((attrs or {}).get("b3_h_dak_max") or 0) - ((attrs or {}).get("b3_h_maaiveld") or 0)
        if "tower" in b:
            height = b["tower"]["top"]
        elif "turret" in b:
            height = b["turret"]["top"]
        out["places"].append({"name": b["name"], "note": b.get("note"), "x": x, "y": y, "h": round(height, 1)})
        if pid and "style" in b:
            out["buildings"][pid] = {k: v for k, v in b.items() if k not in ("at", "latlon", *INFO)}
        if pid:
            out["hotspots"].append({"name": b["name"], "pid": pid, "x": x, "y": y, **{k: b[k] for k in INFO if k in b}})
        print(f"{b['name']}: {pid or 'no building'}")
    for p in POINTS:
        x, y = p["at"] if "at" in p else address_xy(p["addr"]) if "addr" in p else wgs_to_rd(*p["latlon"])
        out["places"].append({"name": p["name"], "note": p.get("note"), "x": x, "y": y, "h": 2.0})
        out["hotspots"].append({"name": p["name"], "x": x, "y": y, **{k: p[k] for k in INFO if k in p}})
    for m in MASTS:
        x, y = wgs_to_rd(*m["latlon"])
        out["masts"].append({**{k: v for k, v in m.items() if k != "latlon"}, "x": x, "y": y})
    names = {h["name"] for h in out["hotspots"]}
    for key, label, members in CATEGORIES:
        missing = [n for n in members if n not in names]
        assert not missing, f"{label}: no hotspot for {missing}"
        out["categories"].append({"key": key, "label": label, "names": members})
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "landmarks.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
