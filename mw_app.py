
from collections import namedtuple, Counter, defaultdict
import urllib.request, urllib.parse, urllib.error
import json
import re
import html
from flask import Flask, request, render_template
from num2words import num2words
import grammar
from classes import StandardEntry, Nonstandard

with open("../../key.txt", "r") as key:
    MW_KEY = key.read()
      
# with open("/etc/secrets/key.txt", "r") as key:
#     MW_KEY = key.read()

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
            
            if split_compound_from_input[0].isnumeric():
                num_results = grammar.number_in_compound(split_compound_from_input)
                if num_results.num_answer_ready:
                    
                    new_page = render_template('_compounds.html', num=num_results.num_outcome)
                    return new_page

                compound_from_input = num2words(split_compound_from_input[0]) + "-" + split_compound_from_input[1]
            # out types = need user input, standard, found in MW, typo 
            else:
                is_a_compound = True
                results, split_compound_from_input = request_url_builder(compound_from_input, is_a_compound, split_compound_from_input)
                print(f"\n\n\n CL! {split_compound_from_input}, {results.r_outcome}, {results.r_outcome_type}")
                # assert False
                if results.r_answer_ready is False:
                    new_page = render_template('_compounds.html', defs_to_show=results.r_outcome, search_term=split_compound_from_input, outcome_header = results.r_outcome_header)
                else:
                    new_page = render_by_type(results)
                
                return new_page
        
        if request.form.get("part_of_speech_selections") is not None:
            print(request.form)
            selected = [request.form["first_part_of_speech"], request.form["second_part_of_speech"]]
            final_outcome = grammar.cmos_rules(selected)
            newest_page = render_template('_compounds.html', standard=final_outcome)
            return newest_page

    return render_template('_compounds.html', first_page=True)

def render_by_type(results):
    #compounds.html template displays outcomes differently depending on the outcome type. To do that, 
    #render_template takes the outcome type as a keyword argument set to the outcome. This function
    #passes those values to render_template as kwargs.
    
    arg_dict = {results.r_outcome_type: results.r_outcome, "header": results.r_outcome_header}
    new_page = render_template('_compounds.html', **arg_dict)

    return new_page
    
def request_url_builder(compound_from_input, is_a_compound, split_compound_from_input=None, just_get_def=None):
    '''Build and send the request to Merriam-Webster's Collegiate® Dictionary with Audio API.'''
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
    Results = namedtuple('Results', ['r_answer_ready', 'r_outcome', 'r_outcome_type', 'r_outcome_header'])
    
    outcomes_by_comp_type = defaultdict(list)
    r_answer_ready = False
    r_outcome = None
    r_outcome_type = None
    r_outcome_header = None

    not_an_entry = confirm_entry_validity(mw_response)

    if len(mw_response) == 0 or not_an_entry:
        ele_results = grammar.check_first_element_lists(split_compound_from_input)
        if ele_results.ele_answer_ready:
            r_answer_ready = True
            r_outcome = ele_results.ele_outcome
            r_outcome_type = "standard"
            r_outcome_header = "something"
    
    else:  
        no_hyphen = split_compound_from_input[0] + split_compound_from_input[1]
        open_compound = split_compound_from_input[0] + " " + split_compound_from_input[1]

        #Checks whether the term is in the dictionary as a closed compound

        all_forms = {compound_from_input: "hyphenated compound", open_compound: "open compound", no_hyphen: "closed compound"}
        
        compound_entries = {}
        for k,v in all_forms.items():
            relevant_entries = part_of_speech_finder(mw_response, k)
            if relevant_entries:
                compound_entries[k] = relevant_entries

        ###handle multiple outcomes
        if len(compound_entries) == 0:
            r_answer_ready = False
        
        else:
            outcomes = []
            for compounds, entries in compound_entries.items(): 
                for ce in entries:
                    if "-" in ce.the_id:
                        compound_type = "hyphenated compound"
                    else:
                        split_k = ce.the_id.split(" ")
                        if len(split_k) > 1:
                            compound_type = "open compound"
                        else:
                            compound_type = "closed compound"
                   
                    if ce.part_type == "main_entry":
                        outcome = in_mw_as_main_entry(compound_type, ce, compound_from_input)        
                       
                    ##what to do with diff crts?
                    if ce.part_type == "variant" or ce.part_type == "cxs_entry" or ce.part_type == "one_of_diff_parts":
                        outcome = in_mw_as_variant(compound_type, ce, compound_from_input)
                    
                    outcomes.append({compound_type: outcome})

            if len(outcomes) > 1:
                for o in outcomes:
                    for k,v in o.items():
                        outcomes_by_comp_type[k].append(v)
                    
                compound_types = [k for k in outcomes_by_comp_type.keys()]
                if len(compound_types) == 2:
                    form = " and ".join(compound_types)
                else:
                    compound_types.insert(-1, "and ")
                    form = ", ".join(compound_types)

            else:
                for o in outcomes:
                    for k, v in o.items():
                        form = k
                    
            r_outcome_header = f"M-W lists '{compound_from_input}' as a/an {form}. Details are provided below."
            print(r_outcome_header)
            r_answer_ready = True
            r_outcome_type = "found_in_MW"
            r_outcome = outcomes
        
    # #Handles each part of the compound separately
    if not r_answer_ready:
        is_a_compound = False
        r_answer_ready, r_outcome, r_outcome_type, r_outcome_header = handle_separately(is_a_compound, split_compound_from_input)
    
        
    results = Results(r_answer_ready, r_outcome, r_outcome_type, r_outcome_header)
    # print("RESULTS__________________", results)
   
    return results, split_compound_from_input

