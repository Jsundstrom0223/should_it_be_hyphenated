from collections import namedtuple
import grammar_constants
from classes import Compound

##PRONOUNS!!!!


def check_first_element_lists(compound):
    print(compound, "COMPOUND?!!! GRAMMAR!!")
    
    ele_answer_ready = False
    ele_outcome = None
    in_first_element_lists = [k for k,v in grammar_constants.FIRST_ELEMENT_DICT.items() if
        compound.elements[0] in v]

    if in_first_element_lists:
        ele_answer_ready = True
        the_list = in_first_element_lists[0]
        ele_outcome =  grammar_constants.FIRST_ELEMENT_OUTCOMES[the_list]
        # ele_outcome = check_first_element(the_list)


    return ele_answer_ready, ele_outcome

def check_cmos_num_rules(compound, idx_and_type):
    print(idx_and_type, "IN GRAMMAR PY!")
    
    print("\n\n\n GRAMMAR PY SPLIT COM", compound.elements)
    Num_Results = namedtuple('Num_Results', ['num_answer_ready', 'num_outcome'])
    # print(f"\n\n\ ORDINAL", ordinal)
    
    num_answer_ready = False
    num_outcome = None

    if len(idx_and_type) == 2:
     
       
        standard_fraction_guidance = "CMoS recommends spelling out simple fractions and states that they should be hyphenated unless the second number is hyphenated (e.g., 'one twenty-fifth'). If you choose to use numerals for the numbers in a fraction (which may be appropriate in technical contexts), the numerator and denominator should be separated by a horizontal bar or a slash, and both should be cardinal numbers (e.g., 1/5)."
        if idx_and_type[0] == "cardinal":
            correct_fraction = f"The input you entered, {compound.full}, appears to be a simple fraction. "
            num_outcome = correct_fraction + standard_fraction_guidance

        elif idx_and_type[0] in grammar_constants.ORDINALS and idx_and_type[1] in grammar_constants.ORDINALS:
            print(idx_and_type[0], "IN ORD!!!!", compound.elements)
            two_ordinals =  f"The input you entered, {compound.full}, appears to be a fraction, but it consists of two ordinal numbers (e.g., '10th' instead of '10'). Although the denominator in a spelled-out fraction can be an ordinal ('one-fifth'), the numerator should not be. "
            num_outcome = two_ordinals + "\n" + standard_fraction_guidance
    
        else:
            numerator_ord =  f"The input you entered, {compound.full}, appears to be a fraction, but the numerator is an ordinal number (e.g., '10th' instead of '10'). Although the denominator in a spelled-out fraction can be an ordinal ('one-fifth'), the numerator should not be. If the input is not intended to be a fraction--i.e., the first element is meant to describe the second, as in 'the first two years of life'--the compound should not be hyphenated."
            num_outcome = numerator_ord + "\n" + standard_fraction_guidance


            
    elif idx_and_type.get(0) == "cardinal":
        print("0 IS CARD!!!!!!!", idx_and_type)
    
        #in_num_lists will never be longer than 1
        in_num_lists = [k for k,v in grammar_constants.NUM_DICT.items() if compound.elements[1] in v]

        if in_num_lists:    
        
            if in_num_lists[0] == "UNITS":
                num_outcome = "Compounds consisting of a number and an abbreviated unit of measurement should never be hyphenated. Note too that the number should be written as a numeral."
        
            if in_num_lists[0] == "CURRENCY":
                num_outcome = "Spelled-out amounts of money (e.g., 'million dollar' rather than '$1 million') should be hyphenated before a noun ('a million-dollar home') and left open after a noun ('a home worth a million dollars'). Also recall that the Chicago Manual recommends spelling out numbers under 100 in most cases; in technical contexts, though, spelling out only single-digit numbers may be more appropriate."

            if in_num_lists[0] == "PCT":
                num_outcome = "Compounds consisting of a number and 'percent' or 'percentage' should not be hyphenated. However, when used in a number range before a noun, percentages should be separated by a hyphen (e.g., 'a 10-20 percent raise.')"
       
    
    if num_outcome is not None:
        num_answer_ready = True
    
    num_results = Num_Results(num_answer_ready, num_outcome)
 
    return num_results

