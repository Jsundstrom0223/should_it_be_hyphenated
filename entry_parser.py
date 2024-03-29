"""Parse the individual dictionary entries in an API response.

Functions:
-get_entry_id
-get_entry_definition
-is_def_duplicate
-is_part_duplicate
-get_cxt_search_term
-cognate_cross_reference
-standard_main_entry
-main_entry_with_cxs
-var_inf_or_stem
-check_alt_forms
-is_variant
-variant_entry
-is_inflection
-inflection_entry
-is_stem
-stem_entry
-get_stem_defs
-main_entry_with_cxs
"""
from classes import StandardEntry, Nonstandard
from grammar_constants import IGNORED_PARTS_OF_SPEECH

def get_entry_id(entry):
    """Get the ID (headword or homograph) of an M-W entry returned by the API."""
    entry_id = entry.get('meta').get('id')
    if ":" in entry_id:
        the_id = entry_id.split(":")[0]
    else:
        the_id = entry_id

    return the_id

def get_entry_definition(entry):
    """Get the definition of an M-W entry returned by the API.
    
    If a shortdef field (i.e., a field listing only the definitions for the first three senses)
    is available, get the shortdef value instead of the full definition.
    """
    raw_def = entry.get('shortdef')
    if raw_def is None:
        raw_def = entry.get('def')

    def_of_term = "; ".join(raw_def)

    return def_of_term

def is_def_duplicate(mw_entries, definition):
    """Check whether the definition of the entry to be added to mw_entries is unique.
    
    Two dictionary entries in an API response can contain the same definition. 
    In those cases, the second entry should not be added to mw_entries.
    
    Arguments:
    mw_entries: A list of StandardEntry and Nonstandard class instances--i.e., 
    entry information that will be returned to the user.
    definition: The definition being checked.

    Returns:
    dupe_def: A boolean value. True means that the definition is a duplicate.
    """
    dupe_def = False
    for i in mw_entries:
        for _, v in i.definition.items():
            if v == definition:
                dupe_def = True
               
    return dupe_def

def is_part_duplicate(mw_entries, part_of_speech, definition):
    """Check whether the part of speech of the entry to be added to mw_entries is unique.
    
    If the entry has the same part of speech as an existing standard entry in mw_entries, 
    combine the two entries. Ignore nonstandard entries because they include additional
    information that should not be combined.
    
    Arguments:
    mw_entries: A list of StandardEntry and Nonstandard class instances--i.e., 
    entry information that will be returned to the user.
    part_of_speech: The part of speech being checked.
    definition: The definition of the entry.

    Returns: 
    dupe_part: A boolean value. True means that the definition is a duplicate.
    """
    dupe_part = False
    standards = [entry for entry in mw_entries if entry.entry_type == "main_entry" and 
                 entry.part == part_of_speech]

    ##Shouldn't be more than two duplicates in a single API response
    for i in standards:
        if i.part == part_of_speech:
            combined_defs = "; ".join([i.definition[part_of_speech], definition[part_of_speech]])
            i.definition[part_of_speech] = combined_defs
            dupe_part = True
   
    return dupe_part

def get_cxt_search_term(cxt):
    """Get the search term that will be used in an additional API call.
    
    Check whether that search term (the value of an entry's cxt field) includes a colon
    and split it if so. Also check whether it is two words; if it is, URL encode the space character. (See cognate_cross_reference's docstring for additional info.)
    
    Argument: 
    cxt: The entry's cxt field, which indicates the term being referenced in the entry.
    
    Returns:
    cxt_search_term: The search term to be used in the new API query.
    cxt_only: The value of the cxt field, without any colons or numerals.
    """
    if ":" in cxt:
        cxt_only = cxt.split(":")[0]
    else:
        cxt_only = cxt

    split_id = cxt_only.split(" ")
    if len(split_id) > 1:
        cxt_search_term = split_id[0] + "%20" + split_id[1]
    else:
        cxt_search_term = cxt_only

    return cxt_search_term, cxt_only