def in_mw_as_main_entry(compound_type, ce, compound_from_input):
    print("\n\n MAIN ENTRY COMP TYPE", compound_type)
    if compound_type == "closed compound":
        outcome = f"According to M-W, the search term you entered, '{compound_from_input}', is a {compound_type} ({ce.the_id}), which means that it should not be hyphenated. Its definition is as follows: {ce.definition}."
        print(outcome)

    elif compound_type == "open compound":                
        if ce.part ==  "adjective" or ce.part == "adverb":
            outcome = f"M-W lists the search term you entered, '{compound_from_input}', as an {compound_type}. However, as CMoS 7.85 says, 'it is never incorrect to hyphenate adjectival compounds before a noun.' The term's definition is as follows: {ce.definition.values()}."
        else:
            outcome = f"M-W lists the search term you entered, '{compound_from_input}', as an {compound_type} ('{ce.the_id}'). Because it is a/an {ce.part}, it should likely be left open in all cases."
    
    else:
        outcome = handle_hyphenated_variant(ce, compound_from_input)
                        
    return outcome

def in_mw_as_variant(compound_type, ce, compound_from_input):
    if compound_type == "closed compound":
        outcome = f"According to M-W, the search term you entered, '{compound_from_input}', is a/an {ce.cr_type} '{ce.crt}', which is a {compound_type}. The definition of {ce.crt} is as follows: {ce.definition}."
                                
    elif compound_type == "open compound":                
        if ce.part ==  "adjective" or ce.part == "adverb":
            outcome = f"The search term you entered, '{compound_from_input}', is a/an {ce.cr_type} of {ce.crt}, which is an {compound_type}. However, as CMoS 7.85 says, 'it is never incorrect to hyphenate adjectival compounds before a noun.' The definition of {ce.crt} is as follows: {ce.definition.values()}."
        else:
            outcome = f"The search term you entered, '{compound_from_input}', is a/an {ce.cr_type} of {ce.crt}, which is an {compound_type}. Because {ce.crt} is a/an {ce.part}, it should likely be left open in all cases." 
                            
    else:
        outcome = handle_hyphenated_variant(ce, compound_from_input)
    
    return outcome