def in_mw_as_main_entry(compound_type, ce, compound_from_input):
    if compound_type == "closed compound":
        outcome = f"According to M-W, the search term you entered is a {compound_type}, '{ce.the_id}', which means that it should not be hyphenated. Its definition is as follows: '{ce.definition[ce.part]}.'"
       
    elif compound_type == "open compound":                
        if ce.part ==  "adjective" or ce.part == "adverb":
            outcome = f"M-W lists the search term you entered as an {compound_type}, '{ce.the_id}'. However, as CMoS 7.85 says, 'it is never incorrect to hyphenate adjectival compounds before a noun.' The term's definition is as follows: '{ce.definition[ce.part]}.'"
        else:
            outcome = f"M-W lists the search term you entered as an {compound_type}, '{ce.the_id}'. Because it is a/an {ce.part}, it should likely be left open in all cases. Its definition is as follows: '{ce.definition[ce.part]}."
    
    else:
        outcome = handle_hyphenated_variant(ce, compound_from_input)
                        
    return outcome

def in_mw_as_variant(compound_type, ce, compound_from_input):
    if compound_type == "closed compound":
        outcome = f"According to M-W, the search term you entered, '{compound_from_input}', is a/an {ce.cr_type} '{ce.cxt}', which is a {compound_type}. The definition of {ce.cxt} is as follows: '{ce.definition[ce.part]}.'"
                                
    elif compound_type == "open compound":                
        if ce.part ==  "adjective" or ce.part == "adverb":
            outcome = f"The search term you entered, '{compound_from_input}', is a/an {ce.cr_type} of {ce.cxt}, which is an {compound_type}. However, as CMoS 7.85 says, 'it is never incorrect to hyphenate adjectival compounds before a noun.' The definition of {ce.cxt} is as follows: '{ce.definition[ce.part]}.'"
        else:
            outcome = f"The search term you entered, '{compound_from_input}', is a/an {ce.cr_type} of {ce.cxt}, which is an {compound_type}. Because {ce.cxt} is a/an {ce.part}, it should likely be left open in all cases. The definition of {ce.cxt} is as follows: '{ce.definition[ce.part]}.'" 
                            
    else:
        outcome = handle_hyphenated_variant(ce, compound_from_input)
    
    return outcome

def handle_hyphenated_variant(ce, compound_from_input):
    adj_caveat = f"Although M-W lists the term as a hyphenated compound, it should likely be hyphenated before but not after a noun.\n" 
    f"As CMoS 7.85 says, 'It is never incorrect to hyphenate adjectival compounds before a noun. When such compounds follow the noun they modify, hyphenation is usually unnecessary, even for adjectival compounds that are hyphenated in Webster's (such as well-read or ill-humored).'"
   
    if ce.part == "adjective" or ce.part == "adverb":
        if ce.part_type == "variant" or ce.part_type == "cxs_entry" or ce.part_type == "one_of_diff_parts":
            mw_result = f"According to M-W, the search term you entered, '{compound_from_input}', is a/an {ce.cr_type} of '{ce.cxt}' and is an {ce.part}. You should likely use '{ce.cxt}' instead of '{compound_from_input}. The definition of {ce.cxt} is as follows: '{ce.definition[ce.part]}.'" 
        else:
            mw_result = f"M-W lists the search term you entered, '{compound_from_input}', as a/an {ce.part} meaning {ce.definition[ce.part]}."
        outcome = mw_result + "\n" + adj_caveat           
                            
    else:
        if ce.part_type == "variant" or ce.part_type == "cxs_entry" or ce.part_type == "one_of_diff_parts":
            outcome = f"According to M-W, the search term you entered, '{compound_from_input}', is a/an {ce.cr_type} of '{ce.cxt}' and is an {ce.part}. You should likely use '{ce.cxt}' instead of '{compound_from_input}' and hyphenate it regardless of where it appears in a sentence. Its definition is as follows: '{ce.definition[ce.part]}'."
        else:
            outcome = f"M-W lists the search term you entered, '{compound_from_input}', as a/an {ce.part} meaning\n '{ce.definition[ce.part]}.' It should likely be hyphenated regardless of its position in a sentence."
   
    return outcome

