
from collections import namedtuple
import urllib.request, urllib.parse, urllib.error
import json
import re
import html
from flask import Flask, request, render_template
from num2words import num2words
import grammar

# with open("../../key.txt", "r") as key:
#     MW_KEY = key.read()
      
with open("/etc/secrets/key.txt", "r") as key:
    MW_KEY = key.read()

QUERY_STRING = "?"
BASE  = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/"
      
app = Flask(__name__)

@app.route("/", methods=['GET'])
def hello_world():
   
    landing_page = render_template('_base.html')
    return landing_page

@app.route("/how_it_works.html", methods=['GET', 'POST'])
def how_it_works():
    return render_template('how_it_works.html')

@app.route("/_terms", methods=['GET', 'POST'])
def grammar_defs():
    if request.method == 'POST':
        print(request.form)
        defs_to_get = [k for k,v in request.form.items() if v == "on"]
       
        def_list = [request_url_builder(item, is_a_compound=False, just_get_def=True) for item in defs_to_get]
        term_and_def_dict = dict(zip(defs_to_get, def_list))
        
        terms_page = render_template('_terms.html', answer=term_and_def_dict)
        return terms_page

    terms_page = render_template('_terms.html')
    return terms_page

@app.route('/_compounds.html', methods=['GET', 'POST'])
def get_an_answer():
    if request.method == 'POST':
        if request.form.get('start_compounds') is not None:
            return render_template('_compounds.html', first_page=True)
      
        if request.form.get("user_compound") is not None:        
            user_input = html.escape(request.form['user_compound']).lower()
        
            #using a regex instead of "if '-' in user_input" to catch any stray characters/extra input
            hyphenated_compound = re.search(r"[\w\d]+-[\w\d]+", user_input)
            if hyphenated_compound is None:
                return render_template('_compounds.html', first_page=True, mistake=True)
            
            compound_from_input = user_input[hyphenated_compound.start() : hyphenated_compound.end()]
            split_compound_from_input = compound_from_input.split("-")
            # by_word_1 = ["self", "ex", "great", "half", "more", "most", "less", "least", "very"]
            
            if split_compound_from_input[0].isnumeric():
                num_results = grammar.number_in_compound(split_compound_from_input)
                if num_results.num_answer_ready:
                    
                    new_page = render_template('_compounds.html', num=num_results.num_outcome)
                    return new_page

                compound_from_input = num2words(split_compound_from_input[0]) + "-" + split_compound_from_input[1]
 
            else:
                is_a_compound = True
                results = request_url_builder(compound_from_input, is_a_compound, split_compound_from_input)
        
                if results.r_answer_ready is False:
                    first = [split_compound_from_input[0], results.r_parts[0]]
                    second = [split_compound_from_input[1], results.r_parts[1]]
                    both_halves = [first, second]
                    new_page = render_template('_compounds.html', part_selection=both_halves)
                else:
                    new_page = render_by_type(results)
                
                return new_page
        
        if request.form.get("part_of_speech_selections") is not None:
            selected = [request.form["first_part_of_speech"], request.form["second_part_of_speech"]]
            final_outcome = grammar.cmos_rules(selected)
            newest_page = render_template('_compounds.html', standard=final_outcome)
            return newest_page

    return render_template('_compounds.html', first_page=True)

def render_by_type(results):
    #compounds.html template displays outcomes differently depending on the outcome type. To do that, 
    #render_template takes the outcome type as a keyword argument set to the outcome. This function
    #passes those values to render_template as kwargs.
    
    arg_dict = {results.r_outcome_type: results.r_outcome}
    new_page = render_template('_compounds.html', **arg_dict)

    return new_page
    
def request_url_builder(compound_from_input, is_a_compound, split_compound_from_input=None, just_get_def=None):

    constructed = BASE + compound_from_input + QUERY_STRING + "key=" + MW_KEY
    with urllib.request.urlopen(constructed) as response:
        mw_response = json.load(response)
   
    if just_get_def is not None:
        shortdef = mw_response[0]["shortdef"]
        return shortdef[0]
    
    if is_a_compound:
        return compound_checker(mw_response, compound_from_input, split_compound_from_input)
            
    return mw_response

