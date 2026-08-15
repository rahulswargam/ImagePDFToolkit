"""Design tokens shared between QSS (ui/styles.py) and Python layout code.

Centralizing these as plain ints means spacing/radius/type-scale values are
defined once instead of hardcoded independently in every f-string and every
layout.setContentsMargins()/setSpacing() call.
"""

# Spacing scale (px).
SPACE_1 = 4
SPACE_2 = 8
SPACE_3 = 12
SPACE_4 = 16
SPACE_5 = 20
SPACE_6 = 24
SPACE_7 = 32
SPACE_8 = 40

# Corner radius scale (px).
RADIUS_SM = 8
RADIUS_MD = 12
RADIUS_LG = 16
RADIUS_XL = 20

# Type scale (px).
FONT_DISPLAY = 32
FONT_HEADING = 20
FONT_SUBHEAD = 16
FONT_BODY = 14
FONT_META = 12

# Icon sizing (px) — square, passed to ui.icons.get_icon(..., size=...).
ICON_SM = 16
ICON_MD = 20
ICON_LG = 24
