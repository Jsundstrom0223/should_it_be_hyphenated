"""Grammar constant lists"""

ORDINALS = ['nd', 'rd', 'st', 'th']
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
ALWAYS_PREFIXES = ["self", "ex", "great"]
AS_ADJS = ["foster", "near", "half"]
FIRST_ELEMENT_DICT = {"ADVS": COMPARATIVE_ADVERBS, "PREFIXES": ALWAYS_PREFIXES, "ADJS": AS_ADJS}

# SECOND_ALWAYS = ["free", "odd"]
# SECOND_ELEMENT_LISTS = [SECOND_ALWAYS]


ADVS_OUTCOME = (f"Compounds consisting of 'more,' 'most,' 'less,' 'least,' or 'very' " 
f"and an adjective or participle (e.g., 'a more perfect nation,' 'the least traveled path' "
f" do not need to be hyphenated unless there is a risk of misinterpretation.")

PREFIXES_OUTCOME = (f"With very few exceptions, compounds beginning with the prefixes " 
f"'self', 'ex', and 'great' should be hyphenated. (The few exceptions apply to 'self,' "
f"which should be hyphenated unless it is followed by a suffix (as in 'selfless') or "
f"preceded by 'un' (as in 'unselfconscious').")

ADJS_OUTCOME = (f"Certain compounds, such as those beginning with 'foster,' 'near,' "
f"and 'half,' are hyphenated when used as adjectives (e.g.,'a near-perfect game,'"
f"'foster-family training,' 'a half-asleep student') but not as verbs ('half listened') "
f" or nouns ('a foster family').")

FIRST_ELEMENT_OUTCOMES = {"ADVS": ADVS_OUTCOME, "PREFIXES": PREFIXES_OUTCOME, "ADJS": ADJS_OUTCOME}