def handle_hyphenated_variant(ce, compound_from_input):
    print("\n\n IN HANDLE HYPH VAR!")
    adj_caveat = f"Although M-W lists the term as a hyphenated compound, it should likely be hyphenated before but not after a noun.\n" 
    f"As CMoS 7.85 says, 'It is never incorrect to hyphenate adjectival compounds before a noun. When such compounds follow the noun they modify, hyphenation is usually unnecessary, even for adjectival compounds that are hyphenated in Webster's (such as well-read or ill-humored).'"
   
    if ce.part == "adjective" or ce.part == "adverb":
        if ce.part_type == "variant" or ce.part_type == "cxs_entry" or ce.part_type == "one_of_diff_parts":
            mw_result = f"According to M-W, the search term you entered, '{compound_from_input}', is a/an {ce.cr_type} of '{ce.crt}' and is an {ce.part}. You should likely use '{ce.crt}' instead of '{compound_from_input}.\n'" 
        else:
            mw_result = f"M-W lists the search term you entered, '{compound_from_input}', as a/an {ce.part} meaning {ce.definition[ce.part]}."
        outcome = mw_result + "\n" + adj_caveat           
                            
    else:
        if ce.part_type == "variant" or ce.part_type == "cxs_entry" or ce.part_type == "one_of_diff_parts":
            outcome = f"According to M-W, the search term you entered, '{compound_from_input}', is a/an {ce.cr_type} of '{ce.crt}' and is an {ce.part}. You should likely use '{ce.crt}' instead of '{compound_from_input}' and hyphenate it regardless of where it appears in a sentence. Its definition is as follows: {ce.definition.values()}."
        else:
            outcome = f"M-W lists the search term you entered, '{compound_from_input}', as a/an {ce.part} meaning\n {ce.definition[ce.part]}. It should likely be hyphenated regardless of its position in a sentence."
   
    return outcome

def confirm_entry_validity(mw_response):
    '''Confirm that the search term is valid.

    Check for empty responses and responses that consist entirely of strings (no JSON).
    When a word isn't in Merriam-Webster's Collegiate® Dictionary but there are
    other similar words in the dictionary, the API returns a list of those words
    (a list of strings). If there are no similar words, it returns an empty list.
    '''
    not_an_entry = all(isinstance(entry, str) for entry in mw_response)

    return not_an_entry

def handle_separately(is_a_compound, split_compound_from_input):
    mw_responses = [request_url_builder(i, is_a_compound, split_compound_from_input) for i in split_compound_from_input]

    #TODO: Support for one typo w/alternative spellings and one without
    
    invalid = [i for i in mw_responses if len(i) == 0]
    if len(invalid) != 0:
        outcome = f"At least one part of the compound you entered, {'-'.join(split_compound_from_input)}, is not in the dictionary, and the dictionary did not return any alternative spellings. Please confirm the correct spelling and try again."
        answer_ready = True
        outcome_type = "typo"
        outcome_header = "Something's not right."

    else:
        not_an_entry = [confirm_entry_validity(mw_response) for mw_response in mw_responses]
      
        if all(not_an_entry):
            # print(mw_responses)
            #TODO: Figure out how to pretty print this with line breaks.
            outcome = f"Both parts of the compound you entered, {'-'.join(split_compound_from_input)}, appear to be misspelled. The dictionary returned the following alternatives. Did you mean to enter one of those instead? Alternatives to first term: {mw_responses[0]}. \n Alternatives to second term: {mw_responses[1]}."
            answer_ready = True
            outcome_type = "typo"
            outcome_header = "Something's not right."
     
        elif any(not_an_entry):
            which_term = [i for i,v in enumerate(not_an_entry) if v]
            outcome = f"One of the words in the compound you entered, {split_compound_from_input[which_term[0]]}, is not in the dictionary. Merriam-Webster's Collegiate® Dictionary returned the following alternatives: \n{mw_responses[which_term[0]]}."
            answer_ready = True
            outcome_type = "typo"
            outcome_header = "Something's not right."

        else:
            compound_and_responses = dict(zip(split_compound_from_input, mw_responses))
            relevant_entries = [part_of_speech_finder(v, k) for k, v in compound_and_responses.items()]
            
            answer_ready = False
            outcome = relevant_entries
            outcome_type = "need user input"
            outcome_header = "Please pick a part of speech."
    
    return answer_ready, outcome, outcome_type, outcome_header

