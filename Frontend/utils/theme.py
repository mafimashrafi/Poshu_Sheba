"""Single source of truth for the vet.ai color palette.

Every color used in the frontend must come from this strict set — no other
hex values should be introduced elsewhere in the app.
"""

PRIMARY = "#1F6F5C"        # buttons, active links, icons
PRIMARY_HOVER = "#2C8C74"  # hover/pressed states
MINT = "#E4F2ED"           # card backgrounds, pills, highlighted sections
NAVY = "#0F2A3D"           # headings and logo text
SLATE = "#4A5A63"          # body/paragraph text
BG = "#F7FAF9"             # page background
BORDER = "#DCE8E3"         # borders and dividers
AMBER = "#E8A33D"          # urgency/warning indicators only
RED = "#D9534F"            # critical/emergency alerts only

PRIMARY_TINT = "rgba(31, 111, 92, 0.10)"
AMBER_TINT = "rgba(232, 163, 61, 0.14)"
RED_TINT = "rgba(217, 83, 79, 0.12)"
NAVY_SHADOW = "rgba(15, 42, 61, 0.08)"
