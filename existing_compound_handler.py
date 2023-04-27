"""Prepare the results that are returned when the user's compound is in the dictionary."""
from classes import ExistingCompound

def parse_existing_comps(existing_comps, compound):
    """Begin the process of parsing dictionary entries for existing compounds.
    
    Arguments:
    existing_comps: A list of StandardEntry and Nonstandard class instances--i.e., information
    about dictionary entries.
    compound: A named tuple with four named fields. Holds information about the
    user-provided compound and open and closed versions of it.
    
    Returns:
    outcome: A list of strings summarizing the entries for existing compounds and explaining 
    whether the compounds should be hyphenated.
    """
    outcome = []
    if len(existing_comps) > 1:
        unique_entries = get_unique_entries(existing_comps)
        for unique_entry in unique_entries:
            outcome.append(check_compound_type(unique_entry, compound))
    
    if len(existing_comps) == 1:
        outcome.append(check_compound_type(existing_comps[0], compound))
    
    return outcome

def get_unique_entries(existing_comps):
    """Check existing_comps for duplicate entries and return all unique entries."""
    defs_only = [i.definition for i in existing_comps if i.entry_type == "main_entry"]
    entry_and_def = {i: i.definition for i in existing_comps if i.entry_type == "main_entry"}

    for comp_entry in existing_comps:
        if comp_entry.definition not in defs_only:
            entry_and_def[comp_entry] = comp_entry.definition
            
    unique_entries = [k for k in entry_and_def.keys()]

    return unique_entries

def check_compound_type(entry, compound):
    """Check the type of the existing compound and the associated MW entry.

    Arguments:
    entry: Entry information returned by start_parsing (an instance of the StandardEntry
    or Nonstandard class).
    compound: A named tuple with four named fields. Holds information about the
    user-provided compound and open and closed versions of it.

    Returns:
    An instance of the ExistingCompound class.
    """
    if "-" in entry.the_id:
        compound_type = "hyphenated compound"
    else:
        split_k = entry.the_id.split(" ")
        if len(split_k) > 1:
            compound_type = "open compound"
        else:
            compound_type = "closed compound"

    if entry.entry_type == "main_entry":
        entry_outcome = in_mw_as_main_entry(compound_type, entry, compound)

        return ExistingCompound(compound.full, compound_type, entry.part, entry.definition,
                                entry_outcome, "found_in_MW")

    if entry.entry_type == "variant_or_cxs" or entry.entry_type == "one_diff_cxts":
        entry_outcome = in_mw_as_variant(compound_type, entry, compound)

        return ExistingCompound(compound.full, compound_type, entry.part, entry.definition,
                                entry_outcome, "found_in_MW")

def get_article(next_word):
    """Get the article that should precede a noun in an f-string expression."""
    vowels = ["a", "e", "i", "o", "u"]
    first_letter = next_word[0]
    if first_letter in vowels:
        article = "an"
    else:
        article = "a"

    return article

def in_mw_as_main_entry(compound_type, entry, compound):
    """Prepare information on open and closed compounds in main dictionary entries.
    
    Arguments:
    compound_type: A variable indicating the type of the existing compound (open, closed,
    or hyphenated).
    entry: Entry information returned by start_parsing (an instance of the StandardEntry class).
    compound: A named tuple with four named fields. Holds information about the
    user-provided compound and open and closed versions of it.

    Returns:
    outcome: A string summarizing the dictionary entry and explaining whether the
    compound should be hyphenated.
    """
    before_a_noun = ["adjective", "adverb", "noun"]

    if compound_type == "closed compound":
        outcome = (f"Merriam-Webster's Collegiate® Dictionary lists the search term you"
                f" entered as a {compound_type}, '{entry.the_id},' which means that it should be"
                " written as one word.\n\nIts definition is as follows: ")

    elif compound_type == "open compound":
        if entry.part in before_a_noun:
            outcome = ("Merriam-Webster's Collegiate® Dictionary lists the search term you"
                       f" entered as an {compound_type}, '{entry.the_id}.' However, it should"
                       " likely be hyphenated if it precedes a noun. As the Chicago Manual of"
                       " Style (section 7.85) says, 'it is never incorrect to hyphenate"
                       " adjectival compounds before a noun.'\n\nIts definition is as follows:")
        else:
            article = get_article(entry.part)
            outcome = ("Merriam-Webster's Collegiate® Dictionary lists the search term you"
                       f" entered as an {compound_type}, '{entry.the_id}.' Because it is {article}"
                       f" {entry.part}, it should likely be left open in all"
                        " cases.\n\nIts definition is as follows: ")

    else:
        outcome = existing_hyphenated_compound(entry, compound)

    return outcome

