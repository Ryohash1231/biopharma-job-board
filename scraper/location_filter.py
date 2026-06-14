BAY_AREA_KEYWORDS = [
    "bay area",
    "san francisco",
    "redwood city",
    "emeryville",
    "berkeley",
    "brisbane",
    "foster city",
    "menlo park",
    "palo alto",
    "mountain view",
    "sunnyvale",
    "santa clara",
    "san jose",
    "fremont",
    "hayward",
    "oakland",
    "alameda",
    "vacaville",
    "novato",
    "san rafael",
    "san mateo",
    "burlingame",
    "san carlos",
    "union city",
    "pleasanton",
    "walnut creek",
    "hercules",
    "milpitas",
    "daly city",
    "belmont",
    "half moon bay",
    "petaluma",
    "vallejo",
    "richmond, ca",
    "concord, ca",
]

NON_US_REMOTE_MARKERS = [
    "japan",
    "uk",
    "italy",
    "spain",
    "switzerland",
    "netherlands",
    "france",
    "germany",
    "apac",
    "ireland",
    "canada",
    "australia",
    "china",
    "mexico",
    "brazil",
    "india",
]


def is_bay_area_or_remote(location):
    location_lower = location.lower()

    if any(keyword in location_lower for keyword in BAY_AREA_KEYWORDS):
        return True

    if "remote" in location_lower:
        if not any(marker in location_lower for marker in NON_US_REMOTE_MARKERS):
            return True

    return False