def cognate_cross_reference(the_id, cxs_mw_response, mw_entries, cxt_only, cxs):
    """Parse information on a dictionary entry's cross-reference target (CXT).
    
    Get the definition and part of speech of an entry's CXT and create an instance of the 
    Nonstandard class for the entry.

    (If an entry for a word (X) has a cxs field, the word is a less common spelling or
    a form of another word, its cxt. The entry for X may not have its own definition or part
    of speech field. In that case, the API will be called to retrieve entries for the CXT.)

    Arguments:
    the_id: The headword of an entry (the term being defined).
    cxs_mw_response: The API's response to a new query in which the entry's CXT is 
    the search term.
    mw_entries: A list of StandardEntry and Nonstandard class instances--i.e., 
    entry information that will be returned to the user.
    cxt_only: The value of the cxt field, without any colons or numerals.
    cxs: The entry's cxs field.
    """
    cxl = cxs[0].get('cxl')
    cxs_defs = {}
    part_of_speech = None
    entry_type = "variant_or_cxs"

    for entry in cxs_mw_response:
        part_of_speech = entry.get('fl')
        #If the original search term is a verbal inflection (e.g., "lit"), retrieve only verb 
        # definitions.
        if "tense" in cxl or "participle" in cxl:
            if part_of_speech == "verb":
                cxs_target_def = get_entry_definition(entry)
                dupe_def = is_def_duplicate(mw_entries, cxs_target_def)
                if not dupe_def:
                    cxs_defs[part_of_speech] = cxs_target_def
                break
        else:
            if part_of_speech in IGNORED_PARTS_OF_SPEECH:
                continue

            cxs_target_def = get_entry_definition(entry)
            if cxs_target_def:
                cxs_defs[part_of_speech] = cxs_target_def
                dupe_def = is_def_duplicate(mw_entries, cxs_target_def)
                if not dupe_def:
                    cxs_defs[part_of_speech] = cxs_target_def

    for k, v in cxs_defs.items():
        mw_entries.append(Nonstandard(the_id, entry_type, k, {k:v}, cxt_only, cxl))

def standard_main_entry(the_id, entry, mw_entries, part_of_speech):
    """Handle standard complete entries.

    Arguments:
    the_id: The headword of the entry (the term being defined).
    entry: A dictionary entry returned by the API.
    mw_entries: A list of StandardEntry and Nonstandard class instances--i.e., 
    entry information that will be returned to the user.
    part_of_speech: The part of speech of the headword.
    """
    def_of_term = get_entry_definition(entry)
    definition = {part_of_speech: def_of_term}
    stems = entry['meta'].get('stems')

    dupe_part = is_part_duplicate(mw_entries, part_of_speech, definition)
    if not dupe_part:
        dupe_def = is_def_duplicate(mw_entries, def_of_term)
        if not dupe_def:
            StandardEntry.stems_and_parts[part_of_speech] = stems
            mw_entries.append(StandardEntry(the_id, "main_entry", part_of_speech, definition))

def main_entry_with_cxs(the_id, entry, mw_entries, part_of_speech, cxs):
    """Handle entries that have their own part of speech and definition + a cxs field.
    
    Arguments:
    the_id: The headword of the entry (the term being defined).
    entry: A dictionary entry returned by the API.
    mw_entries: A list of StandardEntry and Nonstandard class instances--i.e., 
    entry information that will be returned to the user.
    part_of_speech: The part of speech of the headword.
    cxs: The entry's cxs field.
    """
    cxl = cxs[0].get('cxl')
    cxt = cxs[0].get('cxtis')[0]['cxt']

    def_of_term = get_entry_definition(entry)
    if def_of_term:
        dupe_def = is_def_duplicate(mw_entries, def_of_term)
        if not dupe_def:
            definition = {part_of_speech: def_of_term}
            entry_type = "variant_or_cxs"
            mw_entries.append(Nonstandard(the_id, entry_type, part_of_speech, definition, cxt, cxl))

