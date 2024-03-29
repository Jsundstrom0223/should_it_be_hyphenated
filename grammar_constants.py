"""Constants related to CMoS hyphenation guidance and explanations of grammar terms."""
#__________________________________________________________________________________________
#The following constants relate to Chicago Manual of Style rules on specific compounds--
#for example, compounds that end with "percent" ("10 percent") or begin with "least" 
# #("least traveled").

ORDINALS = ['nd', 'rd', 'st', 'th']
PERCENTS = ["percent", "percentage"]
CURRENCY_UNITS = ["dollar", "dollars", "cent", "cents"]
#All units are lowercased because user_input is lowercased in hyphenation_answer
UNITS_OF_MEASUREMENT = [
    "bps", "cal", "cc", "cm", "cps", "d", "dpi", "fps", "ft", "ft.", "g", "gal",
    "gb", "gbps", "gy", "hp", "hz", "iu", "j", "kb", "kbit", "kb", "k", "kbps", "kcal", "kg",
    "khz", "kj", "kl", "km", "kmh", "kmph", "kn", "kw", "kwh", "l", "lb", "m", "mb", "mbps",
    "mg", "ml", "mpg", "mph", "ms", "nm", "oz", "ph", "ppb", "ppm", "ppt", "pt", "qt", "rpm", 
    "s", "sq", "st", "t", "tb", "tbps", "tbsp", "tsp", "v", "w", "wt" 
    ]

CMOS_NUM_DICT = {"PCT": PERCENTS, "CURRENCY": CURRENCY_UNITS, "UNITS": UNITS_OF_MEASUREMENT}

#Some parts of the _compounds template preserve whitespace. Using quotation marks at the start/end of each line prevents the displayed string from breaking at the end of each line but preserves newline characters. https://stackoverflow.com/a/3077017

PCT_OUTCOME = ("According to the Chicago Manual of Style, a single compound consisting" 
" of a number and 'percent' or 'percentage' should not be hyphenated. However, when two"
" percentages are used in a number range before a noun, they should be separated by a"
" hyphen (e.g., 'a 10-20 percent raise'). In either case, the number should be a numeral" 
" rather than a spelled-out number (e.g., '10,' not 'ten'). Lastly, the manual"
" recommends using the word 'percent' in nontechnical contexts and the symbol ('%') in" 
" technical contexts.")

CURRENCY_OUTCOME = ("Spelled-out amounts of money (e.g., 'million dollar' rather than"
" '$1 million') should be hyphenated before a noun ('a million-dollar home') and left open"
" after a noun ('a home worth a million dollars'). Note too that the Chicago Manual of"
" Style recommends spelling out numbers under 100 in most cases; in technical"
" contexts, though, spelling out only single-digit numbers may be more appropriate.")

UNIT_OUTCOME = ("Compounds consisting of a number and an abbreviation"
" (e.g., 'GB,' 'bps,' 'oz,' 'ft.,' etc.) should never be hyphenated. Note too that the"
" number should be written as a numeral (i.e., '10' instead of 'ten').") 
        
CMOS_NUM_OUTCOMES = {"PCT": PCT_OUTCOME, "CURRENCY": CURRENCY_OUTCOME, "UNITS": UNIT_OUTCOME}

FRACTION_GUIDANCE = ("The Chicago Manual of Style recommends spelling out simple fractions and"
                     " states that they should be hyphenated unless the second number is"
                     " hyphenated (e.g., 'one twenty-fifth'). If you choose to use numerals for"
                     " the numbers in a fraction (which may be appropriate in technical contexts),"
                     " the numerator and denominator should be separated by a horizontal bar or a"
                     " slash, and both should be cardinal numbers (e.g., '1/5').")