def get_entry_id(entry):
    '''Get the ID (headword and in some cases homograph(s)) from the API response.'''
    entry_id = entry['meta']['id']
    if ":" in entry_id:
        the_id = entry_id.split(":")[0]
    else:
        the_id = entry_id

    return the_id

def get_entry_definition(entry):
    '''Get the definition of the entry from the API response.'''
    if entry.get('shortdef') is not None:
        def_of_term = entry['shortdef'] 
    else:
        def_of_term = entry['def']

    return def_of_term

def get_cxs_target_def(term, old_part):
    print(f"\n\n IN GET RELATED TERM!", old_part)

    is_a_compound = False
    split_id = term.split(" ")
    #Check whether the cross-reference target is two words; if it is, URL encode the space character.
    if len(split_id) > 1:
        search_term = split_id[0] + "%20" + split_id[1]
    else:
        search_term = term

    cxs_mw_response = request_url_builder(search_term, is_a_compound)
    cxs_defs = []
    
    for i in cxs_mw_response:
        part_of_speech = i.get("fl")
        #If the original search term is a conjugated verb, retrieve only verb definitions.
        if "tense" in old_part or "participle" in old_part or "conjugated form" in old_part:
            if part_of_speech == "verb":
                cxs_target_def = get_entry_definition(i)
                cxs_defs.append({part_of_speech: cxs_target_def})
                part_type = "cxs_entry"
                break
        else:
            cxs_target_def = get_entry_definition(i)
            if cxs_target_def:
                cxs_defs.append({part_of_speech: cxs_target_def})

    print("_______________________", cxs_defs, part_of_speech)
    if len(cxs_defs) > 1:
        part_type = "diff_parts"
        return cxs_defs, part_of_speech, part_type
    else:
        part_type = "cxs_entry"
        return *cxs_defs, part_of_speech, part_type

def check_for_multiple_parts(defs):
    
    if len(defs) > 1:
        part_type = "var_diff_parts"
    else:
        part_type = "variant"
    return part_type

def variant_or_inflection(the_id, item, entry, relevant_entries, abnormal_parts, part):
    """Handle entries in which the headword is an inflection or variant.
    
    """
    ###REDO UNNNECESARY TO GET DEF?
    inflections = entry.get("ins")
    vars = entry.get("vrs")
    print(vars)
    if vars is None and inflections is None:
        return

    if vars is not None:
        var_defs, relation_to_variant, variant_id, part, def_of_term, part_type = get_variants(entry, item, vars)
    else:
        var_defs, relation_to_variant, variant_id, part, def_of_term, part_type = get_inflections(entry, item, inflections)
        
    print("\n\n", var_defs, relation_to_variant, variant_id, part, def_of_term, part_type) 
    
    if part_type == "var_diff_parts":
        handle_diff_parts(the_id, var_defs, relation_to_variant, abnormal_parts, relevant_entries, variant_id)
        return

    else:
        if part is None and def_of_term is None:
            return
        else:
            print("RELATION\n\n", relation_to_variant)
            if "participle of" in relation_to_variant:
                relation_to_variant = "participle of"
            if "tense" in relation_to_variant:
                relation_to_variant = "inflection (conjugated form) of"
            
            # if relation_to_variant not in abnormal_parts:
            #     abnormal_parts.append(relation_to_variant)
            # else:
            make_new_part_type, dupe_defs_or_parts = check_for_duplicates(var_defs, relevant_entries, part, relation_to_variant, variant_id)
            if dupe_defs_or_parts:
                return
            else:
                if make_new_part_type is not None:
                    part_type = make_new_part_type 
    print(f"APPENDING IN VARIANT OR INFLECTIONS. 457. DEF {var_defs}")                        
    relevant_entries.append(Nonstandard(the_id, part_type, part, var_defs, variant_id, relation_to_variant))