def var_inf_or_stem(the_id, search_term, entry, mw_entries, part_of_speech):
    """Handle entries that list the search term as an inflection, variant, or stem.

    If the search term (X) is a less common spelling or a conjugated form of another word (Y),
    M-W may return the entry for Y (with Y's ID), with X listed as a variant, inflection, or
    stem of Y.
    For more information, see the following documentation:
    https://github.com/Jsundstrom0223/should_it_be_hyphenated/blob/main/api_explanation.md.

    Arguments:
    the_id: The headword of the entry (the term being defined).
    search_term: The search term used in the API call (an element of the compound).
    entry: A dictionary entry returned by the API.
    mw_entries: A list of StandardEntry and Nonstandard class instances--i.e., 
    entry information that will be returned to the user.
    part_of_speech: The part of speech of the headword.
    """
    add = False
    vrs = entry.get('vrs')
    inflections = entry.get('ins')
    stems = entry['meta'].get('stems')
   
    if vrs is None and inflections is None and stems is None:
        return

    if vrs is not None:
        term_is_variant = is_variant(vrs, search_term)
        if term_is_variant:
            add, stem_defs, relation = variant_entry(entry, vrs, mw_entries, part_of_speech)
    elif inflections is not None:
        term_is_inflection, inf_label = is_inflection(inflections, search_term)
        if term_is_inflection:
            add, stem_defs, relation = inflection_entry(entry, inf_label, mw_entries, part_of_speech)
    else:
        term_is_stem = is_stem(stems, search_term)
        if term_is_stem:
            add, stem_defs, relation = stem_entry(entry, mw_entries, part_of_speech)

    if not add:
        return

    #A single term can be a variant, inflection, stem, or cognate cross-reference of multiple terms; if it has the same relation to multiple terms (i.e., is a less common spelling of them), some entry information may be combined.
    entry_type = "variant_or_cxs"
    if relation in Nonstandard.relations.keys():
        for part in stem_defs.keys():
            existing_entry = Nonstandard.relations[relation]
            if existing_entry.part == part:
                if the_id != existing_entry.cxt:
                    new_cxt = existing_entry.cxt + " and " + the_id
                    existing_entry.cxt = new_cxt
                    existing_entry.entry_type = "one_diff_cxts"
                    mw_entries.append(Nonstandard(the_id, "one_diff_cxts", part, stem_defs,
                                                   new_cxt, relation))
                break
            mw_entries.append(Nonstandard(the_id, entry_type, part, stem_defs, the_id, relation))

    else:
        for part in stem_defs.keys():
            mw_entries.append(Nonstandard(the_id, entry_type, part, stem_defs, the_id, relation))

def check_alt_forms(search_term_chars, field_value):
    """Check whether an entry's va, inf, or stems field contains a form of the search term.
    
    Arguments:
    search_term: The search term used in the API call (an element of the compound).
    field_value: The va, inf, or stems field of an entry.

    Returns:
    match: A boolean value. True means that the search term is a variant, inflection, or
    stem of an open or hyphenated compound.
    """
    match = False
    splitters = [" ", "-"]
    for splitter in splitters:
        if not match:
            for i, _ in enumerate(search_term_chars):
                first_ele = "".join(search_term_chars[: i+1])
                second_ele = "".join(search_term_chars[i + 1:])
                both = first_ele + splitter + second_ele
                if both == field_value:
                    match = True

    return match

def is_variant(vrs, search_term):
    """Check whether a dictionary entry's va field contains the search term.
    
    Arguments:
    vrs: The vrs (variants) field of an entry.
    search_term: The search term used in the API call (an element of the compound).
    
    Returns:
    term_is_variant: A boolean. True means that the field contains the search term.
    """
    vrs = vrs[0]
    term_is_variant = False
    if "*" in vrs['va']:
        va = vrs['va'].replace("*", "")
    else:
        va = vrs['va']

    if va == search_term:
        term_is_variant = True
    else:
        to_check = list(search_term)
        term_is_variant = check_alt_forms(to_check, va)

    return term_is_variant

def variant_entry(entry, vrs, mw_entries, part_of_speech):
    """Get the information that is displayed to the user when the search term is a variant.
    
    Arguments:
    entry: A dictionary entry returned by the API.
    vrs: The vrs (variants) field of an entry.
    mw_entries: A list of StandardEntry and Nonstandard class instances--i.e., 
    entry information that will be returned to the user.
    part_of_speech: The part of speech of the headword.
    
    Returns:
    add: A boolean value. True means that a Nonstandard class instance should be
    created for the entry.
    stem_defs: The headword's definition(s).
    relation: The search term's relationship to the headword (or a modified version of it).
    """
    relation = None
    vrs = vrs[0]
    vl = vrs.get('vl')
    vl_options = {
        "or less commonly": "less common spelling of",
        "or": "alternative spelling of", 
        "or chiefly British": "chiefly British spelling of"}

    if vl in vl_options.keys():
        relation = vl_options[vl]
    else:
        if vl not in vl_options.keys() or vl is None:
            relation = "variant of"

    add, stem_defs = get_stem_defs(entry, mw_entries, part_of_speech)

    return add, stem_defs, relation

