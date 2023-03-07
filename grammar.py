import grammar_constants
from collections import namedtuple

def check_first_element_lists(split_compound_from_input):
    Ele_Results = namedtuple('Ele_Results', ['ele_answer_ready', 'ele_outcome'])

    ele_answer_ready = False
    ele_outcome = None

    in_first_element_lists = [k for k,v in grammar_constants.FIRST_ELEMENT_DICT.items() if split_compound_from_input[0] in v]

    if in_first_element_lists:
        the_list = in_first_element_lists[0]
        ele_answer_ready = True
        ele_outcome = check_first_element(split_compound_from_input, the_list)
    
    ele_results = Ele_Results(ele_answer_ready, ele_outcome)
    return ele_results

def check_first_element(split_compound_from_input, the_list):

    if the_list == "ADV":
        ele_outcome = "Compounds consisting of 'more,' 'most,' 'less,' 'least,' or 'very' and an adjective or participle (e.g., 'a more perfect nation,' 'the least traveled path' ) do not need to be hyphenated unless there is a risk of misinterpretation."
    
    if the_list == "ALWAYS":
        ele_outcome = f"With very few exceptions, compounds beginning with the prefixes 'self', 'ex', and 'great' should be hyphenated. (The few exceptions apply fo 'self', which should be hyphenated unless it is followed by a suffix (as in 'selfless') or preceded by 'un' (as in 'unselfconscious')."

    if the_list == "ADJ":
        ele_outcome = f"Certain compounds, such as those beginning with 'foster,' 'near,' and 'half,' are hyphenated when used as adjectives (e.g.,'a near-perfect game,''foster-family training,' 'a half-asleep student') but not as verbs ('half listened') or nouns ('a foster family')."
    
    return ele_outcome

def number_in_compound(split_compound_from_input):
    Num_Results = namedtuple('Num_Results', ['num_answer_ready', 'num_outcome'])
    
    num_answer_ready = False
    num_outcome = None

    if split_compound_from_input[0].isnumeric() and split_compound_from_input[1].isnumeric():
        num_outcome = f"The input you entered, {'-'.join(split_compound_from_input)} appears to be a simple fraction. CMoS recommends spelling out simple fractions and states that they should generally be hyphenated unless the second number is hyphenated (e.g., 'one twenty-fifth')."
    
    else:
        in_num_lists = [k for k,v in grammar_constants.NUM_DICT.items() if split_compound_from_input[1] in v]

        if in_num_lists[0] == "UNITS":
            num_outcome = f"Compounds consisting of a number and an abbreviated unit of measurement should never be hyphenated. Note too that the number should be written as a numeral."
    
        if in_num_lists[0] == "CURRENCY":
            num_outcome = f"Spelled-out amounts of money (e.g., 'million dollar' rather than '$1 million') should be hyphenated before a noun ('a million-dollar home') and left open after a noun ('a home worth a million dollars'). Also recall that the Chicago Manual recommends spelling out numbers under 100 in most cases; in technical contexts, though, spelling out only single-digit numbers may be more appropriate."

        if in_num_lists[0] == "PCT":
            num_outcome = f"Compounds consisting of a number and 'percent' or 'percentage' should not be hyphenated. However, when used in a number range before a noun, percentages should be separated by a hyphen (e.g., 'a 10-20 percent raise.')"
    
    if num_outcome is not None:
        num_answer_ready = True
    
    num_results = Num_Results(num_answer_ready, num_outcome)
 
    return num_results
     
def cmos_rules(item):
    print(f" IN CMOS!")
    final_outcome = "COMING SOON"
    if item[0] == "noun":
        if item[1] == "noun":
            final_outcome = "always if equal (city-state, philosopher-king); as adj if first modifies second e.g. 'a career-change seminar,' in which 'career' describes the change"

        if item[1] == "past tense and past participle of" or item[1] == "participle":
            final_outcome = "yes if before a noun; e.g. a light-filled room or mouth-watering meal; otherwise open (the meal was mouth watering)"
        
        if item[1] == "adjective":
            final_outcome = "if before a noun as in 'a cash-poor homeowner'"

        if item[1] == "abbreviation":
            final_outcome = "prob not"

        if item[1] == "adverb":
            final_outcome = "almost never"

    if item[0] == "verb":
        if item[1] == "noun":
    
            final_outcome = "When a verb-noun pair forms a compound, it is generally closed up (e.g., 'pick' + 'pocket' = 'pickpocket') and listed in Merriam-Webster's Collegiate® Dictionary as such; because the verb-noun pair you entered is not in that dictionary, it should likely be left open."
        elif item[1] == "adverb" or item[1] == "preposition":
            final_outcome = "Since Merriam-Webster's Collegiate® Dictionary does not list the term you entered as a compound, it should likely be left open. There may be edge cases not included in the dictionary, though, so read on for a quick word on the treatement of verb-adverb and verb-preposition pairs.\n A verb followed by a preposition or adverb can be hyphenated, left open, or closed up; it all depends on how the pair of words is functioning.Pairs that are used as verbs (i.e., phrasal verbs) are not hyphenated, although their noun or adjectival equivalents can be hyphenated or closed up. For example, take 'break down.' As a phrasal verb--'I'm worried that my car will break down'--there's no hyphen. As a noun, the term is closed up ('There was a breakdown in negotiations.') \n Note tooIf the second word in the pair is a two-letter particle like 'by', 'in', or 'up', a hyphen is likely appropriate."
        else:
            final_outcome = "PROB NO"
         
    if item[0] == "adjective":
        if item[1] == "noun" or item[1] == "past tense and past participle of" or item[1]== "participle":
            
            final_outcome= "If the term appears before a noun, it should be hypehanted. Otherwise, it should probably be left open. (For example, 'a tight-lipped witness' but 'a witness who remained tight lipped'; 'a short-term solution' but 'a solution in the short term.'"
        if item[1] == "verb":
            
            final_outcome = "if it's an irregular verb like run, for which the infinitive and past participle are identical, may be hyphenated before a noun. otherwise nah"

    if item[0] == "past tense and past participle of" or item[0] == "participle" and item[1] == "noun":
        
        final_outcome = "yes if before a noun"

    if item[0] == "adverb" and item[1] == "past tense and past participle of" or item[1] == "adjective" or item[1] == "participle of":
        
        final_outcome = ("The term should be hyphenated if it appears before a noun (e.g., 'well-lit room'). Otherwise, leave it open ('The room is well lit').")

    return final_outcome