COMPARATIVE_ADVERBS = ["more", "most", "less", "least", "very"]
ALWAYS_PREFIXES = ["self", "ex", "great"]
SOMETIMES_PREFIXES = [
    "anti",
    "bi",
    "bio",
    "co",
    "counter",
    "cyber",
    "extra",
    "hyper",
    "infra",
    "inter",
    "intra",
    "macro",
    "mega",
    "meta",
    "mid",
    "mini",
    "multi",
    "over",
    "proto",
    "semi",
    "sub",
    "super",
    "supra",
    "ultra",
    "un",
    "under"
    ]

AS_ADJS = ["foster", "near", "half"]
FIRST_ELEMENT_DICT = {"ADVS": COMPARATIVE_ADVERBS, "ALWAYS_PREFIXES": ALWAYS_PREFIXES, "SOMETIMES_PREFIXES": SOMETIMES_PREFIXES, "ADJS": AS_ADJS}

# SECOND_ALWAYS = ["free", "odd"]
# SECOND_ELEMENT_LISTS = [SECOND_ALWAYS]

CMOS_ADVS = ("Compounds consisting of 'more,' 'most,' 'less,' 'least,' or 'very'"
" and an adjective or a participle (e.g., 'a more perfect nation,' 'the least traveled"
" path') do not need to be hyphenated unless there is a risk of misinterpretation.")

CMOS_ALWAYS_PREFIXES = ("With very few exceptions, compounds beginning with the prefixes"
" 'self', 'ex', and 'great' should be hyphenated. The few exceptions apply to 'self,'"
" which should be hyphenated unless it is followed by a suffix (as in 'selfless') or"
" preceded by 'un' (as in 'unselfconscious').")

CMOS_SOMETIMES_PREFIXES = ("A two-word compound that begins with a prefix (e.g., 'cyber,'"
" 'sub,' 'un,' etc.) should generally be closed up--that is, written as one word"
" ('cyberthreat,' 'subfolder,' 'unidiomatic'). However, it should be hyphenated if the"
" second term in the compound is a capitalized word or a numeral or if closing the compound"
" up could cause confusion. Moreover, it is usually best to hyphenate compounds in which the"
" prefix ends with the first letter of the second word (e.g., 'anti-intellectual'), although"
" there are exceptions, such as 'unnecessary.'\n\n")

CMOS_AS_ADJS = ("Certain compounds, such as those beginning with 'foster,' 'near,'"
" and 'half,' are hyphenated when used as adjectives (e.g., 'a near-perfect game,'"
" 'foster-family training,' 'a half-asleep student') but not as verbs ('half listened')" 
" or nouns ('a foster family').")

FIRST_ELEMENT_OUTCOMES = {
    "ADVS": CMOS_ADVS,
    "ALWAYS_PREFIXES": CMOS_ALWAYS_PREFIXES,
    "SOMETIMES_PREFIXES": CMOS_SOMETIMES_PREFIXES,
    "ADJS": CMOS_AS_ADJS
    }

#__________________________________________________________________________________________
#The following constants relate to Chicago Manual of Style hyphenation standards that are
#based on part of speech--for example, standards regarding the hyphenation of noun-adjective
#compounds ("cash-poor").

NUM_SUPERLATIVE = ("A compound formed from an ordinal number and a superlative should be"
                   " hyphenated before a noun (e.g., 'the second-largest database') but"
                   " otherwise left open ('ranked the second largest).")

NUM_NOUN = ("A number-noun compound should be hyphenated before a noun (e.g., 'two-factor"
            " authentication'); otherwise, it should be left open ('authenticate using two"
            " factors').")

BY_PART_NUM = {"SUPERLATIVE": NUM_SUPERLATIVE, "NOUN": NUM_NOUN}

NOUN_NOUN = ("If the elements of a two-noun compound are equal (as in 'city-state' and"
             " 'philosopher-king'), the compound should be hyphenated.\n\nIf the first element"
             " describes the second and the compound is being used as a noun, it should be"
             " written as two words (e.g., 'insider threat'). \n\nHowever, if the compound"
             " precedes a noun and is being used as an adjective, it should be hyphenated."
             " For example, take 'career-transition workshop.' The compound is hyphenated"
             " because 'career' describes 'transition' and 'career transition' describes"
             " 'workshop.'")

