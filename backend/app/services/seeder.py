import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.destination import Destination, Contributor, Endorsement
from ..data.catalog_metadata import source_fields

SEED_DESTINATIONS = [
    # ── INDIAN DESTINATIONS ────────────────────────────────────────────────
    {
        "name": "Goa",
        "country": "India",
        "region": "India",
        "description": "Sun-kissed Arabian Sea beaches, vibrant night markets, Portuguese heritage villas, and beach shack delicacies.",
        "category": "Beach",
        "tags": ["Beach", "Nightlife", "Water Sports", "Relaxing", "Seafood"],
        "rating": 4.7,
        "review_count": 5240,
        "endorsement_count": 18450,
        "price_inr": 15000,
        "best_season": "Nov – Feb",
        "image_url": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Kerala Backwaters",
        "country": "India",
        "region": "India",
        "description": "Tranquil emerald canals, traditional kettuvallam houseboats, coconut palm groves, and authentic Ayurvedic wellness.",
        "category": "Nature",
        "tags": ["Backwaters", "Houseboat", "Serene", "Nature", "Ayurveda"],
        "rating": 4.9,
        "review_count": 4890,
        "endorsement_count": 16900,
        "price_inr": 18000,
        "best_season": "Sep – Mar",
        "image_url": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Coorg",
        "country": "India",
        "region": "India",
        "description": "Misty hills of the Western Ghats lined with fragrant coffee estates, spice plantations, and cascading waterfalls.",
        "category": "Nature",
        "tags": ["Coffee", "Hills", "Trekking", "Nature", "Quiet"],
        "rating": 4.6,
        "review_count": 2980,
        "endorsement_count": 9400,
        "price_inr": 12000,
        "best_season": "Oct – Mar",
        "image_url": "https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Ooty",
        "country": "India",
        "region": "India",
        "description": "The Queen of Hill Stations in the Nilgiris, celebrated for scenic toy train rides, pine forests, and sprawling tea estates.",
        "category": "Nature",
        "tags": ["Hills", "Tea Gardens", "Heritage Train", "Cool Climate", "Scenic"],
        "rating": 4.5,
        "review_count": 3120,
        "endorsement_count": 8750,
        "price_inr": 10000,
        "best_season": "Oct – Jun",
        "image_url": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Manali",
        "country": "India",
        "region": "India",
        "description": "Snow-capped Himalayan peaks, roaring Beas river, pine valleys, and year-round thrills from skiing to paragliding.",
        "category": "Adventure",
        "tags": ["Snow", "Mountains", "Adventure", "Trekking", "Scenic"],
        "rating": 4.7,
        "review_count": 4650,
        "endorsement_count": 14200,
        "price_inr": 20000,
        "best_season": "Oct – Feb (Snow), Mar – Jun",
        "image_url": "https://images.unsplash.com/photo-1568454537842-d933259bb258?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Jaipur",
        "country": "India",
        "region": "India",
        "description": "The regal Pink City with majestic hill fortresses like Amer, intricate honeycomb facades of Hawa Mahal, and bustling bazaars.",
        "category": "Cultural",
        "tags": ["Heritage", "Forts", "Palaces", "Culture", "Shopping"],
        "rating": 4.8,
        "review_count": 5100,
        "endorsement_count": 15800,
        "price_inr": 14000,
        "best_season": "Oct – Mar",
        "image_url": "https://images.unsplash.com/photo-1477587458883-47145ed94245?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Udaipur",
        "country": "India",
        "region": "India",
        "description": "The City of Lakes featuring white marble palaces floating on Lake Pichola, rooftop cafes, and timeless Mewar grandeur.",
        "category": "Luxury",
        "tags": ["Romantic", "Lakes", "Palaces", "Heritage", "Luxury"],
        "rating": 4.9,
        "review_count": 4350,
        "endorsement_count": 17200,
        "price_inr": 22000,
        "best_season": "Sep – Mar",
        "image_url": "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Munnar",
        "country": "India",
        "region": "India",
        "description": "Rolling carpeted tea plantations, cool mountain mist, wildlife in Eravikulam National Park, and Anamudi peak vistas.",
        "category": "Nature",
        "tags": ["Tea Plantations", "Misty Hills", "Nature", "Trekking", "Scenic"],
        "rating": 4.7,
        "review_count": 3420,
        "endorsement_count": 11300,
        "price_inr": 13000,
        "best_season": "Sep – May",
        "image_url": "https://images.unsplash.com/photo-1593693397690-362cb9666fc2?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Hampi",
        "country": "India",
        "region": "India",
        "description": "Surreal boulder-strewn landscapes sheltering the monolithic stone ruins and temples of the Vijayanagara Empire along the Tungabhadra.",
        "category": "Cultural",
        "tags": ["UNESCO Heritage", "Ruins", "History", "Backpacker", "Architecture"],
        "rating": 4.8,
        "review_count": 2780,
        "endorsement_count": 10500,
        "price_inr": 11000,
        "best_season": "Oct – Feb",
        "image_url": "https://images.unsplash.com/photo-1600100397608-f010f443b7e7?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Rishikesh",
        "country": "India",
        "region": "India",
        "description": "Yoga Capital of the World along the roaring Ganga, famous for white-water river rafting, mountain meditation, and evening aartis.",
        "category": "Spiritual",
        "tags": ["Yoga", "Rafting", "Spiritual", "Ganges", "Adventure"],
        "rating": 4.7,
        "review_count": 3890,
        "endorsement_count": 13600,
        "price_inr": 9000,
        "best_season": "Sep – Apr",
        "image_url": "https://images.unsplash.com/photo-1588668214407-6ea9a6d8c272?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Varanasi",
        "country": "India",
        "region": "India",
        "description": "One of the world's oldest living cities, where ancient spiritual rituals, mesmerizing Ganga evening aartis, and historic ghats meet.",
        "category": "Spiritual",
        "tags": ["Spiritual", "Ghats", "Culture", "Historic", "River Aarti"],
        "rating": 4.6,
        "review_count": 4200,
        "endorsement_count": 12800,
        "price_inr": 10000,
        "best_season": "Oct – Mar",
        "image_url": "https://images.unsplash.com/photo-1561361513-2d000a50f0dc?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Ladakh",
        "country": "India",
        "region": "India",
        "description": "A high-altitude desert wonderland with crystal-clear Pangong Lake, towering mountain passes, and serene Buddhist monasteries.",
        "category": "Adventure",
        "tags": ["Himalaya", "High Passes", "Motorcycling", "Adventure", "Lakes"],
        "rating": 4.9,
        "review_count": 3100,
        "endorsement_count": 14900,
        "price_inr": 35000,
        "best_season": "May – Sep",
        "image_url": "https://images.unsplash.com/photo-1581793745862-99fde7fa73d2?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Andaman Islands",
        "country": "India",
        "region": "India",
        "description": "Pristine white sand beaches like Radhanagar, vibrant coral reef scuba diving, and azure waters surrounded by rainforests.",
        "category": "Beach",
        "tags": ["Scuba Diving", "Island", "Beaches", "Coral Reef", "Romantic"],
        "rating": 4.8,
        "review_count": 2890,
        "endorsement_count": 11800,
        "price_inr": 28000,
        "best_season": "Oct – May",
        "image_url": "https://images.unsplash.com/photo-1589308078059-be1415eab4c3?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Mysore",
        "country": "India",
        "region": "India",
        "description": "Heritage royal hub famed for the illuminated Amba Vilas Palace, fragrant sandalwood, rich silk sarees, and Chamundi Hill.",
        "category": "Cultural",
        "tags": ["Royal Palace", "Heritage", "Silk", "Culture", "Architecture"],
        "rating": 4.6,
        "review_count": 2450,
        "endorsement_count": 7900,
        "price_inr": 10000,
        "best_season": "Sep – Mar",
        "image_url": "https://images.unsplash.com/photo-1600100397608-f010f443b7e7?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Meghalaya",
        "country": "India",
        "region": "India",
        "description": "The Abode of Clouds featuring living root bridges in Cherrapunji, crystal-clear Dawki river, and roaring Nohkalikai Falls.",
        "category": "Nature",
        "tags": ["Living Root Bridges", "Waterfalls", "Caves", "Nature", "Trekking"],
        "rating": 4.8,
        "review_count": 2150,
        "endorsement_count": 9200,
        "price_inr": 24000,
        "best_season": "Oct – Apr",
        "image_url": "https://images.unsplash.com/photo-1626014303757-65644775be72?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Darjeeling",
        "country": "India",
        "region": "India",
        "description": "Charming colonial hill retreat offering golden Kanchenjunga sunrise views from Tiger Hill, world-famous tea gardens, and the toy train.",
        "category": "Nature",
        "tags": ["Himalaya", "Tea Estates", "Scenic", "Sunrise", "Toy Train"],
        "rating": 4.6,
        "review_count": 2800,
        "endorsement_count": 8600,
        "price_inr": 16000,
        "best_season": "Mar – May, Oct – Dec",
        "image_url": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=800&auto=format&fit=crop&q=80",
    },

    # ── INTERNATIONAL DESTINATIONS ─────────────────────────────────────────
    {
        "name": "Bali",
        "country": "Indonesia",
        "region": "Asia",
        "description": "Lush emerald rice terraces, cliffside sea temples in Uluwatu, world-class surf breaks, and spiritual wellness retreats.",
        "category": "Beach",
        "tags": ["Beach", "Spiritual", "Culture", "Surfing", "Tropical"],
        "rating": 4.7,
        "review_count": 4201,
        "endorsement_count": 15300,
        "price_inr": 63000,
        "best_season": "Apr – Sep",
        "image_url": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Kyoto",
        "country": "Japan",
        "region": "Asia",
        "description": "Ancient wooden temples, ethereal bamboo groves in Arashiyama, classical zen rock gardens, and traditional Gion geisha districts.",
        "category": "Cultural",
        "tags": ["Cultural", "Historic", "Nature", "Temples", "Zen"],
        "rating": 4.8,
        "review_count": 3102,
        "endorsement_count": 11450,
        "price_inr": 82000,
        "best_season": "Mar – May, Oct – Nov",
        "image_url": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Santorini",
        "country": "Greece",
        "region": "Europe",
        "description": "Iconic whitewashed cliffside villages perched above the volcanic caldera with legendary crimson sunsets over the Aegean Sea.",
        "category": "Luxury",
        "tags": ["Romantic", "Scenic", "Island", "Luxury", "Caldera"],
        "rating": 4.9,
        "review_count": 2341,
        "endorsement_count": 8720,
        "price_inr": 105000,
        "best_season": "Apr – Oct",
        "image_url": "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Iceland",
        "country": "Iceland",
        "region": "Europe",
        "description": "Dramatic land of fire and ice boasting glowing Northern Lights, thermal blue lagoons, glacier walks, and cascading waterfalls.",
        "category": "Adventure",
        "tags": ["Adventure", "Nature", "Aurora", "Glaciers", "Volcanoes"],
        "rating": 4.8,
        "review_count": 1623,
        "endorsement_count": 6540,
        "price_inr": 151000,
        "best_season": "Sep – Mar (Aurora), Jun – Aug",
        "image_url": "https://images.unsplash.com/photo-1476610182048-b716b8518aae?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Amalfi Coast",
        "country": "Italy",
        "region": "Europe",
        "description": "Pastel villages clinging dramatically to sheer Mediterranean sea cliffs, fragrant lemon groves, and glamorous coastal cruising.",
        "category": "Luxury",
        "tags": ["Scenic", "Coastal", "Luxury", "Romantic", "Italian Cuisine"],
        "rating": 4.7,
        "review_count": 2756,
        "endorsement_count": 7820,
        "price_inr": 92000,
        "best_season": "May – Sep",
        "image_url": "https://images.unsplash.com/photo-1612528443702-f6741f70a049?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Machu Picchu",
        "country": "Peru",
        "region": "South America",
        "description": "The legendary 15th-century Incan citadel shrouded in Andean clouds, celebrated for breathtaking stone architecture and the Inca Trail.",
        "category": "Adventure",
        "tags": ["Adventure", "Historic", "Trekking", "Ancient Ruins", "UNESCO"],
        "rating": 4.9,
        "review_count": 1890,
        "endorsement_count": 9340,
        "price_inr": 122000,
        "best_season": "Apr – Oct",
        "image_url": "https://images.unsplash.com/photo-1587595431973-160d0d94add1?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Bangkok",
        "country": "Thailand",
        "region": "Asia",
        "description": "Electric metropolis blending ornate Grand Palace shrines, bustling floating markets, Michelin-rated street food, and vibrant nightlife.",
        "category": "Cultural",
        "tags": ["Street Food", "Temples", "Nightlife", "Shopping", "Culture"],
        "rating": 4.6,
        "review_count": 4800,
        "endorsement_count": 13900,
        "price_inr": 45000,
        "best_season": "Nov – Feb",
        "image_url": "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Dubai",
        "country": "UAE",
        "region": "Asia",
        "description": "Futuristic skyline with the iconic Burj Khalifa, desert dune safaris, luxury shopping megamalls, and artificial Palm island marvels.",
        "category": "Luxury",
        "tags": ["Luxury", "Shopping", "Desert Safari", "Skyline", "Modern"],
        "rating": 4.7,
        "review_count": 5400,
        "endorsement_count": 16200,
        "price_inr": 55000,
        "best_season": "Nov – Mar",
        "image_url": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Maldives",
        "country": "Maldives",
        "region": "Asia",
        "description": "Ultimate tropical paradise with overwater bungalow villas, luminous coral atolls, manta ray snorkeling, and turquoise lagoons.",
        "category": "Beach",
        "tags": ["Overwater Villas", "Luxury", "Honeymoon", "Reefs", "Beach"],
        "rating": 4.9,
        "review_count": 3120,
        "endorsement_count": 14100,
        "price_inr": 120000,
        "best_season": "Nov – Apr",
        "image_url": "https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Singapore",
        "country": "Singapore",
        "region": "Asia",
        "description": "A dazzling garden city renowned for futuristic Supertree Groves at Gardens by the Bay, diverse hawker fare, and Marina Bay.",
        "category": "Cultural",
        "tags": ["Gardens", "Architecture", "Food", "Modern", "Clean City"],
        "rating": 4.7,
        "review_count": 3900,
        "endorsement_count": 12100,
        "price_inr": 68000,
        "best_season": "Year-round (Nov – Jan peak)",
        "image_url": "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Paris",
        "country": "France",
        "region": "Europe",
        "description": "The timeless City of Light offering Eiffel Tower views, the Louvre's treasures, romantic Seine river cruises, and artisan patisseries.",
        "category": "Cultural",
        "tags": ["Romantic", "Art", "Museums", "Cuisine", "Architecture"],
        "rating": 4.8,
        "review_count": 4700,
        "endorsement_count": 13800,
        "price_inr": 110000,
        "best_season": "Apr – Jun, Sep – Nov",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&auto=format&fit=crop&q=80",
    },
    {
        "name": "Phuket",
        "country": "Thailand",
        "region": "Asia",
        "description": "Thailand's largest sun-drenched island featuring limestone sea stacks in Phang Nga Bay, vibrant beach clubs, and Big Buddha.",
        "category": "Beach",
        "tags": ["Beach", "Islands", "Water Sports", "Nightlife", "Tropical"],
        "rating": 4.6,
        "review_count": 3600,
        "endorsement_count": 11200,
        "price_inr": 48000,
        "best_season": "Nov – Apr",
        "image_url": "https://images.unsplash.com/photo-1589394815804-964ed0be2eb5?w=800&auto=format&fit=crop&q=80",
    },
]

