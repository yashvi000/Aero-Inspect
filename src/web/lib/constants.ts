import zoneData from "../../shared/zone_definitions.json";

// Format: "code - zone_label" (e.g. "5330 - Fuselage Skin / Plate")
export const ZONES = zoneData.zones.map(
  (z) => `${z.code} - ${z.zone_label}`
);

export const INSPECTION_TYPES = [
  "GVI — General Visual",
  "DVI — Detailed Visual",
  "SDI — Special Detailed",
];

export const DEFECT_TYPES = ["Crack", "Corrosion", "Scratch", "Dent", "Paint"];

export const ZONE_DEFINITIONS = zoneData.zones;