def get_inflections(entry, item, inflections):
    def_of_term = None
    var_defs = []
    relation_to_variant = None
    variant_id = None
    part_of_speech = None
    print("\n\n GET INFLECTIONS!!!!")

    for i in inflections:
        inf = i['if']
        if "*" in inf:
            inf = inf.replace("*", "")
        if inf == item:
            inflection_label = i.get('il')
    
            def_of_term = get_entry_definition(entry)      
            part_of_speech = entry.get('fl')
            variant_id = get_entry_id(entry)

            if part_of_speech == "verb":
                
                if inflection_label is not None and "participle" in inflection_label:
                    relation_to_variant = "participle of"
                else:
                    relation_to_variant = "inflection (conjugated form) of"
            
            else:
                relation_to_variant = "variant of"
            var_defs = {part_of_speech: def_of_term}
    
    part_type = check_for_multiple_parts(var_defs)
    return var_defs, relation_to_variant, variant_id, part_of_speech, def_of_term, part_type

def get_variants(entry, item, vars):
    ###prob fine without stems. confirm
    ###CONFIRM THAT I ONLY NEED VARIANTS OR INFLECTIONS, NOT BOTH
    print("IN GET VARIANTS")
   
    def_of_term = None
    var_defs = []
    relation_to_variant = None
    variant_id = None
    part_of_speech = None
    vars = vars[0]

    if "*" in vars['va']:
        va = vars['va'].replace("*", "")
    else:
        va = vars['va']

    print(f"514!!!\n\n\n {va} {item}")
    ###DO WE EVEN NEED TO GET THE DEF HERE?
    if va == item:
        def_of_term = get_entry_definition(entry)
        variant_id = get_entry_id(entry)
        vl = vars.get('vl')
        part_of_speech = entry.get('fl')
        ##chiefly british not an option. where is that coming from with flavour?
        vl_options = {"or less commonly": "less common spelling of", "or": "alternative spelling of", "or chiefly British": "chiefly British spelling of"}
        for k, v in vl_options.items():
            if vl == k:
                relation_to_variant = v

        if vl is None or vl not in vl_options.items():
            relation_to_variant = "variant of"

        var_defs = {part_of_speech: def_of_term}
    
    else:
        relation_to_variant = "not variant"
    ###should never happen
    part_type = check_for_multiple_parts(var_defs)
        
    ##tigthen this up later
    return var_defs, relation_to_variant, variant_id, part_of_speech, def_of_term, part_type

def handle_diff_parts(the_id, cxs_target_def, cxl_part, abnormal_parts, relevant_entries, crt):
    for i in cxs_target_def:
        part_type = "one_of_diff_parts" 
        if cxl_part not in abnormal_parts:
            abnormal_parts.append(cxl_part)
        else:
            dupe = duplicate_definitions(i, relevant_entries)
            if dupe:
                continue
        for part_of_speech, v in i.items():
            print(f"APPENDING IN HANDLE DIFF PARTS. 551. DEF {i}. PROB A PROBLEM.")        
            relevant_entries.append(Nonstandard(the_id, part_type, part_of_speech, i, crt, cxl_part))
        
def check_for_duplicates(definition, relevant_entries, part_of_speech, cxl_part, crt):    
        dupe_defs_or_parts = False
        make_new_part_type = None
        print(f"\n\n IN CHECK FOR DUPLICATES")
        duplicate_defs = duplicate_definitions(definition, relevant_entries)

        if duplicate_defs:
            dupe_defs_or_parts = True

        else:
            combined, make_new_part_type = duplicate_parts_of_speech(part_of_speech, definition, relevant_entries, cxl_part, crt)
            if combined:
                dupe_defs_or_parts = True

        return make_new_part_type, dupe_defs_or_parts    

def duplicate_definitions(definition, relevant_entries):
    dupe = False
    for i in relevant_entries:    
        vs = [v for v in i.definition.values()]
        vs2 = [v for v in definition.values()]
        if vs2 == vs:
                dupe = True
    
    return dupe
   
