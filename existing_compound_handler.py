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
    existing_compounds = []
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
        outcome = f"According to M-W, the search term you entered is a {compound_type}, '{ce.the_id}', which means that it should not be hyphenated. Its definition is as follows: '"
       
    elif compound_type == "open compound":                
        if ce.part ==  "adjective" or ce.part == "adverb":
            outcome = f"M-W lists the search term you entered as an {compound_type}, '{ce.the_id}'. However, as CMoS 7.85 says, 'it is never incorrect to hyphenate adjectival compounds before a noun.' The term's definition is as follows: '.'"
        else:
            article = get_article(ce.part)
            outcome = f"M-W lists the search term you entered as an {compound_type}, '{ce.the_id}'. Because it is {article} {ce.part}, it should likely be left open in all cases. Its definition is as follows: "
    
    else:
        outcome = existing_hyphenated_compound(ce, compound_from_input)

    return outcome

def in_mw_as_variant(compound_type, ce, compound_from_input):
    article_before_relation = get_article(ce.relation)
    article_before_part = get_article(ce.part)

    if compound_type == "closed compound":
        outcome = f"According to M-W, the search term you entered, '{compound_from_input}', is {article_before_relation} {ce.relation} '{ce.cxt}', which is a {compound_type}. The definition of {ce.cxt} is as follows: '"
                                
    elif compound_type == "open compound":     
        compound_is_open_compound = f"The search term you entered, '{compound_from_input}', is {article_before_relation} {ce.relation} '{ce.cxt}', which is an {compound_type}."           
        if ce.part ==  "adjective" or ce.part == "adverb":
            outcome = compound_is_open_compound + "\n\n" + f"However, as CMoS 7.85 says, 'it is never incorrect to hyphenate adjectival compounds before a noun.' The definition of {ce.cxt} is as follows: .'"
        else:
            outcome = compound_is_open_compound + "\n\n" + f"Because {ce.cxt} is {article_before_part} {ce.part}, it should likely be left open in all cases. The definition of {ce.cxt} is as follows: .'" 
                            
    else:
        outcome = existing_hyphenated_compound(ce, compound_from_input)
    
    return outcome

def existing_hyphenated_compound(ce, compound_from_input):
    adj_caveat = (f'''Although M-W lists the term as a hyphenated compound, it should likely 
    be hyphenated before but not after a noun. As CMoS 7.85 says, 'It is never incorrect to 
    hyphenate adjectival compounds before a noun. When such compounds follow the noun they 
    modify, hyphenation is usually unnecessary, even for adjectival compounds that are 
    hyphenated in Webster's (such as well-read or ill-humored).''')
   
    if ce.entry_type != "main_entry":
        article_before_relation = get_article(ce.relation)
    article_before_part = get_article(ce.part)
    
    compound_is_variant = (f"According to M-W, the search term you entered, ' "
    "'{compound_from_input}', is {article_before_relation} {ce.relation} of "
    "'{ce.cxt}' and is an {ce.part}. You should likely use '{ce.cxt}' instead of ' "
    "'{compound_from_input}.'")

    if ce.part == "adjective" or ce.part == "adverb":
        if ce.entry_type == "variant_or_cxs":
            mw_result = compound_is_variant + "\n\n" + f"The definition of {ce.cxt} is as follows: '" 
        else:
            mw_result = f"M-W lists the term you entered, '{compound_from_input}', as {article_before_part} {ce.part}. Its definition is as follows: ."
        outcome = mw_result + "\n\n" + adj_caveat           
                            
    else:
        if ce.entry_type == "variant_or_cxs":
            outcome = compound_is_variant + "\n\n" + f"Because it is a {ce.part}, it should likely be hyphenated regardless of its position in a sentence. Its definition is as follows: "
        else:
            outcome = f"M-W lists the search term you entered, '{compound_from_input}', as {article_before_part} {ce.part}.' The term should likely be hyphenated regardless of its position in a sentence. Its definition is as follows: "
   
    return outcome
