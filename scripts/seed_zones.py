import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.backend.db.session import SessionLocal
from src.backend.db.models.zone import Zone

zones = [
    {"id": "zone_01", "zone_name": "nose_section",          "zone_label": "Nose Section"},
    {"id": "zone_02", "zone_name": "cockpit",               "zone_label": "Cockpit"},
    {"id": "zone_03", "zone_name": "left_fwd_fuselage",     "zone_label": "Left Forward Fuselage"},
    {"id": "zone_04", "zone_name": "right_fwd_fuselage",    "zone_label": "Right Forward Fuselage"},
    {"id": "zone_05", "zone_name": "left_wing_root",        "zone_label": "Left Wing Root"},
    {"id": "zone_06", "zone_name": "right_wing_root",       "zone_label": "Right Wing Root"},
    {"id": "zone_07", "zone_name": "left_wing_tip",         "zone_label": "Left Wing Tip"},
    {"id": "zone_08", "zone_name": "right_wing_tip",        "zone_label": "Right Wing Tip"},
    {"id": "zone_09", "zone_name": "left_engine",           "zone_label": "Left Engine Pylon"},
    {"id": "zone_10", "zone_name": "right_engine",          "zone_label": "Right Engine Pylon"},
    {"id": "zone_11", "zone_name": "left_aft_fuselage",     "zone_label": "Left Aft Fuselage"},
    {"id": "zone_12", "zone_name": "right_aft_fuselage",    "zone_label": "Right Aft Fuselage"},
    {"id": "zone_13", "zone_name": "tail_section",          "zone_label": "Tail Section"},
    {"id": "zone_14", "zone_name": "left_horizontal_stab",  "zone_label": "Left Horizontal Stabiliser"},
    {"id": "zone_15", "zone_name": "right_horizontal_stab", "zone_label": "Right Horizontal Stabiliser"},
]

print("Starting zone seed...")

db = SessionLocal()

try:
    existing = db.query(Zone).count()
    print(f"Existing zones: {existing}")
    
    if existing > 0:
        print(f"Zones already seeded ({existing} zones found). Skipping.")
    else:
        for z in zones:
            zone = Zone(
                id=z["id"],
                zone_name=z["zone_name"],
                zone_label=z["zone_label"],
                current_status="NOT_INSPECTED",
                color="GRAY"
            )
            db.add(zone)
        db.commit()
        print(f"Successfully seeded {len(zones)} zones.")

except Exception as e:
    print(f"Error: {e}")
    db.rollback()

finally:
    db.close()
    print("Done.")