def duplicate_parts_of_speech(part_of_speech, definition, relevant_entries, cxl_part, crt):
    ###THIS SHOULD NEVER HAPPEN TO THINGS WITH A PART TYPE OF MAIN ENTRY BUT CONFIRM
    combined = False
    new_part_type = None

    nonstandard_entries = [j for j in relevant_entries if j.part_type != "main_entry"]
    for i in nonstandard_entries:
            if i.cr_type == cxl_part:
                if i.part == part_of_speech:  
                    if i.crt != crt:
                        i.part_type = "variant_diff_crts"
                        new_part_type = "variant_diff_crts"
             
                    else:
                        combined = True
                        idefk = i.definition.get(part_of_speech)
                        newnew = [*idefk, *definition]
                        i.definition[part_of_speech] = newnew
                else:
                    #CAN PROB GO (619)
                    print(f"\n\n\n 603!!!!! {i.cr_type}, {i.crt}")
                    i.cr_type = i.cr_type + " " + i.crt
                    i.part_type = "variant_diff_parts"
                    new_part_type = "variant_diff_parts"
                    
    return combined, new_part_type              

def cognate_cross_reference(the_id, entry, relevant_entries, abnormal_parts):
    '''Handle entries that have a cognate cross-reference (cxs) field.
    
    If an entry for a word (X) has a cxs field instead of a part of speech,
    the word is a less common spelling or a conjugated form of another word.
    This other word, Y, is the entry's cross-reference target (CRT). X may not have its
    own definition separate from Y's.

    For example, the entry for "flavour" has a cxs field indicating that "flavour" is
    the "chiefly British spelling of" flavor (its CRT). The entry does not include
    a definition.
    '''
    #
    cxl_part = entry.get("cxs")[0]["cxl"]
    crt = entry.get("cxs")[0]["cxtis"][0]["cxt"]

    if cxl_part is None:
        return
    if "participle of" in cxl_part:
        cxl_part = "participle of"
    if "tense" in cxl_part:
        cxl_part = "inflection (conjugated form) of"

    def_of_term = get_entry_definition(entry)
              
    if not def_of_term:
        print(f"636!!! \n\n\n {entry}")
        cxs_target_def, part_of_speech, part_type = get_cxs_target_def(crt, cxl_part)
        
        if part_type == "diff_parts":
            handle_diff_parts(the_id, cxs_target_def, cxl_part, abnormal_parts, relevant_entries, crt)
            return
        
        if cxl_part not in abnormal_parts:
            abnormal_parts.append(cxl_part)
        else:
            make_new_part_type, dupe_defs_or_parts = check_for_duplicates(cxs_target_def, relevant_entries, part_of_speech, cxl_part, crt)
            if dupe_defs_or_parts:
                return
            else:
                if make_new_part_type is not None:
                    part_type = make_new_part_type
        print(f"APPENDING IN COGNATE CROSS REFERENCE--ENTRY DOES NOT HAVE ITS OWN DEF. DEF IS CXS TARGET DEF. 541. DEF {cxs_target_def}. PROB A PROBLEM.")                
        relevant_entries.append(Nonstandard(the_id, part_type, part_of_speech, cxs_target_def, crt, cxl_part))
                      
    else:
        print(entry, "PART IS NONE BUT HAS DEF \n\n____________________\n\n\n\n")
        ###NEED ACTUAL PART HERE
        part_type = "cxs_entry"
            
        if cxl_part not in abnormal_parts:
            abnormal_parts.append(cxl_part)

        else:  
            make_new_part_type, dupe_defs_or_parts = check_for_duplicates(def_of_term, relevant_entries, cxl_part, cxl_part, crt)
            if dupe_defs_or_parts:
                return
            else:
                if make_new_part_type is not None:
                    part_type = make_new_part_type    
        print(f"APPENDING IN COGNATE CROSS REFERENCE--ENTRY HAS OWN DEF. DEF IS def of term. 560. DEF {def_of_term}. PROB A PROBLEM.")  
        relevant_entries.append(Nonstandard(the_id, part_type, cxl_part, def_of_term, crt, cxl_part))
        
