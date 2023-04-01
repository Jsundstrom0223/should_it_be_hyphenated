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

PCT_OUTCOME = '''According to the Chicago Manual of Style, a single compound consisting  
of a number and 'percent' or 'percentage' should not be hyphenated. However, when two 
percentages are used in a number range before a noun, they should be separated by a hyphen 
(e.g., 'a 10-20 percent raise'). In either case, the number should be a numeral rather than 
a spelled-out number (e.g., '10,' not 'ten'). Lastly, the manual recommends using the word 
'percent' in nontechnical contexts and the symbol ('%') in technical contexts.'''

CURRENCY_OUTCOME = '''Spelled-out amounts of money (e.g., 'million dollar' rather than 
'$1 million') should be hyphenated before a noun ('a million-dollar home') and left open 
after a noun ('a home worth a million dollars'). Note too that the Chicago Manual of Style 
recommends spelling out numbers under 100 in most cases; in technical contexts, though, 
spelling out only single-digit numbers may be more appropriate.'''

UNIT_OUTCOME = '''Compounds consisting of a number and an abbreviated unit of measurement 
(e.g., 'GB,' 'bps,' 'oz,' 'ft.,' etc.) should never be hyphenated. Note too that the 
number should be written as a numeral (i.e., '10' instead of 'ten').''' 
        
NUM_OUTCOMES = {"PCT": PCT_OUTCOME, "CURRENCY": CURRENCY_OUTCOME, "UNITS": UNIT_OUTCOME}


COMPARATIVE_ADVERBS = ["more", "most", "less", "least", "very"]
ALWAYS_PREFIXES = ["self", "ex", "great"]
AS_ADJS = ["foster", "near", "half"]
FIRST_ELEMENT_DICT = {"ADVS": COMPARATIVE_ADVERBS, "PREFIXES": ALWAYS_PREFIXES, "ADJS": AS_ADJS}

# SECOND_ALWAYS = ["free", "odd"]
# SECOND_ELEMENT_LISTS = [SECOND_ALWAYS]

ADVS_OUTCOME = '''Compounds consisting of 'more,' 'most,' 'less,' 'least,' or 'very' 
and an adjective or participle (e.g., 'a more perfect nation,' 'the least traveled path' 
f" do not need to be hyphenated unless there is a risk of misinterpretation.'''

PREFIXES_OUTCOME = '''With very few exceptions, compounds beginning with the prefixes 
'self', 'ex', and 'great' should be hyphenated. The few exceptions apply to 'self,' 
which should be hyphenated unless it is followed by a suffix (as in 'selfless') or 
preceded by 'un' (as in 'unselfconscious').''' 

ADJS_OUTCOME = '''Certain compounds, such as those beginning with 'foster,' 'near,' 
and 'half,' are hyphenated when used as adjectives (e.g.,'a near-perfect game,' 
'foster-family training,' 'a half-asleep student') but not as verbs ('half listened') 
or nouns ('a foster family').'''

FIRST_ELEMENT_OUTCOMES = {"ADVS": ADVS_OUTCOME, "PREFIXES": PREFIXES_OUTCOME, "ADJS": ADJS_OUTCOME}

ADJ_DEF = '''An adjective is a word that modifies (describes) a noun or pronoun, such as 
'robust' in 'robust error checks.' Other parts of speech, such as nouns, can also function 
as adjectives; for example, in the phrase 'security concerns,' the noun 'security' modifies 
the noun 'concerns' and is therefore functioning as an adjective.'''

ADV_DEF = '''An adverb is a word that modifies (describes) a verb, an adjective, or another 
adverb. Adverbs answer questions like 'how?' (e.g., 'thoroughly,' 'sufficiently,' 'securely,' 
etc.) and 'when?' (e.g., 'late,' 'early,' etc.). '''

COMP_DEF = '''A compound consists of multiple words working together to express a single idea. 
There are three types of compounds: closed (e.g., 'upstream'), open (e.g., 'web page'), and 
hyphenated (e.g., 'zero-day'). While some compounds are always written the same way, many 
compounds change on the basis of context and use. For example, as a noun, 'denial of service' 
should be left open ('suffered a denial of service'), but as an adjective, it should be 
hyphenated (a 'denial-of-service attack').'''

NOUN_DEF = '''A noun is a word that names a person, place, or thing. There are two kinds of 
nouns, common and proper. Common nouns name generic people, places, or things (e.g., 
'programming language'), and proper nouns name specific people, places, or things and 
are usually capitalized (e.g., 'Python').'''

PART_DEF = '''A participle is a word that is derived from a verb and is used as a modifier. 
There are two kinds of participles, present and past participles. In general, the present 
participle of a verb is the '-ing' form of the verb (e.g., 'testing'). The past participle 
of a regular verb is the simple past tense of the verb, but irregular verbs (like 'write') 
tend to have separate past participles ('written,' not 'wrote'). 

Participles are used as adjectives or as part of other tenses. For example, in the phrase 
'testing pipeline,' the participle 'testing' is functioning as an adjective modifying 
'pipeline.' In 'We are testing the new functionality,' 'testing' and 'are' together 
form the present continuous tense.'''

VERB_DEF = '''A verb is a word that describes an action (e.g., 'to deploy') or a state 
or state of being (e.g., 'to need' or 'to involve').'''


PART_OF_SPEECH_DEFS = {"adjective": ADJ_DEF, "adverb": ADV_DEF, "compound": COMP_DEF, "noun": NOUN_DEF, "participle": PART_DEF, "verb": VERB_DEF}
