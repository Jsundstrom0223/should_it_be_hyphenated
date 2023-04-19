"""Prepare the results that are returned when the user's compound is in the dictionary."""
from classes import ExistingCompound

def get_article(next_word):
    """Get the article that should precede a noun in an f-string expression."""
    vowels = ["a", "e", "i", "o", "u"]
    first_letter = next_word[0]
    if first_letter in vowels:
        article = "an"
    else:
        article = "a"

    return article

def check_compound_type(entry, compound):
    """Check the type of the existing compound and the associated MW entry.

    Arguments:
    entry: Entry information returned by start_parsing (an instance of the StandardEntry
    or Nonstandard class).
    compound: A named tuple with four named fields. Holds information about the
    user-provided compound and alternate versions (open and closed versions) of it.

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

def in_mw_as_main_entry(compound_type, entry, compound):
    """Prepare information on open and closed compounds in main dictionary entries.
    
    Arguments:
    compound_type: A variable indicating the type of the existing compound (open, closed,
    or hyphenated).
    entry: Entry information returned by start_parsing (an instance of the StandardEntry class).
    compound: A named tuple with four named fields. Holds information about the
    user-provided compound and alternate versions (open and closed versions) of it.

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
    user-provided compound and alternate versions (open and closed versions) of it.

    Returns:
    outcome: A string summarizing the dictionary entry and explaining whether the
    compound should be hyphenated.
    """
    article_before_relation = get_article(entry.relation)
    article_before_part = get_article(entry.part)
    before_a_noun = ["adjective", "adverb", "noun"]

    if compound_type == "closed compound":
        outcome = ("Merriam-Webster's Collegiate® Dictionary lists the search term you entered,"
                   f" '{compound.full},' as {article_before_relation} {entry.relation} "
                   f" '{entry.cxt},' which is a {compound_type}. As such, it should be written as"
                   f" one word.\n\nThe definition of '{entry.cxt}' is as follows:")

    elif compound_type == "open compound":
        comp_is_open = ("Merriam-Webster's Collegiate® Dictionary lists the search term you"
                         f" entered, '{compound.full},' as {article_before_relation}"
                         f" {entry.relation} '{entry.cxt},' which is an open (unhyphenated)"
                         " compound.\n\n")

        if entry.part in before_a_noun:
            outcome = (f"{comp_is_open}However, because the compound is a {article_before_part} {entry.part}, it"
                       " should likely be hyphenated when used before a noun. As the Chicago"
                       " Manual of Style (section 7.85) says, 'it is never incorrect to hyphenate"
                       f" adjectival compounds before a noun.'\n\nThe definition of '{entry.cxt}'"
                       " is as follows:")
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
    user-provided compound and alternate versions (open and closed versions) of it.

    Returns:
    outcome: A string summarizing the dictionary entry and explaining whether the
    compound should be hyphenated.
    """
    adj_caveat = ("Although the dictionary lists the term as a hyphenated compound, it should"
                  " likely be hyphenated before but not after a noun. As the Chicago Manual of"
                  " Style (section 7.85) says, 'It is never incorrect to hyphenate adjectival"
                  " compounds before a noun. When such compounds follow the noun they modify,"
                  " hyphenation is usually unnecessary, even for adjectival compounds that are" 
                  " hyphenated in Webster's (such as well-read or ill-humored).'\n\n")

    if entry.entry_type != "main_entry":
        article_before_relation = get_article(entry.relation)
        comp_is_variant = ("According to Merriam-Webster's Collegiate® Dictionary, the search term"
                       f" you entered, '{compound.full},' is {article_before_relation}"
                       f" {entry.relation} of '{entry.cxt}' and is {article_before_part}"
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