def compound_checker(mw_response, compound_from_input, split_compound_from_input):
    Results = namedtuple('Results', ['r_answer_ready', 'r_outcome', 'r_outcome_type', 'r_parts'])
    
    r_answer_ready = False
    r_outcome = None
    r_outcome_type = None
    r_parts = None

    not_an_entry = confirm_entry_validity(mw_response)

    if len(mw_response) == 0 or not_an_entry:
        ele_results = grammar.check_first_element_lists(split_compound_from_input)
        if ele_results.ele_answer_ready:
            r_answer_ready = True
            r_outcome = ele_results.ele_outcome
            r_outcome_type = "standard"
    
    else:  
        no_hyphen = split_compound_from_input[0] + split_compound_from_input[1]
        open_compound = split_compound_from_input[0] + " " + split_compound_from_input[1]

        #Checks whether the term is in the dictionary as a closed compound
        found_in_MW = []
        print("_____________________\n\n", mw_response)

        all_forms = {compound_from_input: "hyphenated compound", open_compound: "open compound", no_hyphen: "closed compound"}
        compound_count = 0
        for entry in mw_response:
            part, retrieved = get_stems_and_inflections(entry, compound_from_input)
            print(f"PART AND RETRIEVED {part} {retrieved}\n\n")
            if compound_from_input in retrieved:
                ###TOMORROW MAKE NEW TEMPALTE SECTION FOR THIS, LOOKS BAD AS IS, ALSO ADD TO HANDLE SEPARATELY?
                parts_and_defs = part_of_speech_finder([entry], compound_from_input)
   
                for k,v in parts_and_defs[0].items():
                    newv = str(v).strip("[]")
                    definition = f"Definition: {newv}"
                if entry.get('shortdef') is not None:
                    def_of_term = entry['shortdef'] 
                else:
                    def_of_term = entry['def']
                inf_or_stem_outcome = f"The compound you entered, {compound_from_input}, is a {part} of {newv} and should be hyphenated. The definition of {newv} is as follows: {def_of_term}."
                found_in_MW.append((inf_or_stem_outcome, def_of_term))

                r_answer_ready = True
                r_outcome = found_in_MW
                r_outcome_type = "standard"
            else:
                the_id = get_entry_id(entry)
                    
                if the_id in all_forms.keys(): 
                    parts_and_defs = part_of_speech_finder([entry], the_id)
                    if the_id == compound_from_input:
                        compound_count += 1
                    
                        ###The length of parts_and_defs here will always be one because there is one part of speech per entry in M-W (i.e., different entries for different parts)
                        for k,v in parts_and_defs[0].items():
                            newv = str(v).strip("[]")
                            definition = f"Definition: {newv}"

                            if k == "adjective":
                                hyph_outcome = f"{compound_from_input.capitalize()} is in the dictionary as an adjective; it should be hyphenated if it precedes a noun."
                            else:
                                hyph_outcome = f"{compound_from_input.capitalize()} is in the dictionary as a / an {k}; it should likely be hyphenated regardless of what it precedes."

                        found_in_MW.append((all_forms[the_id], hyph_outcome, definition))
                
                    else:
                        found_in_MW.append((all_forms[the_id], the_id, *parts_and_defs))    
                
                r_answer_ready = True
                r_outcome = found_in_MW

                #Differentiating between outcome types because they are rendered differently in the Jinja 'compounds' template
                if compound_count == 0:
                    r_outcome_type = "no_hyph"

                if compound_count == 1 and len(found_in_MW) == 1:
                    r_outcome_type = "only_hyph"
                    r_outcome = found_in_MW[0]

                if compound_count > 0 and len(found_in_MW) > 1:
                    r_outcome_type = "both"

    #Handles each part of the compound separately
    if not r_answer_ready:
        is_a_compound = False
        r_answer_ready, r_outcome, r_outcome_type, r_parts = handle_separately(is_a_compound, split_compound_from_input)
        
    results = Results(r_answer_ready, r_outcome, r_outcome_type, r_parts)
    print("RESULTS__________________", results)
    return results

def confirm_entry_validity(mw_response):
    not_an_entry = all(isinstance(entry, str) for entry in mw_response)
    return not_an_entry