NOUN_PARTICIP_INFL = ("A compound formed from a noun and a present or past participle should be"
                      " hyphenated before a noun but otherwise left open (e.g.,"
                      " 'security-focused configuration management' and 'an error-handling"
                      " issue' but 'sound error handling'). If a noun is followed by another"
                      " form of a verb, like the present tense of a verb ('focuses'), the pair"
                      " should be written as two words.")

NOUN_ADJ = ("A noun-adjective compound should be hyphenated before a noun but otherwise"
            " left open (e.g., 'a beginner-friendly interface' but 'designed to be"
            " beginner friendly').")

NOUN_ADV = ("Some noun-adverb compounds, like 'hanger-on,' are hyphenated; however, because"
            " the compound you entered is not in Merriam-Webster's Collegiate® Dictionary, it"
            " should likely be written as two words.")

BY_PART_NOUN = {
    "NOUN": NOUN_NOUN,
    "PARTICIP_INFL": NOUN_PARTICIP_INFL,
    "ADJECTIVE": NOUN_ADJ,
    "ADVERB": NOUN_ADV
    }

VERB_NOUN = ("When a verb-noun pair forms a compound, it is generally closed up (e.g., 'pick'"
             " + 'pocket' = 'pickpocket') and listed in Merriam-Webster's Collegiate® Dictionary"
             " as such; because the verb-noun pair you entered is not in that dictionary, it"
             " should likely be written as two words.")

VERB_ADVERB_OR_PREP = ("Since Merriam-Webster's Collegiate® Dictionary does not list the term you"
                       " entered as an established compound, it should likely be written as two"
                       " words (i.e., left open). There may be edge cases not included in the"
                       " dictionary, though, so read on for a quick word on the treatment of"
                       " verb-adverb and verb-preposition pairs.\n\n"
                       "A verb followed by a preposition or an adverb can be hyphenated, left open,"
                       " or closed up; it all depends on how the pair of words is functioning. Pairs"
                       " that are being used as verbs (i.e., phrasal verbs) are not hyphenated,"
                       " although their noun or adjectival equivalents may be hyphenated or closed"
                       " up. For example, take 'back up.' As a phrasal verb ('back up your files'),"
                       " there's no hyphen. As a noun, the term is written as one word ('data"
                       " backup').")

VERB_OTHER = ("Because the second element of the compound you entered is not an adverb, a"
              " preposition, or a noun, the compound should likely be written as two words.")

BY_PART_VERB = {
    "NOUN": VERB_NOUN,
    "ADVERB": VERB_ADVERB_OR_PREP,
    "PREPOSITION": VERB_ADVERB_OR_PREP,
    "VERB_OTHER": VERB_OTHER
    }

ADJ_PARTICIP = ("An adjective-participle compound should be hyphenated if it appears"
                " before a noun (e.g., 'a hard-coded value'). Otherwise, it should likely"
                " be written as two words.")

ADJ_NOUN = ("An adjective-noun compound should be hyphenated if it appears before a noun"
            " (e.g., 'primary-key error'). Otherwise, it should likely be written as two words.")
            
ADJ_VERB = ("A compound formed from an adjective and a verb should likely be written as"
            " two words. However, if the second element is a participle, the compound"
            " should likely be hyphenated before a noun. (Recall that a participle is a word that's derived from"
            " a verb and functions as an adjective. Many participles end in '-ing' or '-ed.'"
            " Examples include 'running' in the phrase 'running container' and 'documented' in"
            " 'well-documented codebase.')")

BY_PART_ADJ = {"PARTICIPLE": ADJ_PARTICIP, "NOUN": ADJ_NOUN, "VERB": ADJ_VERB}