def is_inflection(inflections, search_term):
    """Check whether a dictionary entry's inf field contains the search term.

    Arguments:
    inflections: The ins (inflections) field of an entry.
    search_term: The search term used in the API call (an element of the compound).
    
    Returns:
    term_is_inflection: A boolean. True means that the field contains the search term.
    inf_label: The il field (the search term's relationship to the headword).
    """
    term_is_inflection = False
    inf_label = None

    for i in inflections:
        inf = i.get('if')
        if inf is None:
            continue
        if "*" in inf:
            inf = inf.replace("*", "")
        if inf == search_term:
            inf_label = i.get('il')
            term_is_inflection = True
            break

        to_check = list(search_term)
        term_is_inflection = check_alt_forms(to_check, inf)

    return term_is_inflection, inf_label

def inflection_entry(entry, inf_label, mw_entries, part_of_speech):
    """Get the information that is displayed to the user when the search term is an inflection.
    
    Arguments:
    entry: A dictionary entry returned by the API.
    inf_label: The search term's relationship to the headword (e.g.,
    'present tense plural of').
    mw_entries: A list of StandardEntry and Nonstandard class instances--i.e., 
    entry information that will be returned to the user.
    part_of_speech: The part of speech of the headword.

    Returns:
    add: A boolean value. True means that a Nonstandard class instance should be
    created for the entry.
    stem_defs: The headword's definition(s).
    relation: The search term's relationship to the headword (or a modified version of it).
    """
    relation = None

    if part_of_speech == "verb":
        if inf_label is None or inf_label == "or":
            relation = "inflection (conjugated form) of"
        else:
            relation = inf_label
    else:
        relation = "variant of"

    add, stem_defs = get_stem_defs(entry, mw_entries, part_of_speech)

    return add, stem_defs, relation

def is_stem(stems, search_term):
    """Check whether a dictionary entry's stems field contains the search term.
    
    Arguments:
    stems: The stems field of an entry.
    search_term: The search term used in the API call (an element of the compound).
    
    Returns:
    term_is_stem: A boolean. True means that the field contains the search term.
    """
    term_is_stem = False
    if search_term in stems:
        term_is_stem = True
    else:
        to_check = list(search_term)

        for stem in stems:
            if not term_is_stem:
                term_is_stem = check_alt_forms(to_check, stem)

    return term_is_stem

def stem_entry(entry, mw_entries, part_of_speech):
    """Get the information that is displayed to the user when the search term is an inflection.

    Arguments:
    entry: A dictionary entry returned by the API.
    mw_entries: A list of StandardEntry and Nonstandard class instances--i.e., 
    entry information that will be returned to the user.
    part_of_speech: The part of speech of the headword.

    Returns:
    add: A boolean value. True means that a Nonstandard class instance should be
    created for the entry.
    stem_defs: The headword's definition(s).
    relation: The search term's relationship to the headword (or a modified version of it).
    """
    relation = None
    cxs = entry.get('cxs')
    if cxs is not None:
        relation = cxs[0].get('cxl')
    if relation is None:
        relation = "variant of"

    add, stem_defs = get_stem_defs(entry, mw_entries, part_of_speech)
    return add, stem_defs, relation

def get_stem_defs(entry, mw_entries, part_of_speech):
    """Retrieve definitions of variants, inflections, and stems.

    Although the function's name is get_stem_defs, it also retrieves the
    definitions of words that are variants or inflections or another word,
    since variants and inflections are also considered stems.

    Arguments:
    entry: A dictionary entry returned by the API.
    mw_entries: A list of StandardEntry and Nonstandard class instances--i.e., 
    entry information that will be returned to the user.
    part_of_speech: The part of speech of the headword.

    Returns:
    add: A boolean value. True means that a Nonstandard class instance should be
    created for the entry.
    stem_defs: The headword's definition(s).
    """
    add = False
    stem_defs = None

    def_of_term = get_entry_definition(entry)

    if def_of_term:
        dupe_def = is_def_duplicate(mw_entries, def_of_term)
        if not dupe_def:
            stem_defs = {part_of_speech: def_of_term}
            add = True

    return add, stem_defs
