from flask import Flask, request, render_template
from num2words import num2words
from collections import namedtuple
import urllib.request, urllib.parse, urllib.error
import json
import re
import html

# with open("../../key.txt", "r") as key:
#     MW_KEY = key.read()
      
with open("/etc/secrets/key.txt", "r") as key:
    MW_KEY = key.read()

query_string = "?"
base  = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/"
      
app = Flask(__name__)

@app.route("/", methods=['GET'])
def hello_world():
   
    landing_page = render_template('_base.html')
    return landing_page

@app.route("/how_it_works.html", methods=['GET', 'POST'])
def how_it_works():
    if request.method == 'POST':
        return render_template('how_it_works.html')

@app.route('/_compounds.html', methods=['GET', 'POST'])
def get_an_answer():
    if request.method == 'POST':
        if request.form.get('start_compounds') is not None:
            print(request.form.get('start_compounds'), "COMP!!!!")
            return render_template('_compounds.html', first_page=True)
      
        if request.form.get("user_compound") is not None:        
            user_input = html.escape(request.form['user_compound']).lower()
        
            #using a regex instead of "if '-' in user_input" to catch any stray characters/extra input
            hyphenated_compound = re.search("[\w\d]+-[\w\d]+", user_input)
            if hyphenated_compound is None:
                return render_template('_compounds.html', first_page=True, mistake=True)
            else:
                compound_from_input = user_input[hyphenated_compound.start() : hyphenated_compound.end()]
                split_compound_from_input = compound_from_input.split("-")
                by_word_1 = ["self", "ex", "great", "half", "more", "most", "less", "least", "very"]
             
                if split_compound_from_input[0].isnumeric():
                    compound_from_input = num2words(split_compound_from_input[0]) + "-" + split_compound_from_input[1]
 
                if split_compound_from_input[0] in by_word_1 or split_compound_from_input[0].endswith("ly"):
                    word_answer, found_by_word = check_by_word(split_compound_from_input)
                    if found_by_word:
                        new_page = render_template('_compounds.html', final=word_answer)
                        return new_page
                 
                is_a_compound = True
                results = request_url_builder(compound_from_input, is_a_compound, split_compound_from_input)
                
                print(f"\n\n NAMED TUPLE {results.r_answer_ready}, {results.r_outcome}, {results.r_parts} !!!!!!")
             
                if results.r_answer_ready is False:
                    first = [split_compound_from_input[0], results.r_parts[0]]
                    second = [split_compound_from_input[1], results.r_parts[1]]
                    all = [first, second]
                    new_page = render_template('_compounds.html', answer3=all)
                else:
                    print({results.r_outcome})
                    new_page = render_template('_compounds.html', final=results.r_outcome)
                return new_page
            
        if request.form.get("part_of_speech_selections") is not None:
            selected = [request.form["first_part_of_speech"], request.form["second_part_of_speech"]]
            final_outcome = cmos_rules(selected)
            newest_page = render_template('_compounds.html', final=final_outcome)
            return newest_page

    return render_template('_compounds.html', first_page=True)

@app.route("/_terms", methods=['GET', 'POST'])
def grammar_defs():
    if request.method == 'POST':
        defs_to_get = [k for k,v in request.form.items() if v == "on"]
       
        def_list = [request_url_builder(item, is_a_compound=False, just_get_def=True) for item in defs_to_get]
        term_and_def_dict = dict(zip(defs_to_get, def_list))
        
        terms_page = render_template('_terms.html', answer=term_and_def_dict)
        return terms_page

    terms_page = render_template('_terms.html')
    return terms_page

def request_url_builder(compound_from_input, is_a_compound, split_compound_from_input, just_get_def=None):
    print("\n\n\n IN REQUEST BUILDER", compound_from_input)

    constructed = base + compound_from_input + query_string + "key=" + MW_KEY
    response = urllib.request.urlopen(constructed)
    mw_response = json.load(response)
        
    if just_get_def is not None:
        shortdef = mw_response[0]["shortdef"]
        return shortdef[0]
    
    if is_a_compound:
        return compound_checker(mw_response, compound_from_input, split_compound_from_input)
            
    else:
        # if len(mw_response) == 0:
        #     invalid = True
        #     print("000000000000000000000000")
        #     return invalid
        # else:
        return mw_response
 
