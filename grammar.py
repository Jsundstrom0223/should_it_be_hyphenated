"""Handle grammar-related checks and prepare the grammar explanations returned to the user."""

from collections import namedtuple
from grammar_constants import (ADJ_NOUN_OR_PARTICIP, ADJ_VERB,
BY_PART_ADVERB_ADJ_OR_PARTICIP, BY_PART_NOUN, BY_PART_PARTICIPLE_NOUN, BY_PART_VERB,
CMOS_NUM_DICT, CMOS_NUM_OUTCOMES, FIRST_ELEMENT_DICT, FIRST_ELEMENT_OUTCOMES,
FRACTION_GUIDANCE, NUM_SUPERLATIVE, NUM_NOUN, ORDINALS)

def check_first_element_lists(compound):
    """Check whether any word-specific Chicago Manual standards apply to the compound.
    
    Check whether the first element of the compound appears in any of the "first element" 
    lists in grammar_constants.py (the values of the FIRST_ELEMENT_DICT dictionary). 
    
    Argument:
    compound: The 'compound' named tuple created in hyphenation_answer.

    Returns:
    ele_answer_ready: A boolean. False means that there are no Chicago Manual of Style
    standards regarding the first element of the compound. 
    outcome: If ele_answer_ready is True, the Chicago Manual of Style standard that
    explains whether the compound should be hyphenated. Otherwise, None.
    """
    ele_answer_ready = False; ele_outcome = None
    in_first_element_lists = [k for k,v in FIRST_ELEMENT_DICT.items() if
        compound.elements[0] in v]
    
    if len(in_first_element_lists) > 0:
        ele_answer_ready = True
        the_list = in_first_element_lists[0]
        if the_list == 'SOMETIMES_PREFIXES':
            outcome_details = sometimes_hyphenated_prefixes(compound)
            ele_outcome = FIRST_ELEMENT_OUTCOMES[the_list] + outcome_details
        else:
            ele_outcome =  FIRST_ELEMENT_OUTCOMES[the_list]

    return ele_answer_ready, ele_outcome

def sometimes_hyphenated_prefixes(compound):
    end_of_prefix = compound.elements[0][-1]
    other_ele_first_letter = compound.elements[1][0]
    if end_of_prefix != other_ele_first_letter:
        outcome_details = (f"Because the prefix in your compound, '{compound.elements[0]}', does not"
                            f" end with '{other_ele_first_letter},' the first letter of the second word,"
                            f" it should likely be closed up ('{compound.closed}').")
    else:
        outcome_details = (f"Because the prefix in your compound, {compound.elements[0]}, ends"
                           f" with '{other_ele_first_letter},' the first letter of the second word,"
                            " it should likely be hyphenated in all cases.")
        
    return outcome_details