###precautionary check to ensure there are no duplicate menu options ADD
def main_entry_with_cxs(the_id, entry, relevant_entries, abnormal_parts, part):
    cxl_part = entry.get("cxs")[0]["cxl"]
    crt = entry.get("cxs")[0]["cxtis"][0]["cxt"]
    part_type = "cxs_entry"

    def_of_term = get_entry_definition(entry)  
    definition = {part: def_of_term}
    if "participle of" in cxl_part:
        cxl_part = "participle of"
    if "tense" in cxl_part:
        cxl_part = "inflection (conjugated form) of"
    
    # if cxl_part not in abnormal_parts:
    #     abnormal_parts.append(cxl_part)
    # else:
    make_new_part_type, dupe_defs_or_parts = check_for_duplicates(definition, relevant_entries, part, cxl_part, crt)
    if dupe_defs_or_parts:
        return
    else:
        if make_new_part_type is not None:
            part_type = make_new_part_type
    print(f"\n\n CXS WITH MAIN ENTRY. 696, DEFINITION: {definition} \n\n FULL ENTRY {entry}")
    relevant_entries.append(Nonstandard(the_id, part_type, part, definition, crt, cxl_part)) 

def standard_main_entry(the_id, entry, relevant_entries, normal_parts, part):
    '''Handle standard complete entries.'''
    
    print("IN STANDARD MAIN ENTRY")
    # if item == "aeon":
        
    ###TODO Cap only the first letter of k in def dict
    def_of_term = get_entry_definition(entry)  
                
    if part not in normal_parts:
        normal_parts.append(part)
        print(normal_parts)
        definition = {part: def_of_term}
        print(f"STANDARD ENTRY. 712. DEF {definition}")
        relevant_entries.append(StandardEntry(the_id, "main_entry", part, definition))
      
    ###CONFIRM THAT THERE WILL NEVER BE A DUPLICATE

def part_of_speech_finder(mw_response, item):
    
    print("\n\n\n\nin part of speech!!!!!")
    relevant_entries = []
    abnormal_parts = []
    normal_parts = []

    for entry in mw_response: 

        the_id = get_entry_id(entry)
        part = entry.get("fl")

        if the_id == item:
            if part is None:
                cognate_cross_reference(the_id, entry, relevant_entries, abnormal_parts)
                                  
            else:
                cxl_part = entry.get("cxs")
                if cxl_part is None:
                    standard_main_entry(the_id, entry, relevant_entries, normal_parts, part)
                else:
                    main_entry_with_cxs(the_id, entry, relevant_entries, abnormal_parts, part)
                
        else:
            variant_or_inflection(the_id, item, entry, relevant_entries, abnormal_parts, part)

            #If the search term (X) is a less common spelling of another word (Y), X may not have its own #entry. In that case, M-W will return the entry for Y (with Y's ID), with X listed as a variant of #Y.
            #Alternatively, X may have its own entry (with Y's ID and definition). In that case, the #definition should not be added to the list twice. 
    
    variant_entries = [i for i in relevant_entries if i.part_type == "variant_diff_crts"]
    if variant_entries:
        handle_variant_entries(relevant_entries, variant_entries)
    
    return relevant_entries

def handle_variant_entries(relevant_entries, variant_entries): 
    type_and_targets_list = []
    type_and_targets = defaultdict(list)
    definitions = []
    crts = []

    for ve in variant_entries:
        #All items in list will have same part of speech and cr_type
        p = ve.part
        ve_id = ve.the_id
        cr_type = ve.cr_type
        crts.append(ve.crt)

        type_and_targets_list.append((ve.cr_type, ve.crt))
      
        definitions.append({ve.crt: ve.definition})
        relevant_entries.pop(relevant_entries.index(ve)) 

    for k, v in type_and_targets_list:
        type_and_targets[k].append(v)
    
    if len(crts) == 2:
        targets = " and ".join(crts)
    elif len(crts) > 2:
        crts(-1, "and ")
        targets = ", ".join(crts)
    else:
        targets = crts

    type_and_targets_dict = dict(type_and_targets)
    
    print(F"APPENDING GROUPED VARIANT. OKAY IF THIS IS DIFFERENT TYPE OF DEF. TRUE DICT {type_and_targets_dict} VPOST P! {p} DEF {definitions}")
    relevant_entries.append(Nonstandard(ve_id, "variant_diff_crts", p, definitions, targets, cr_type))
   