def compound_checker(mw_response, compound_from_input, split_compound_from_input):
        done = True
        Results = namedtuple('Results', ['r_answer_ready', 'r_outcome', 'r_parts'])
        
        if len(mw_response) == 0 or "hwi" not in mw_response[0]:
            ##TODO: Confirm whether this is necessary
            done = False 

        elif mw_response[0]['meta']['id'] != compound_from_input:
            no_hyphen = split_compound_from_input[0] + split_compound_from_input[1]

            #Checks whether the term is in M-W as a closed compound
            if mw_response[0]['meta']['id'] == no_hyphen:
                outcome =  f"Per the dictionary, the term is not hyphenated; use {mw_response[0]['meta']['id']} instead. (TL;DR: No!)"
                answer_ready = True
            else:
                done = False
        else: 
            part = mw_response[0].get("fl")

            if part == "adjective":
                outcome = f'The compound term you provided, {compound_from_input}, is in the dictionary and is an {part}; it should be hyphenated if it precedes a noun. (TL;DR: Maybe)'
            else:
                outcome =  f"The compound term you provided, {compound_from_input}, is in the dictionary and is a {part}; it should likely be hyphenated regardless of what it precedes. (TL;DR: Yes!)"
            answer_ready = True
        
        #Handles each part of the compound separately
        if not done:
            is_a_compound = False
            answer_ready, outcome, all_defs_and_parts = handle_separately(is_a_compound, split_compound_from_input)
            results = Results(answer_ready, r_outcome=outcome, r_parts=all_defs_and_parts)
        else: 
            results = Results(answer_ready, r_outcome=outcome, r_parts=None)   
        return results

def handle_separately(is_a_compound, split_compound_from_input):
    mw_responses = [request_url_builder(i, is_a_compound, split_compound_from_input) for i in split_compound_from_input]
    
    #Checks for empty responses and responses that consist entirely of strings. Note that when a word isn't in M-W but there are other similar words in the dic, M-W returns a list of those words (a list of strings). If the word isn't in M-W and there are no similar words, M-W returns an empty list. 

    invalid = [i for i in mw_responses if len(i) == 0]
    if len(invalid) != 0:
        outcome = f"At least one part of the compound you entered, {'-'.join(split_compound_from_input)}, is not in the dictionary, and the dictionary did not return any alternative spellings. Please confirm the correct spelling and try again."
        print(outcome)
        answer_ready = True
        all_defs_and_parts = None
        
    else:
        not_an_entry = [all(isinstance(jitem, str) for jitem in item) for item in mw_responses]
        print(f"\n\n IN HANDLE SEPARATELY, NOT AN ENTRY!!! {not_an_entry}")
 
        if all(not_an_entry):
            print(mw_responses)
            #TODO: Figure out how to pretty print this with line breaks.
            outcome = f"Both parts of the compound you entered, {'-'.join(split_compound_from_input)}, appear to be misspelled. The dictionary returned the following alternatives. Did you mean to enter one of those instead? Alternatives to first term: {mw_responses[0]}. \n Alternatives to second term: {mw_responses[1]}."
            answer_ready = True
            all_defs_and_parts = None
     
        elif any(not_an_entry):
            which_term = [i for i,v in enumerate(not_an_entry) if v]
            outcome = f"One of the words in the compound you entered, {split_compound_from_input[which_term[0]]}, is not in the dictionary. M-W returned the following alternatives: \n{mw_responses[which_term[0]]}."
            answer_ready = True
            all_defs_and_parts = None

        else:
            compound_and_responses = dict(zip(split_compound_from_input, mw_responses))
            parts = [part_of_speech_finder(v, k) for k, v in compound_and_responses.items()]
            all_defs_and_parts = combiner(parts)
            answer_ready = False
            outcome = None

    return answer_ready, outcome, all_defs_and_parts

