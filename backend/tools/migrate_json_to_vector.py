import json
import os
import sys
import logging
from typing import Dict, Any

# Ensure backend can be imported
sys.path.append(os.getcwd())

from backend.memory.vector_store_manager import VectorStoreManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DNS_Migrator")


def load_json_db(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load DB: {e}")
        return {}


def migrate_data():
    logger.info("--- Starting Knowledge Migration ---")

    # Paths
    json_path = os.path.join(os.getcwd(), "trips_db.json")
    vector_store = VectorStoreManager()

    data = load_json_db(json_path)
    if not data:
        return

    collection_name = "knowledge_base"

    # 1. Migrate Company Profile
    profile = data.get("company_profile", {})
    if profile:
        text = f"Company Profile: {profile.get('name')} specializes in {profile.get('specialty')}. Target audience: {profile.get('target_audience')}."
        vector_store.add_memory(
            collection_name, text, {"category": "profile", "source": "trips_db.json"}
        )
        logger.info("Migrated Company Profile.")

    # 2. Migrate AI Persona
    persona = data.get("ai_persona", {})
    if persona:
        text = f"AI Persona: My name is {persona.get('name')}, a {persona.get('role')}. Tone: {persona.get('tone')}. Rule: {persona.get('self_identification_rule')}"
        vector_store.add_memory(
            collection_name, text, {"category": "persona", "source": "trips_db.json"}
        )
        logger.info("Migrated AI Persona.")

    # 3. Migrate Trips
    trips = data.get("trips", [])
    for trip in trips:
        # Construct a rich semantic string
        details = ", ".join(
            trip.get("includes", [])
            + trip.get("highlights", [])
            + trip.get("extras", [])
        )
        text = f"Trip Offer: {trip.get('type')}. Price: {trip.get('price')}. Destinations: {', '.join(trip.get('destinations', []))}. Details: {details}."

        metadata = {
            "category": "trip",
            "type": trip.get("type"),
            "price": trip.get("price"),
        }
        vector_store.add_memory(collection_name, text, metadata)
    logger.info(f"Migrated {len(trips)} Trips.")

    # 4. Migrate FAQs
    faqs = data.get("faq", {})
    for q, a in faqs.items():
        text = f"FAQ: Question: {q} -> Answer: {a}"
        vector_store.add_memory(collection_name, text, {"category": "faq"})
    logger.info(f"Migrated {len(faqs)} FAQs.")

    # 5. Migrate Policy
    policies = data.get("booking_policies", {})
    for category, rules in policies.items():
        text = f"Policy ({category}): {json.dumps(rules, ensure_ascii=False)}"
        vector_store.add_memory(collection_name, text, {"category": "policy"})
    logger.info("Migrated Policies.")

    logger.info("--- Migration Complete ---")


if __name__ == "__main__":
    migrate_data()
