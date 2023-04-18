"""Prepare the information that will be returned to the user if the compound is in the dictionary."""
from classes import ExistingCompound

def get_article(next_word):
    vowels = ["a", "e", "i", "o", "u"]
    first_letter = next_word[0]
    if first_letter in vowels:
        article = "an"
    else:
        article = "a"

    return article

def sort_entries(mw_entries, compound):
    for entry in mw_entries:
        if "-" in entry.the_id:
            compound_type = "hyphenated compound"
        else:
            split_k = entry.the_id.split(" ")
            if len(split_k) > 1:
                compound_type = "open compound"
            else:
                compound_type = "closed compound"

        if entry.entry_type == "main_entry":
            entry_outcome = in_mw_as_main_entry(compound_type, 
                entry, compound.full)  
            
            return ExistingCompound(compound.full, compound_type, entry.part, entry.definition, entry_outcome, "found_in_MW")
      
        if entry.entry_type == "variant_or_cxs" or entry.entry_type == "one_diff_cxts":
            entry_outcome = in_mw_as_variant(compound_type, entry, compound.full)

            return ExistingCompound(compound.full, compound_type, entry.part, entry.definition, entry_outcome, "found_in_MW")

def in_mw_as_main_entry(compound_type, ce, compound_from_input):
    if compound_type == "closed compound":
        outcome = (f"Merriam-Webster's Collegiate® Dictionary lists the search term you"
                f" entered as a {compound_type}, '{ce.the_id},' which means that it should be"
                " written as one word (i.e., closed).\n\nIts definition is as follows: ")
       
    elif compound_type == "open compound":                
        if ce.part ==  "adjective" or ce.part == "adverb":
            outcome = (f"Merriam-Webster's Collegiate® Dictionary lists the search term you"
                       f" entered as an {compound_type}, '{ce.the_id}.' However, it should"
                       "likely be hyphenated if it precedes a noun. As the Chicago"
                        " Manual of Style (section 7.85) says, 'it is never incorrect to hyphenate"
                        " adjectival compounds before a noun.'\n\nIts definition is as follows:")
        else:
            article = get_article(ce.part)
            outcome = (f"Merriam-Webster's Collegiate® Dictionary lists the search term you"
                       f" entered as an {compound_type}, '{ce.the_id}.' Because it is {article}"
                       f" {ce.part}, it should likely be left open (written as two words) in all"
                        " cases.\n\nIts definition is as follows: ")
    
    else:
        outcome = existing_hyphenated_compound(ce, compound_from_input)

    return outcome

def in_mw_as_variant(compound_type, ce, compound_from_input):
    article_before_relation = get_article(ce.relation)
    article_before_part = get_article(ce.part)

    if compound_type == "closed compound":
        outcome = ("Merriam-Webster's Collegiate® Dictionary lists the search term you entered,"
                   f" '{compound_from_input},' as {article_before_relation} {ce.relation} "
                   f" '{ce.cxt}', which is a {compound_type}. As such, it should be written as"
                   f" one word.\n\nThe definition of '{ce.cxt}' is as follows:")
                            
    elif compound_type == "open compound":     
        open_compound = ("Merriam-Webster's Collegiate® Dictionary lists the search term you"
                         f" entered, '{compound_from_input},' as {article_before_relation}"
                         f" {ce.relation} '{ce.cxt},' which is an open (unhyphenated)"
                         " compound.\n\n")
        
        if ce.part ==  "adjective" or ce.part == "adverb":
            outcome = (f"{open_compound}However, because the compound is an {ce.part}, it should"
                       " likely be hyphenated when used before a noun. As the Chicago Manual of"
                       " Style (section 7.85) says, 'it is never incorrect to hyphenate adjectival"
                       f" compounds before a noun.'\n\nThe definition of '{ce.cxt}' is as follows:")
        else:
            outcome = (f"{open_compound}Because '{ce.cxt}' is {article_before_part} {ce.part}, it"
                       " should likely be left open (written as two words) in all cases.\n\nThe"
                       f" definition of '{ce.cxt}' is as follows:")
                            
    else:
        outcome = existing_hyphenated_compound(ce, compound_from_input)
    
    return outcome

def existing_hyphenated_compound(ce, compound_from_input):
    adj_caveat = ("Although the dictionary lists the term as a hyphenated compound, it should"
                  " likely be hyphenated before but not after a noun. As the Chicago Manual of" 
                  " Style (section 7.85) says, 'It is never incorrect to hyphenate adjectival"
                  " compounds before a noun. When such compounds follow the noun they modify,"
                  " hyphenation is usually unnecessary, even for adjectival compounds that are" 
                  " hyphenated in Webster's (such as well-read or ill-humored).'\n\n")
   
    if ce.entry_type != "main_entry":
        article_before_relation = get_article(ce.relation)
        comp_is_variant = ("According to Merriam-Webster's Collegiate® Dictionary, the search term"
                       f" you entered, '{compound_from_input},' is {article_before_relation}"
                       f" {ce.relation} of '{ce.cxt}' and is {article_before_part} {ce.part}."
                       f"You should likely use '{ce.cxt}' instead of '{compound_from_input}.'\n\n")
    article_before_part = get_article(ce.part)
    
    if ce.part == "adjective" or ce.part == "adverb":
        if ce.entry_type == "variant_or_cxs":
            outcome = f"{comp_is_variant} {adj_caveat}The definition of '{ce.cxt}' is as follows: '" 
        else:
            outcome = (f"Merriam-Webster's Collegiate® Dictionary lists the search term you"
                       f" entered, '{compound_from_input},' as {article_before_part} {ce.part}."
                       f" {adj_caveat}Its definition is as follows:")
    
    else:
        if ce.entry_type == "variant_or_cxs":
            outcome = (f"{comp_is_variant}Because it is {article_before_part} {ce.part},"
                       " it should likely be hyphenated regardless of its position in a"
                       " sentence.\n\nIts definition is as follows: ")
        else:
            outcome = ("Merriam-Webster's Collegiate® Dictionary lists the search term you"
                       f" entered, '{compound_from_input},' as {article_before_part} {ce.part}."
                       " The term should likely be hyphenated regardless of its position in a"
                       " sentence.\n\nIts definition is as follows: ")
   
    return outcome