def cmos_rules(item):
    final_outcome = "There are no Chicago Manual of Style standards regarding the compound you entered, and the compound is not in the dictionary. The compound should likely be left open regardless of its position in a sentence." 
    
    if item[0] == "number":
        for ending in grammar_constants.ORDINALS:
            if Compound.compound.elements_of_compound[0].endswith(ending):
                ordinal = True
                          
        
        if ordinal and item[1] == "superlative":
        
            final_outcome = "A compound formed from an ordinal number and a superlative should be hyphenated before but not after a noun (e.g., 'the second-best player' but 'ranked the second best)."
        elif item[1] == "noun":
            final_outcome = "A number-noun compound should be hyphenated before but not after a noun (e.g., 'a two-year contract' but 'contracted for two years)."
        # else:
        #     final_outcome = "NUMBER!!!!!"
       
    if item[0] == "noun":
        # print(item[1])
        # if item[1] == "inflection (conjugated form)":
        #     final_outcome= 
        if item[1] == "noun":
            final_outcome = "If the elements of a two-noun compound are equal (as in 'city-state' and 'philosopher-king'), the compound should be hyphenated. If the first element modifies the second (e.g., 'restaurant owner') and the compound is being used as a noun, it should be left open. If the compound precedes a noun and is being used as an adjective, it should be hyphenated (e.g., 'a career-transition workshop,' in which 'career' modifies 'transition')."

        if item[1] == "past tense and past participle of" or item[1] == "participle" or item[1] == "inflection (conjugated form)":
            final_outcome = "A compound formed from a noun and a present or past participle should be hyphenated before but not after a noun (e.g., 'a light-filled room,' 'a mouth-watering meal'). If the second element of the compound is another form of a verb, like the present tense of a verb ('waters'), the coompound should likely be left open."
        
        if item[1] == "adjective":
            final_outcome = "A noun-adjective compound should be hyphenated if it precedes a noun, as in 'a cash-poor homeowner.'"

        # if item[1] == "abbreviation":
        #     final_outcome = "prob not"

        if item[1] == "adverb":
            final_outcome = "Some noun-adverb compounds, like 'hanger-on', are hyphenated; however, because the compound you entered is not in Merriam-Webster's Collegiate® Dictionary, it should likely be left open."

    if item[0] == "verb" or item[0] == "inflection (conjugated form)":
        if item[1] == "noun":
    
            final_outcome = "When a verb-noun pair forms a compound, it is generally closed up (e.g., 'pick' + 'pocket' = 'pickpocket') and listed in Merriam-Webster's Collegiate® Dictionary as such; because the verb-noun pair you entered is not in that dictionary, it should likely be left open."
        elif item[1] == "adverb" or item[1] == "preposition":
            final_outcome = "Since Merriam-Webster's Collegiate® Dictionary does not list the term you entered as a compound, it should likely be left open. There may be edge cases not included in the dictionary, though, so read on for a quick word on the treatement of verb-adverb and verb-preposition pairs.\n A verb followed by a preposition or adverb can be hyphenated, left open, or closed up; it all depends on how the pair of words is functioning. Pairs that are used as verbs (i.e., phrasal verbs) are not hyphenated, although their noun or adjectival equivalents can be hyphenated or closed up. For example, take 'break down.' As a phrasal verb--'I'm worried that my car will break down'--there's no hyphen. As a noun, the term is closed up ('There was a breakdown in negotiations.') If the second word in the pair is a two-letter particle like 'by', 'in', or 'up', a hyphen is likely appropriate."
        else:
            final_outcome = "Because the second element of the compound you entered is not an adverb, preposition, or noun, the compound should likely be left open."
         
    if item[0] == "adjective":
        if item[1] == "noun" or item[1] == "past tense and past participle of" or item[1]== "participle":
            
            final_outcome= "If the term appears before a noun, it should be hypehanted. Otherwise, it should probably be left open. (For example, 'a tight-lipped witness' but 'a witness who remained tight lipped'; 'a short-term solution' but 'a solution in the short term.')"
        if item[1] == "verb" or item[1] == "inflection (conjugated form)":
            ##TO-DO: Better example
            final_outcome = "If the verb in your compound is an irregular verb like 'run,' the past participle of which is also 'run,' the compound may be hyphenated before a noun. Otherwise, it should likely be left open."

    if item[0] == "past tense and past participle of" or item[0] == "participle" and item[1] == "noun":
        ###DOES THIS COVER PRESENT PARTICIPES?
        final_outcome = "A participle-noun compound should be hyphenated before but not after a noun (e.g., 'a cutting-edge solution' but 'on the cutting edge')."

    if item[0] == "adverb" and item[1] == "past tense and past participle of" or item[1] == "adjective" or item[1] == "participle":
        
        final_outcome = "The term should be hyphenated if it appears before a noun (e.g., 'well-lit room'). Otherwise, leave it open ('The room is well lit')."

  
    return final_outcome

