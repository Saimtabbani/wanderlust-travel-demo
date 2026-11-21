"""Source-backed geographic metadata for Wanderlust's destination catalogue.

Wikidata entity data is published under CC0 1.0. This registry identifies the
place and supplies a representative coordinate for planning estimates only. It
does *not* validate this prototype's editorial summaries, prices, ratings,
endorsements, images, availability, or travel safety.
"""

CATALOG_SOURCE = {
    "name": "Wikidata",
    "license": "CC0 1.0",
    "checked_at": "2026-11-21",
}

# name: (latitude, longitude, Wikidata QID)
PLACE_METADATA = {
    "Goa": (15.2993, 74.1240, "Q1171"),
    "Kerala Backwaters": (9.4981, 76.3388, "Q639280"),
    "Coorg": (12.3375, 75.8069, "Q1136022"),
    "Ooty": (11.4102, 76.6950, "Q914969"),
    "Manali": (32.2432, 77.1892, "Q1379905"),
    "Jaipur": (26.9124, 75.7873, "Q21375"),
    "Udaipur": (24.5854, 73.7125, "Q200667"),
    "Munnar": (10.0889, 77.0595, "Q1146010"),
    "Hampi": (15.3350, 76.4600, "Q637405"),
    "Rishikesh": (30.0869, 78.2676, "Q755480"),
    "Varanasi": (25.3176, 82.9739, "Q1027"),
    "Ladakh": (34.2268, 77.5619, "Q2006677"),
    "Andaman Islands": (11.7401, 92.6586, "Q40886"),
    "Mysore": (12.2958, 76.6394, "Q1297"),
    "Meghalaya": (25.4670, 91.3662, "Q1186"),
    "Darjeeling": (27.0410, 88.2663, "Q201587"),
    "Bali": (-8.4095, 115.1889, "Q3120"),
    "Kyoto": (35.0116, 135.7681, "Q34600"),
    "Santorini": (36.3932, 25.4615, "Q192395"),
    "Iceland": (64.9631, -19.0208, "Q189"),
    "Amalfi Coast": (40.6333, 14.6029, "Q454347"),
    "Machu Picchu": (-13.1631, -72.5450, "Q12542"),
    "Bangkok": (13.7563, 100.5018, "Q1861"),
    "Dubai": (25.2048, 55.2708, "Q612"),
    "Maldives": (3.2028, 73.2207, "Q826"),
    "Singapore": (1.3521, 103.8198, "Q334"),
    "Paris": (48.8566, 2.3522, "Q90"),
    "Phuket": (7.9519, 98.3381, "Q182113"),
}


def source_fields(destination_name: str) -> dict:
    metadata = PLACE_METADATA.get(destination_name)
    if not metadata:
        return {}
    latitude, longitude, qid = metadata
    return {
        "latitude": latitude,
        "longitude": longitude,
        "source_name": CATALOG_SOURCE["name"],
        "source_url": f"https://www.wikidata.org/wiki/{qid}",
        "source_license": CATALOG_SOURCE["license"],
        "source_checked_at": CATALOG_SOURCE["checked_at"],
    }