def part_of_speech_finder(mw_response, item):
    print("\n\n\n\nin part of speech!!!!!")
    
    parts = []
    for jitem in mw_response:
        id = jitem['meta']['id']
        # print("\n\n", jitem)
        if ":" in id:
            this_id = id.split(":")[0]
        else:
            this_id = id
        if this_id == item:
            part = jitem.get("fl")
            print(f"PART ON 161 {part} ________________")
            if part is None:
                cross_reference = jitem.get("cxs")[0]["cxl"]
                reference = jitem.get("cxs")[0]["cxtis"][0]["cxt"]
                part = cross_reference 
                print("PART IS NONE!", part, reference, jitem.get("cxs")[0]["cxtis"])
                parts.append({part: reference})
                continue

        if this_id != item:
            print(f"\n\n\n________{item} {this_id}")
            inflections = jitem.get("ins")
            stems = jitem['meta'].get('stems')

            if inflections is not None:
                fixed_inf = [inf['if'] for inf in inflections]
                new_fixed_inf = [j if "*" not in j else j.replace("*", "") for j in fixed_inf]

                if item in new_fixed_inf:
                    part = f"participle of"
                    parts.append({part: this_id})
                    continue       
                else:
                    continue
            elif stems is not None:
                if item in stems:
                    print(stems, "STEMS!")
                    part = f"variation / form of"
                    parts.append({part: this_id})
                    continue
            else:
                continue
                
        if jitem.get('shortdef') is not None:
            def_of_term = jitem['shortdef'] 
        else:
            def_of_term = jitem['def']
        parts.append({part: def_of_term})

    return parts

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
    
            final_outcome = "When a verb-noun pair forms a compound, it is generally closed up (e.g., 'pick' + 'pocket' = 'pickpocket') and listed in M-W as such; because the verb-noun pair you entered is not in M-W, it should likely be left open."
        elif item[1] == "adverb" or item[1] == "preposition":
            final_outcome = "Since M-W does not list the term you entered as a compound, it should likely be left open. There may be edge cases not included in M-W, though, so read on for a quick word on the treatement of verb-adverb and verb-preposition pairs.\n A verb followed by a preposition or adverb can be hyphenated, left open, or closed up; it all depends on how the pair of words is functioning. Since M-W does not list the pair of words you provided, you'll \n Pairs that are used as verbs (i.e., phrasal verbs) are not hyphenated, although their noun or adjectival equivalents can be hyphenated or closed up. For example, take 'break down.' As a phrasal verb--'I'm worried that my car will break down'--there's no hyphen. As a noun, the term is closed up ('There was a breakdown in negotiations.') \n Note tooIf the second word in the pair is a two-letter particle like 'by', 'in', or 'up', a hyphen is likely appropriate"
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

def combiner(parts):
    print(f"_________________\n\n\n\n COMBINER {parts} \n\n ________________")
    all_defs_and_parts = [{}, {}]

    for i in range(len(all_defs_and_parts)):
        for item in parts[i]:
            for k,v in item.items():
                if k not in all_defs_and_parts[i].keys():
                    all_defs_and_parts[i][k] = [v]
                else:
                    all_defs_and_parts[i][k].append(v)

    return all_defs_and_parts

def check_by_word(split_compound_from_input):
    outcome = None
    adverbs = ["more", "most", "less", "least", "very"]
    if split_compound_from_input[0].isnumeric():
        outcome = "NUMMMM"
        
        if split_compound_from_input[1] == "percent" or split_compound_from_input[1] == "percentage":
            print(f"!!!!!!!!!!!!!, {split_compound_from_input[1]}")
            outcome = "NOOOOO, PERCENT!!"  

    if split_compound_from_input[0] in adverbs:
        outcome = "Compounds consisting of 'more,' 'most,' 'less,' 'least,' or 'very' and an adjective or participle (e.g., 'a more perfect nation,' 'the least traveled path' ) do not need to be hyphenated unless there is a risk of misinterpretation."
    if split_compound_from_input[0].endswith("ly") and split_compound_from_input[0] != "only" and split_compound_from_input[0] != "family":
        outcome = "NO NO SEEMS LIKE AN ADVERB ENDING IN LY!" 
    
    if split_compound_from_input[0] == "self":
        print("hyph unless followed by a suffix (selfless) or precede by 'un' ('unselfconscious')")
        outcome = "hyph unless followed by a suffix (selfless) or precede by 'un' ('unselfconscious')"
    if split_compound_from_input[0] == "ex":
        print("yes")
        outcome = "yes"
    if split_compound_from_input[0] == "great":
        print("yes, if the second word describes a family relationship (e.g., 'great-grandfather')")
        outcome = "yes, if the second word describes a family relationship (e.g., 'great-grandfather')"
    if split_compound_from_input[0] == "half":
        print("yes if used as an adjective, whether before or after a noun (e.g., 'half-asleep'); open if used as a noun or verb (e.g., 'a half hour' or 'half listen')")
        outcome = "yes if used as an adjective, whether before or after a noun (e.g., 'half-asleep'); open if used as a noun or verb (e.g., 'a half hour' or 'half listen')"

    if outcome is not None:
        found_by_word = True
    else:
        found_by_word = False
    return outcome, found_by_word