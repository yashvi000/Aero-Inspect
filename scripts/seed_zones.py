import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.backend.db.session import SessionLocal
from src.backend.db.models.zone import Zone
import json
from src.shared.utils.paths import PROJECT_ROOT

def seed_zones():
    print("Starting zone seed...")
    db = SessionLocal()

    try:
        existing = db.query(Zone).count()
        print(f"Existing zones: {existing}")

        if existing > 0:
            print(f"Zones already seeded ({existing} zones found). Skipping.")
            return

        # Load from zone_definitions.json
        zone_file = PROJECT_ROOT / "src" / "shared" / "zone_definitions.json"
        with open(zone_file, "r") as f:
            data = json.load(f)

        for z in data["zones"]:
            zone = Zone(
                id=z["id"],
                zone_name=z["zone_name"],
                zone_label=z["zone_label"],
                current_status="NOT_INSPECTED",
                color="GRAY"
            )
            db.add(zone)

        db.commit()
        print(f"Successfully seeded {len(data['zones'])} zones.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()

    finally:
        db.close()
        print("Done.")

if __name__ == "__main__":
    seed_zones()