def handle_separately(is_a_compound, split_compound_from_input):
    mw_responses = [request_url_builder(i, is_a_compound, split_compound_from_input) for i in split_compound_from_input]

    #TODO: Support for one typo w/alternative spellings and one without
    
    #Checks for empty responses and responses that consist entirely of strings. Note that when a word isn't Merriam-Webster's Collegiate® Dictionary but there are other similar words in the dictionary, it returns a list of those words (a list of strings). If there are no similar words, it returns an empty list. 
    invalid = [i for i in mw_responses if len(i) == 0]
    if len(invalid) != 0:
        outcome = f"At least one part of the compound you entered, {'-'.join(split_compound_from_input)}, is not in the dictionary, and the dictionary did not return any alternative spellings. Please confirm the correct spelling and try again."
        answer_ready = True
        all_defs_and_parts = None
        outcome_type = "typo"

    else:
        not_an_entry = [confirm_entry_validity(mw_response) for mw_response in mw_responses]
      
        if all(not_an_entry):
            print(mw_responses)
            #TODO: Figure out how to pretty print this with line breaks.
            outcome = f"Both parts of the compound you entered, {'-'.join(split_compound_from_input)}, appear to be misspelled. The dictionary returned the following alternatives. Did you mean to enter one of those instead? Alternatives to first term: {mw_responses[0]}. \n Alternatives to second term: {mw_responses[1]}."
            answer_ready = True
            all_defs_and_parts = None
            outcome_type = "typo"
     
        elif any(not_an_entry):
            which_term = [i for i,v in enumerate(not_an_entry) if v]
            outcome = f"One of the words in the compound you entered, {split_compound_from_input[which_term[0]]}, is not in the dictionary. Merriam-Webster's Collegiate® Dictionary returned the following alternatives: \n{mw_responses[which_term[0]]}."
            answer_ready = True
            all_defs_and_parts = None
            outcome_type = "typo"

        else:
            compound_and_responses = dict(zip(split_compound_from_input, mw_responses))
            parts = [part_of_speech_finder(v, k) for k, v in compound_and_responses.items()]
            all_defs_and_parts = combiner(parts)
            answer_ready = False
            outcome = None
            outcome_type = None
    
    return answer_ready, outcome, outcome_type, all_defs_and_parts

def get_entry_id(entry):
    entry_id = entry['meta']['id']
    if ":" in entry_id:
        the_id = entry_id.split(":")[0]
    else:
        the_id = entry_id
    return the_id

def get_stems_and_inflections(entry, item):
    part = None
    retrieved = None 

    inflections = entry.get("ins")
    stems = entry['meta'].get('stems')

    if inflections is not None:
        infs = [inf['if'] for inf in inflections]
        formatted_infs = [i if "*" not in i else i.replace("*", "") for i in infs]
        if item in formatted_infs:
            part = "participle of"
            retrieved = formatted_infs
            
    if retrieved is None and stems is not None:
        if item in stems:
            part = "variation / form / stem of"
            retrieved = stems

    return part, retrieved

def part_of_speech_finder(mw_response, item):
    print("\n\n\n\nin part of speech!!!!!")
    
    parts = []
    for entry in mw_response:
        the_id = get_entry_id(entry)

        print("ENTRY!!!!_______\n \n")
        if the_id == item:
            part = entry.get("fl")
            if part is None:
                part = entry.get("cxs")[0]["cxl"]
                reference = entry.get("cxs")[0]["cxtis"][0]["cxt"]
                print("PART IS NONE!", part, reference, entry.get("cxs")[0]["cxtis"])
                parts.append({part: reference})
                
        #The "stems" of a word list all variants of the word; an "inflection" is essentially a conjugated verb. All inflections are stems, but all stems are not inflections.
        if the_id != item:
            print(f"\n\n\n________{item} {the_id}")
            part, retrieved = get_stems_and_inflections(entry, item)
            if part is not None:
                parts.append({part: the_id})
            continue
          
        if entry.get('shortdef') is not None:
            def_of_term = entry['shortdef'] 
        else:
            def_of_term = entry['def']
        parts.append({part: def_of_term})
        print(f"____________________\n PARTS {parts}________________\n")

    return parts

def combiner(parts):
    all_defs_and_parts = [{}, {}]

    for i in range(len(all_defs_and_parts)):
        for item in parts[i]:
            for k,v in item.items():
                if k not in all_defs_and_parts[i].keys():
                    all_defs_and_parts[i][k] = [v]
                else:
                    all_defs_and_parts[i][k].append(v)

    return all_defs_and_parts
