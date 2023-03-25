"""Grammar constant lists"""

ORDINAL_ENDINGS = ['nd', 'rd', 'st', 'th']
PERCENTS = ["percent", "percentage"]
CURRENCY_UNITS = ["dollar", "dollars", "cent", "cents"]
UNITS_OF_MEASUREMENT = [
    "bps", "Bps", "cal", "Cal", "cc", "cm", "cps", "d", "dpi", "fps", "ft", "ft.", "g", "gal",
    "Gb", "GB", "Gbps", "Gy", "hp", "Hz", "IU", "J", "kb", "kbit", "KB", "K", "Kbps", "kcal", "kg",
    "kHz", "kJ", "kl", "km", "kmh", "kmph", "kn", "kW", "kWh", "L", "lb", "m", "Mb", "MB", "Mbps",
    "mg", "mL", "mpg", "mph", "ms", "nm", "oz", "pH", "ppb", "ppm", "ppt", "pt", "qt", "rpm", 
    "s", "sq", "st", "t", "Tb", "TB", "Tbps", "tbsp", "tsp", "V", "W", "wt" 
    ]
NUM_DICT = {"PCT": PERCENTS, "CURRENCY": CURRENCY_UNITS, "UNITS": UNITS_OF_MEASUREMENT}

COMPARATIVE_ADVERBS = ["more", "most", "less", "least", "very"]
FIRST_ALWAYS = ["self", "ex", "great"]
FIRST_AS_ADJ = ["foster", "near", "half"]
FIRST_ELEMENT_DICT = {"ADV": COMPARATIVE_ADVERBS, "ALWAYS": FIRST_ALWAYS, "ADJ": FIRST_AS_ADJ}

# SECOND_ALWAYS = ["free", "odd"]
# SECOND_ELEMENT_LISTS = [SECOND_ALWAYS]