def in_mw_as_variant(compound_type, entry, compound):
    """Prepare information on open and closed compounds in nonstandard dictionary entries.
    
    Arguments:
    compound_type: A variable indicating the type of the existing compound (open, closed,
    or hyphenated).
    entry: Entry information returned by start_parsing (an instance of the Nonstandard class).
    compound: A named tuple with four named fields. Holds information about the
    user-provided compound and open and closed versions of it.

    Returns:
    outcome: A string summarizing the dictionary entry and explaining whether the
    compound should be hyphenated.
    """
    article_before_relation = get_article(entry.relation)
    article_before_part = get_article(entry.part)
    before_a_noun = ["adjective", "adverb", "noun"]

    if compound_type == "closed compound":
        outcome = ("Merriam-Webster's Collegiate® Dictionary lists the search term you entered,"
                   f" '{compound.full},' as {article_before_relation} {entry.relation}"
                   f" '{entry.cxt},' which is a {compound_type}. As such, it should be written as"
                   f" one word.\n\nThe definition of '{entry.cxt}' is as follows:")

    elif compound_type == "open compound":
        comp_is_open = ("Merriam-Webster's Collegiate® Dictionary lists the search term you"
                         f" entered, '{compound.full},' as {article_before_relation}"
                         f" {entry.relation} '{entry.cxt},' which is an open (unhyphenated)"
                         " compound.\n\n")

        if entry.part in before_a_noun:
            outcome = (f"{comp_is_open}However, because the compound is {article_before_part}"
                       f" {entry.part}, it should likely be hyphenated if it precedes a noun."
                       " As the Chicago Manual of Style (section 7.85) says, 'it is never"
                       " incorrect to hyphenate adjectival compounds before a noun.'\n\n"
                       f" The definition of '{entry.cxt}' is as follows:")
        else:
            outcome = (f"{comp_is_open}Because '{entry.cxt}' is {article_before_part}"
                       f" {entry.part}, it should likely be left open in all cases.\n\nThe"
                       f" definition of '{entry.cxt}' is as follows:")

    else:
        outcome = existing_hyphenated_compound(entry, compound)

    return outcome

def existing_hyphenated_compound(entry, compound):
    """Prepare information about hyphenated compounds.
    
    Check the part of speech of the entry and the entry type. Then prepare the information
    that will be returned to the user.
    
    Arguments:
    entry: Entry information returned by start_parsing (an instance of the StandardEntry or
    Nonstandard class). 
    compound: A named tuple with four named fields. Holds information about the
    user-provided compound and open and closed versions of it.

    Returns:
    outcome: A string summarizing the dictionary entry and explaining whether the
    compound should be hyphenated.
    """
    adj_caveat = ("\n\nAlthough the dictionary lists the term as a hyphenated compound, it should"
                  " likely be hyphenated before but not after a noun. As the Chicago Manual of"
                  " Style (section 7.85) says, 'It is never incorrect to hyphenate adjectival"
                  " compounds before a noun. When such compounds follow the noun they modify,"
                  " hyphenation is usually unnecessary, even for adjectival compounds that are" 
                  " hyphenated in Webster's (such as well-read or ill-humored).'\n\n")

    if entry.entry_type != "main_entry":
        article_before_relation = get_article(entry.relation)
        comp_is_variant = ("According to Merriam-Webster's Collegiate® Dictionary, the search term"
                       f" you entered, '{compound.full},' is {article_before_relation}"
                       f" {entry.relation} '{entry.cxt}' and is {article_before_part}"
                       f" {entry.part}. You should likely use '{entry.cxt}' instead of"
                       f" '{compound.full}.'\n\n")

    article_before_part = get_article(entry.part)

    if entry.part == "adjective" or entry.part == "adverb":
        if entry.entry_type == "variant_or_cxs":
            outcome = f"{comp_is_variant} {adj_caveat}The definition of '{entry.cxt}' is as follows: '"
        else:
            outcome = (f"Merriam-Webster's Collegiate® Dictionary lists the search term you"
                       f" entered, '{compound.full},' as {article_before_part} {entry.part}."
                       f" {adj_caveat}Its definition is as follows:")

    else:
        if entry.entry_type == "variant_or_cxs":
            outcome = (f"{comp_is_variant}Because it is {article_before_part} {entry.part},"
                       " it should likely be hyphenated regardless of its position in a"
                       " sentence.\n\nIts definition is as follows: ")
        else:
            outcome = ("Merriam-Webster's Collegiate® Dictionary lists the search term you"
                       f" entered, '{compound.full},' as {article_before_part} {entry.part}."
                       " The term should likely be hyphenated regardless of its position in a"
                       " sentence.\n\nIts definition is as follows: ")

    return outcome

def format_outcome_header(compound_types, compound):
    """Format the header that will be displayed if the compound is in the dictionary.
    
    Arguments:
    compound_types: A list of variables indicating the type(s) of the existing 
    compound(s) (open, closed, or hyphenated).
    compound: The 'compound' named tuple created in hyphenation_answer.

    Returns:
    header: The header that will be displayed to the user.
    """
    if len(compound_types) == 1:
        header = f'''Merriam-Webster's Collegiate® Dictionary lists '{compound.full}' as 
        {compound_types[0]}. Details on the compound and an explanation of whether it should be hyphenated are provided below.'''

    else:
        if len(compound_types) == 2:
            final_types = " and ".join(compound_types)
        if len(compound_types) > 2:
            compound_types.insert(1, ", ")
            compound_types.insert(-1, ", and ")
            final_types = "".join(compound_types)

        header = f'''Merriam-Webster's Collegiate® Dictionary lists '{compound.full}' as 
        {final_types}. This means that the treatment of the term depends on its use. Details are provided below.'''
    
    return header