def check_cmos_num_rules(compound, idx_and_type):
    """Check whether any number-specific Chicago Manual standards apply to the compound.
    
    Check whether the compound is a fraction. If it is not and the first element of the
    compound is a cardinal number (e.g., "10" instead of "10th"), check whether the 
    second element appears in any of the "units" lists in grammar_constants.py (the values
    of the CMOS_NUM_DICT dictionary). 

    Arguments:
    compound: The 'compound' named tuple created in hyphenation_answer.
    idx_and_type: A dictionary that identifies the numeric element(s) of the compound.

    Returns:
    num_results: A named tuple with four named fields
        1. answer_ready: A boolean. False means that the user needs to provide more 
        information on the compound's use. 
        2. outcome: If ele_answer_ready is True, the Chicago Manual of Style standard 
        that explains whether the compound should be hyphenated. Otherwise, None.
        3. outcome_type: A variable indicating the type of that information; necessary because the _compounds template displays different results in different ways.
        4. header: A summary of that information or, in some cases, an empty string.
    """
    Num_Results = namedtuple('Num_Results', ['answer_ready', 'outcome', 'outcome_type', 'header'])

    answer_ready = False
    outcome = None
    outcome_type = "standard"
    header = ""

    if len(idx_and_type) == 2:
        if idx_and_type[0] == "cardinal":
            correct_fraction = (f"The input you entered, {compound.full}, appears to be"
            " a simple fraction.")
            outcome = correct_fraction + FRACTION_GUIDANCE

        elif idx_and_type[0] in ORDINALS and idx_and_type[1] in ORDINALS:
            two_ordinals =  (f"The input you entered, {compound.full}, appears to be"
            " a fraction, but it consists of two ordinal numbers (e.g., '10th' instead"
            " of '10'). Although the denominator in a spelled-out fraction can be an"
            " ordinal ('one-fifth'), the numerator should not be.")
            outcome = two_ordinals + "\n\n" + FRACTION_GUIDANCE

        else:
            numerator_ord = (f"The input you entered, {compound.full}, appears to be"
            " a fraction, but the numerator is an ordinal number (e.g., '10th' instead"
            " of '10'). Although the denominator in a spelled-out fraction can be an"
            " ordinal ('one-fifth'), the numerator should not be. If the input is not" 
            " intended to be a fraction--i.e., the first element is meant to describe"
            " the second, as in 'the first two years of life'--the compound should not"
            " be hyphenated.")
            outcome = numerator_ord + "\n\n" + FRACTION_GUIDANCE

    elif idx_and_type.get(0) == "cardinal":
        #in_num_lists will never be longer than 1
        in_num_lists = [k for k,v in CMOS_NUM_DICT.items() if compound.elements[1] in v]

        if in_num_lists:
            the_list = in_num_lists[0]
            outcome =  CMOS_NUM_OUTCOMES[the_list]

    if outcome is not None:
        answer_ready = True
        header = '''According to Chicago Manual of Style hyphenation standards,
         your compound should be handled as follows:'''

    num_results = Num_Results(answer_ready, outcome, outcome_type, header)

    return num_results

def cmos_rules(selected):
    """Check the parts of speech selected by the user and retrieve the relevant outcome.
    
    Argument:
    selected: A list of the parts of speech selected by the user.

    Returns:
    final_outcome: An explanation of whether the compound should be hyphenated.
    final_header: The header displayed along with the final outcome or, in some cases,
    an empty string.
    """
    final_outcome = None
    final_header = '''According to Chicago Manual of Style hyphenation standards,
     your compound should be handled as follows:'''
   
    if selected[0] == "number":
        if selected[1] == "superlative":
            final_outcome = NUM_SUPERLATIVE
        if selected[1] == "noun":
            final_outcome = NUM_NOUN

    if selected[0] == "noun":
        if "participle" in selected[1] or selected[1] == "inflection (conjugated form)":
            key = "PARTICIP_INFL"
        else:
            key = selected[1].upper()

        for k,v in BY_PART_NOUN.items():
            if k == key:
                final_outcome = v

    if selected[0] == "verb" or selected[0] == "inflection (conjugated form)":
        key = selected[1].upper()
        if key in BY_PART_VERB.keys():
            final_outcome = BY_PART_VERB[key]
        else:
            final_outcome = BY_PART_VERB["VERB_OTHER"]

    if selected[0] == "adjective":
        if selected[1] == "noun" or "participle" in selected[1]:
            final_outcome= ADJ_NOUN_OR_PARTICIP
        if selected[1] == "verb" or selected[1] == "inflection (conjugated form)":
            final_outcome = ADJ_VERB

    if "participle" in selected[0] and selected[1] == "noun":
        final_outcome = BY_PART_PARTICIPLE_NOUN

    if selected[0] == "adverb" and selected[1] == "adjective" or selected[0] == "adverb" and "participle" in selected[1]:
        final_outcome = BY_PART_ADVERB_ADJ_OR_PARTICIP

    if final_outcome is None:
        final_outcome = ("There are no Chicago Manual of Style standards regarding"
        " the compound you entered, and the compound is not in the dictionary. The"
        " compound should likely be left open (i.e., written as two words) regardless"
        " of its position in a sentence.")
        final_header = ""
    
    return final_outcome, final_header