SEED_CONTRIBUTORS = [
    {
        "username": "priya_travels",
        "display_name": "Priya Sharma (Verified Travel Writer)",
        "is_verified": True,
        "reputation_score": 0.92,
        "account_age_days": 450,
        "endorsements_count": 12,
    },
    {
        "username": "arjun_nomad",
        "display_name": "Arjun Patel (Verified Backpacker)",
        "is_verified": True,
        "reputation_score": 0.88,
        "account_age_days": 310,
        "endorsements_count": 9,
    },
    {
        "username": "sarah_explorer",
        "display_name": "Sarah Jenkins (Global Explorer)",
        "is_verified": True,
        "reputation_score": 0.78,
        "account_age_days": 180,
        "endorsements_count": 6,
    },
    {
        "username": "vikram_hiker",
        "display_name": "Vikram Sen (Mountain Enthusiast)",
        "is_verified": False,
        "reputation_score": 0.62,
        "account_age_days": 95,
        "endorsements_count": 4,
    },
    {
        "username": "ananya_cultural",
        "display_name": "Ananya Roy (Heritage Blogger)",
        "is_verified": True,
        "reputation_score": 0.85,
        "account_age_days": 240,
        "endorsements_count": 8,
    },
]

def seed_destinations(db: Session) -> int:
    """
    Seeds initial realistic demonstration destinations, contributors, and relational endorsement records if empty.
    Returns the count of seeded destinations.
    """
    existing_count = db.query(Destination).count()
    if existing_count > 0:
        # Backfill source fields in the supplied prototype DB without touching
        # its editorial demo metrics. This keeps re-runs deterministic.
        for destination in db.query(Destination).all():
            metadata = source_fields(destination.name)
            for key, value in metadata.items():
                if getattr(destination, key) is None:
                    setattr(destination, key, value)
        db.commit()
        return existing_count

    # 1. Seed Destinations
    destinations_to_add = []
    for d in SEED_DESTINATIONS:
        dest = Destination(
            name=d["name"],
            country=d["country"],
            region=d["region"],
            description=d["description"],
            category=d["category"],
            tags=json.dumps(d["tags"]),
            rating=d["rating"],
            review_count=d["review_count"],
            baseline_endorsements=d["endorsement_count"],
            endorsement_count=d["endorsement_count"],
            price_inr=d["price_inr"],
            best_season=d["best_season"],
            image_url=d["image_url"],
            **source_fields(d["name"]),
        )
        destinations_to_add.append(dest)

    db.add_all(destinations_to_add)
    db.commit()

    # 2. Seed Contributors
    contributors_map = {}
    for c in SEED_CONTRIBUTORS:
        contrib = Contributor(
            username=c["username"],
            display_name=c["display_name"],
            is_verified=c["is_verified"],
            reputation_score=c["reputation_score"],
            account_age_days=c["account_age_days"],
            endorsements_count=c["endorsements_count"],
        )
        db.add(contrib)
        contributors_map[c["username"]] = contrib

    db.commit()

    # 3. Seed Initial Sample Relational Endorsements linking verified contributors to top destinations
    # Distribute over realistic past timestamps (e.g. 5, 20, 60, 120 days ago)
    now = datetime.utcnow()
    initial_endorsements = [
        # Goa (dest_id: 1) endorsed by Priya (verified writer, recent)
        {"dest_idx": 0, "username": "priya_travels", "days_ago": 5, "verified_visit": True, "trust": 0.95},
        # Goa endorsed by Arjun
        {"dest_idx": 0, "username": "arjun_nomad", "days_ago": 18, "verified_visit": True, "trust": 0.90},
        # Kerala Backwaters (dest_idx: 1) endorsed by Priya
        {"dest_idx": 1, "username": "priya_travels", "days_ago": 12, "verified_visit": True, "trust": 0.95},
        # Manali (dest_idx: 4) endorsed by Vikram
        {"dest_idx": 4, "username": "vikram_hiker", "days_ago": 45, "verified_visit": False, "trust": 0.65},
        # Jaipur (dest_idx: 5) endorsed by Ananya
        {"dest_idx": 5, "username": "ananya_cultural", "days_ago": 25, "verified_visit": True, "trust": 0.88},
        # Bali (dest_idx: 16) endorsed by Sarah
        {"dest_idx": 16, "username": "sarah_explorer", "days_ago": 30, "verified_visit": True, "trust": 0.82},
        # Kyoto (dest_idx: 17) endorsed by Sarah
        {"dest_idx": 17, "username": "sarah_explorer", "days_ago": 90, "verified_visit": True, "trust": 0.80},
    ]

    for ie in initial_endorsements:
        if ie["dest_idx"] < len(destinations_to_add):
            target_dest = destinations_to_add[ie["dest_idx"]]
            contrib = contributors_map.get(ie["username"])
            endr = Endorsement(
                destination_id=target_dest.id,
                contributor_id=contrib.id if contrib else None,
                session_id=f"seed_session_{ie['username']}_{target_dest.id}",
                trust_weight=ie["trust"],
                is_verified_visit=ie["verified_visit"],
                created_at=now - timedelta(days=ie["days_ago"]),
            )
            db.add(endr)

    db.commit()
    return len(destinations_to_add)