BY_PART_PARTICIPLE_NOUN = ("A participle-noun compound should be hyphenated before but not after a"
                           " noun (e.g., 'a cutting-edge solution' but 'a solution on the cutting"
                           " edge').")

BY_PART_ADVERB_ADJ_OR_PARTICIP = ("A compound formed from an adverb and an adjective or a participle"
                                  " should be hyphenated if it appears before a noun (e.g.,"
                                  " 'a well-documented codebase'). Otherwise, it should be written"
                                  " as two words (e.g., 'not well documented').")

#__________________________________________________________________________________________
#The following constants define the grammar terms listed on the "Brush Up
# on Your Grammar" page of the Flask app. (They are the "plain English" definitions 
# returned to the user.)

ADJ_DEF = ("An adjective is a word that modifies (describes) a noun or pronoun, such as 'robust'"
           " in 'robust error checks.' Other parts of speech, such as nouns, can also function as"
           " adjectives; for example, in the phrase 'security concerns,' the noun 'security' is"
           " modifying the noun 'concerns' and is therefore functioning as an adjective.")

ADV_DEF = ("An adverb is a word that modifies (describes) a verb, an adjective, or another"
           " adverb. Adverbs answer questions like 'How?' (thoroughly, sufficiently,"
           " securely, etc.) and 'When?' (late, early, etc.).")

COMP_DEF = ("A compound consists of multiple words working together to express a single idea."
            " There are three types of compounds: closed (that is, one word, like 'upstream'), open"  " (two words, like 'web page'), and hyphenated (e.g., 'zero-day'). Some compounds are"
            " always written the same way, but many take different forms depending on their use."
            " For example, as a noun, 'denial of service' should be left open ('experienced a denial"
            " of service'), but as an adjective, it should be hyphenated (a 'denial-of-service"
            " attack').")

NOUN_DEF = ("A noun is a word that names a person, place, or thing. There are two kinds of nouns,"
            " common and proper. Common nouns name generic people, places, or things (e.g.,"
            " 'programming language'), and proper nouns name specific people, places, or things"
            " and are usually capitalized (e.g., 'Python').")

PART_DEF = ("A participle is a word derived from a verb. There are two kinds of participles,"
            " present and past participles. In general, the present participle of a verb is the"
            " '-ing' form of the verb (e.g., 'running'). The past participle of a regular verb"
            " is the simple past tense of the verb, but irregular verbs don't follow that rule."
            " Some irregular verbs (like 'write') have separate past participles ('written,'"
            " not 'wrote'); for others, like ‘run,’ the past participle is the verb’s past tense"
            " and base form.\n\n"
            "Participles are used as adjectives or as part of other tenses. For example, in the"
            " phrase 'a running container,' the participle 'running' is functioning as an"
            " adjective modifying 'container.' In 'We are testing the new functionality,'"
            " 'testing' and 'are' together form the present continuous tense.")

VERB_DEF = ("A verb describes an action (e.g., 'deploy') or a condition or state of being"
            " (e.g., 'need' or 'involve').")

PART_OF_SPEECH_DEFS = {
    "adjective": ADJ_DEF,
    "adverb": ADV_DEF,
    "compound": COMP_DEF,
    "noun": NOUN_DEF,
    "participle": PART_DEF,
    "verb": VERB_DEF
    }

#__________________________________________________________________________________________
#The final constants are lists of parts of speech that the app ignores and parts of speech
#that it considers valid.

IGNORED_PARTS_OF_SPEECH = [
    "abbreviation",
    "auxiliary verb",
    "biographical name",
    "pronunciation spelling",
    "symbol",
    "trademark"
    ]

VALID_PARTS_OF_SPEECH = [
    "adjective",
    "adverb",
    "inflection (conjugated form)",
    "noun",
    "participle",
    "preposition",
    "verb"
    ]
