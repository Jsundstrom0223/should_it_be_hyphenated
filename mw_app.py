
from collections import namedtuple, defaultdict
import urllib.request, urllib.parse, urllib.error
import json
import re
import html
from flask import Flask, request, render_template
from num2words import num2words
import grammar
from grammar_constants import ORDINAL_ENDINGS
from classes import StandardEntry, Nonstandard, Number

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
        defs_to_get = [k for k,v in request.form.items() if v == "on"]
        def_list = [request_url_builder(item, is_a_compound=False, just_get_def=True) for item in defs_to_get]
        term_and_def_dict = dict(zip(defs_to_get, def_list))
        
        terms_page = render_template('_terms.html', answer=term_and_def_dict)
        return terms_page

    terms_page = render_template('_terms.html')
    return terms_page

@app.route('/_compounds.html', methods=['GET', 'POST'])
def hyphenation_answer():
    global elements_of_compound 
    
    if request.method == 'POST':
        if request.form.get('start_compounds') is not None:
            return render_template('_compounds.html', first_page=True)
      
        if request.form.get("user_compound") is not None:        
            user_input = html.escape(request.form['user_compound']).lower()
            
            #Using a regex instead of "if '-' in user_input" to catch any stray characters/extra input
            hyphenated_compound = re.search(r"[\w\d]+-[\w\d]+", user_input)
            if hyphenated_compound is None:
                return render_template('_compounds.html', first_page=True,
                    mistake=True, no_hyphen=True)
            
            compound_from_input = user_input[hyphenated_compound.start():hyphenated_compound.end()]
            elements_of_compound = compound_from_input.split("-") 
            remaining = user_input[hyphenated_compound.end(): ]
            
            if "-" in remaining:
                return render_template('_compounds.html', first_page=True,
                    mistake=True, multiple_hyphens=True)
            
            includes_a_number = False
            if elements_of_compound[0].isnumeric() or elements_of_compound[1].isnumeric():
                includes_a_number = True
                ordinal = False
                ord_end = None
            else:
                for ending in ORDINAL_ENDINGS:
                    if elements_of_compound[0].endswith(ending):
                        split_num = elements_of_compound[0].split(ending)
                        if split_num[0].isnumeric():
                            includes_a_number = True
                            ordinal = True
                            ord_end = ending

            if includes_a_number:
                new_page = comp_with_num_element(elements_of_compound, ordinal, ord_end)
                return new_page
            
            is_a_compound = True
            results, elements_of_compound = request_url_builder(compound_from_input, is_a_compound, elements_of_compound)
            if results.r_answer_ready is False:
                new_page = render_template('_compounds.html', defs_to_show=results.r_outcome, search_term=elements_of_compound, outcome_header = results.r_outcome_header)
            else:
                new_page = render_by_type(results)
            
            return new_page

        if request.form.get("part_of_speech_selections") is not None:
            if "non_numeric_element" in request.form.keys():
                selected = ["number", request.form['non_numeric_element']]
            else:
                selected = [request.form["first_part_of_speech"].lower(), 
                    request.form["second_part_of_speech"].lower()]
            final_outcome = grammar.cmos_rules(selected, elements_of_compound)

            newest_page = render_template('_compounds.html', standard=final_outcome)
            return newest_page

    return render_template('_compounds.html', first_page=True)

def comp_with_num_element(elements_of_compound, ordinal, ord_end):
    num_results = grammar.number_in_compound(elements_of_compound, ordinal)
    
    if num_results.num_answer_ready:             
        new_page = render_template('_compounds.html', num=num_results.num_outcome)
                        
    else:
        NumericElementResults = namedtuple('Results', ['ne_answer_ready', 'ne_outcome', 'ne_outcome_type', 'ne_outcome_header'])
        ne_answer_ready = False
        is_a_compound = False
                        
        if not ordinal:
            spelled_out = num2words(elements_of_compound[0])
        else:
            ord_num = elements_of_compound[0].split(ord_end)
            num_spelled_out = num2words(ord_num[0])
            spelled_out = num_spelled_out + ord_end

        num_element = Number(elements_of_compound[0], spelled_out, ordinal)
        mw_response = request_url_builder(elements_of_compound[1], is_a_compound)

        relevant_entries = parse_entries(mw_response, elements_of_compound[1])
        ne_outcome = [num_element, [relevant_entries]]
        ne_outcome_type = "comp_with_number"
  
        ne_outcome_header = "NUM"
        ne_results = NumericElementResults(ne_answer_ready, ne_outcome, ne_outcome_type, ne_outcome_header)
        new_page = render_template('_compounds.html', comp_with_number = ne_results.ne_outcome, search_term = elements_of_compound, header=ne_results.ne_outcome_header, type=ne_results.ne_outcome_type)
    
    return new_page

def render_by_type(results):
    #compounds.html template displays outcomes differently depending on the outcome type. To do that, 
    #render_template takes the outcome type as a keyword argument set to the outcome. This function
    #passes those values to render_template as kwargs.
    
    arg_dict = {results.r_outcome_type: results.r_outcome, "header": results.r_outcome_header}
    new_page = render_template('_compounds.html', **arg_dict)

    return new_page
    
def request_url_builder(compound_from_input, is_a_compound, elements_of_compound=None, just_get_def=None):
    '''Build and send the request to Merriam-Webster's Collegiate® Dictionary with Audio API.'''
    
    constructed = BASE + compound_from_input + QUERY_STRING + "key=" + MW_KEY
    with urllib.request.urlopen(constructed) as response:
        mw_response = json.load(response)
   
    if just_get_def is not None:
        shortdef = mw_response[0]["shortdef"]
        return shortdef[0]
    
    if is_a_compound:
        return compound_checker(mw_response, compound_from_input, elements_of_compound)

    return mw_response

def compound_checker(mw_response, compound_from_input, elements_of_compound):
    Results = namedtuple('Results', ['r_answer_ready', 'r_outcome', 'r_outcome_type', 'r_outcome_header'])
    
    outcomes_by_comp_type = defaultdict(list)
    r_answer_ready = False
    r_outcome = None
    r_outcome_type = None
    r_outcome_header = None

    validity = confirm_entry_validity(mw_response)

    #If there is no entry for the compound, check whether any CMoS standards apply to the compound. If none do,
    #the compound will be split up, and each element of the compound will be handled separately.
    if validity == "empty" or validity == "typo":
        ele_results = grammar.check_first_element_lists(elements_of_compound)
        if ele_results.ele_answer_ready:
            r_answer_ready = True
            r_outcome = ele_results.ele_outcome
            r_outcome_type = "standard"
            r_outcome_header = "something"
    
    else:  
        no_hyphen = elements_of_compound[0] + elements_of_compound[1]
        open_compound = elements_of_compound[0] + " " + elements_of_compound[1]

        #Checks whether the term is in the dictionary as a closed or open compound
        all_forms = {compound_from_input: "hyphenated compound", open_compound: "open compound", no_hyphen: "closed compound"}
        
        compound_entries = {}
        for k,v in all_forms.items():
            relevant_entries = parse_entries(mw_response, k)
            if relevant_entries:
                compound_entries[k] = relevant_entries

        if len(compound_entries) == 0:
            r_answer_ready = False
        
        else:
            outcomes = []
            for compounds, entries in compound_entries.items(): 
                for ce in entries:
                    if "-" in ce.the_id:
                        compound_type = "a hyphenated compound"
                    else:
                        split_k = ce.the_id.split(" ")
                        if len(split_k) > 1:
                            compound_type = "an open compound"
                        else:
                            compound_type = "a closed compound"
                   
                    if ce.part_type == "main_entry":
                        outcome = grammar.in_mw_as_main_entry(compound_type, ce, compound_from_input)        
                       
                    ##what to do with diff crts?
                    if ce.part_type == "variant_or_cxs" or ce.part_type == "one_of_diff_parts":
                        outcome = grammar.in_mw_as_variant(compound_type, ce, compound_from_input)
                    
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
                    
            r_outcome_header = f"M-W lists '{compound_from_input}' as {form}. Details are provided below."
            r_answer_ready = True
            r_outcome_type = "found_in_MW"
            r_outcome = outcomes
        
    # #Handles each part of the compound separately
    if not r_answer_ready:
        is_a_compound = False
        r_answer_ready, r_outcome, r_outcome_type, r_outcome_header = handle_separately(is_a_compound, elements_of_compound)
        
    results = Results(r_answer_ready, r_outcome, r_outcome_type, r_outcome_header)
    
    return results, elements_of_compound

def confirm_entry_validity(mw_response):
    '''Confirm that the search term is valid.

    Check for empty responses and responses that consist entirely of strings (no JSON).
    When a word isn't in Merriam-Webster's Collegiate® Dictionary but there are
    other similar words in the dictionary, the API returns a list of those words
    (a list of strings). If there are no similar words, it returns an empty list.
    '''

    if len(mw_response) == 0:
        return "empty"

    else:
        print(mw_response)
        typo_in_input = all(isinstance(entry, str) for entry in mw_response)
        if typo_in_input:
            return "typo"

        else:
            return "valid"

def handle_separately(is_a_compound, elements_of_compound):
    mw_responses = [request_url_builder(i, is_a_compound, elements_of_compound) for i in elements_of_compound]

    validity = [confirm_entry_validity(i) for i in mw_responses]
    
    if validity[0] == "valid" and validity[1] == "valid":
        compound_and_responses = dict(zip(elements_of_compound, mw_responses))
        relevant_entries = [parse_entries(v, k) for k, v in compound_and_responses.items()]
        answer_ready = False
        outcome = relevant_entries
        outcome_type = "need user input"
        outcome_header = "Please pick a part of speech."

    else:
        answer_ready, outcome, outcome_type, outcome_header =\
            handle_invalid_entries(mw_responses, elements_of_compound, validity)
    
    return answer_ready, outcome, outcome_type, outcome_header

def handle_invalid_entries(mw_responses, elements_of_compound, validity):
    answer_ready = True
    outcome_type = "typo"
    outcome_header = f'''At least one element of the compound you entered,
        '{'-'.join(elements_of_compound)}', appears to be misspelled.'''
    
    if validity[0] == "typo" and validity[1] == "typo":
        outcome = (f"Both elements of the compound you entered are misspelled. "
        f"However, the dictionary returned spelling suggestions for both elements. "
        f"Please review the suggestions and enter another compound. "
        f"Spelling suggestions for the first element, '{elements_of_compound[0]},' are as follows: "
        f"{mw_responses[0]}. "
        f"Spelling suggestions for the second element, '{elements_of_compound[1]},' are as follows: "
        f"{mw_responses[1]}.")
     
    elif validity[0] == "empty" and validity[1] == "empty":
        outcome = (f"Both parts of the compound you entered are misspelled, "
        f" and the dictionary did not return any alternative spellings. "
        f"Please check the spelling of your compound and enter it again.")
    
    else:
        outcomes = []
        both = {0: validity[0], 1: validity[1]}
        for k,v in both.items():
            if v == "typo":
                o = (f"The dictionary returned the following spelling suggestions "
                f"for '{elements_of_compound[k]}', which is misspelled: "
                f"{mw_responses[k]}.")
                outcomes.append(o)
            if v == "empty":
                o = (f"The dictionary did not return any spelling suggestions for "
                f"'{elements_of_compound[k]}', which is misspelled.")
                outcomes.append(o)
        outcome = " ".join(outcomes).strip("'[]")


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
        raw_def = entry['shortdef'] 
    else:
        raw_def = entry['def']

    def_of_term = "; ".join(raw_def)

    return def_of_term

def check_for_multiple_parts(defs):
    if len(defs) > 1:
        part_type = "one_of_diff_parts"
    else:
        part_type = "variant_or_cxs"
        
    return part_type

def variant_inflection_or_stem(the_id, item, entry, relevant_entries, part_of_speech):
    """Handle entries in which the headword is an inflection, variant, or stem.

    If the search term (X) is a less common spelling of another word (Y), X may not have its own #entry. In that case, M-W will return the entry for Y (with Y's ID), with X listed as a variant, inflection, or stem of #Y.
    Alternatively, X may have its own entry (with Y's ID and definition). In that case, the 
    definition should not be added to the list twice. 

    An inflection is "the change of form that words undergo in different grammatical contexts,
    such as tense or number." 
    A variant is "a different spelling or styling" of a word. 
    Stems include all variants and inflections but also include "undefined entry words," which are words "derived from or related to" the word being defined. All variants and inflections are stems, but all stems are not variants/inflections.
    
    """
    add = False
    inflections = entry.get("ins")
    vrs = entry.get("vrs")
    stems = entry['meta'].get("stems")
               
    if vrs is None and inflections is None and stems is None:
        return

    if vrs is not None:
        term_is_variant = is_variant(item, vrs)
        if term_is_variant: 
            add, var_defs, relation_to_variant = get_variants(entry, vrs, relevant_entries, part_of_speech)
        
    elif inflections is not None:
        term_is_inflection, inflection_label = is_inflection(inflections, item)
        if term_is_inflection:
            add, var_defs, relation_to_variant = get_inflections(entry, inflection_label, relevant_entries, part_of_speech)
        
    else:
        term_is_stem=is_stem(stems, item)
        if term_is_stem:
            add, var_defs, relation_to_variant = get_stems(entry, relevant_entries, part_of_speech)  
        
    if add:    
        part_type = check_for_multiple_parts(var_defs)

        for k, v in var_defs.items():
            ###ADD CHECKS OF BAD PARTS OF SPEECH HERE?
            if relation_to_variant in Nonstandard.grouped.keys():
                here = Nonstandard.grouped[relation_to_variant]
                if here.part == k:
                    new_crt = here.crt + " and " + the_id
                    here.crt = new_crt
                    here.part_type = "one_diff_crts"
                    relevant_entries.append(Nonstandard(the_id, "one_diff_crts", k, var_defs, new_crt, relation_to_variant))  
            else:
                relevant_entries.append(Nonstandard(the_id, part_type, k, var_defs, the_id, relation_to_variant))  

def is_variant(item, vrs):
    vrs = vrs[0]
    term_is_variant = False

    if "*" in vrs['va']:
        va = vrs['va'].replace("*", "")
    else:
        va = vrs['va']

    if va == item:
        term_is_variant = True
    
    return term_is_variant

def get_variants(entry, vrs, relevant_entries, part_of_speech):
    add = False
    relation_to_variant = None

    vrs = vrs[0]
    vl = vrs.get('vl')
    vl_options = {"or less commonly": "less common spelling of", "or": "alternative spelling of", "or chiefly British": "chiefly British spelling of"}
  
    if vl in vl_options.keys():
        relation_to_variant = vl_options[vl]
    else:
        if vl not in vl_options.keys() or vl is None:
            relation_to_variant = "variant of"

    add, var_defs = get_var_defs(relevant_entries, entry, part_of_speech)
    
    return add, var_defs, relation_to_variant

def is_inflection(inflections, item):
    term_is_inflection = False
    inflection_label = None

    for i in inflections:
        inf = i['if']
        if "*" in inf:
            inf = inf.replace("*", "")
        if inf == item:
            inflection_label = i.get('il')
            term_is_inflection = True

    return term_is_inflection, inflection_label

def get_inflections(entry, inflection_label, relevant_entries, part_of_speech):
    add = False
    relation_to_variant = None
    
    if part_of_speech == "verb":
        if inflection_label is not None and "participle" in inflection_label:
            relation_to_variant = "participle of"
        else:
            relation_to_variant = "inflection (conjugated form) of"   
    else:
        relation_to_variant = "variant of"
    
    add, var_defs = get_var_defs(relevant_entries, entry, part_of_speech)
  
    return add, var_defs, relation_to_variant

def is_stem(stems, item):
    term_is_stem = False
    if item in stems:
        term_is_stem = True

    return term_is_stem

def get_stems(entry, relevant_entries, part_of_speech):
    add = False
    relation_to_variant = None
    
    if entry.get("cxs") is not None:
        relation_to_variant = entry.get("cxs")[0]["cxl"]   
        # if relation_to_variant == "plural of":
        #     TO-DO: list of parts/cxls to avoid       
    else:
        relation_to_variant = "variant of"
   
    add, var_defs = get_var_defs(relevant_entries, entry, part_of_speech)
    
    return add, var_defs, relation_to_variant

def get_var_defs(relevant_entries, entry, part_of_speech):
    add = False
    var_defs = None
    
    def_of_term = get_entry_definition(entry)  
    if def_of_term:   
        dupe_def = def_is_duplicate(relevant_entries, def_of_term)
        if not dupe_def:
            var_defs = {part_of_speech: def_of_term}
            add = True

    return add, var_defs

def cognate_cross_reference(the_id, entry, relevant_entries, item):
    '''Handle entries that have a cognate cross-reference (cxs) field.
    
    If an entry for a word (X) has a cxs field instead of a part of speech,
    the word is a less common spelling or a conjugated form of another word.
    This other word, Y, is the entry's cross-reference target (CRT). X may not have its
    own definition separate from Y's.

    For example, the entry for "flavour" has a cxs field indicating that "flavour" is
    the "chiefly British spelling of" flavor (its CRT). The entry does not include
    a definition.
    '''

    cxl_part = entry.get("cxs")[0]["cxl"]
    crt = entry.get("cxs")[0]["cxtis"][0]["cxt"]

    if cxl_part is None:
        return
    
    #Avoid long cxls like "present tense second-person singular and present tense plural of"
    if "participle of" in cxl_part:
        cxl_part = "participle of"
    elif "tense" in cxl_part:
        cxl_part = "inflection (conjugated form) of"

    def_of_term = get_entry_definition(entry)

    ###okay as is or will there be ones with their own ef?        
    if not def_of_term:
        get_cxs_target_def(the_id, crt, cxl_part, relevant_entries)

def get_cxs_target_def(the_id, crt, cxl_part, relevant_entries):
    is_a_compound = False
    split_id = crt.split(" ")

    #Check whether the cross-reference target is two words; if it is, URL encode the space character.
    if len(split_id) > 1:
        search_term = split_id[0] + "%20" + split_id[1]
    else:
        search_term = crt

    cxs_mw_response = request_url_builder(search_term, is_a_compound)
    cxs_defs = {}
    part_of_speech = None
    
    for i in cxs_mw_response:
        part_of_speech = i.get("fl")
        
        #If the original search term is a verbal inflection, retrieve only verb definitions.
        if "tense" in cxl_part or "participle" in cxl_part or "conjugated form" in cxl_part:
            if part_of_speech == "verb":
                cxs_target_def = get_entry_definition(i)
                #ADD CHeCK? # if cxs_target_def:
                dupe_def = def_is_duplicate(relevant_entries, cxs_target_def)
                if not dupe_def:
                    cxs_defs[part_of_speech] = cxs_target_def
                break
            
        else:
            if part_of_speech == "biographical name" or part_of_speech == "auxiliary verb" or part_of_speech == "abbreviation" or part_of_speech == "symbol":
                continue
            
            cxs_target_def = get_entry_definition(i)
            if cxs_target_def: 
                cxs_defs[part_of_speech] = cxs_target_def
                dupe_def = def_is_duplicate(relevant_entries, cxs_target_def)
                if not dupe_def:
                    cxs_defs[part_of_speech] = cxs_target_def
                else:
                    continue

    part_type = check_for_multiple_parts(cxs_defs)
          
    for k, v in cxs_defs.items():
        relevant_entries.append(Nonstandard(the_id, part_type, k, cxs_defs, crt, cxl_part))  

###is this a bad name
def def_is_duplicate(relevant_entries, definition):
    dupe_def = False

    for i in relevant_entries:  
        for k, v in i.definition.items():
            if v == definition:
                dupe_def = True

    return dupe_def

def main_entry_with_cxs(the_id, entry, relevant_entries, part):
    cxl_part = entry.get("cxs")[0]["cxl"]
    crt = entry.get("cxs")[0]["cxtis"][0]["cxt"]
    part_type = "cxs_entry"
    
    if "participle of" in cxl_part:
        cxl_part = "participle of"
    elif "tense" in cxl_part:
        cxl_part = "inflection (conjugated form) of"

    def_of_term = get_entry_definition(entry)  
    if def_of_term:
        dupe_def = def_is_duplicate(relevant_entries, def_of_term)
        if not dupe_def:             
            definition = {part: def_of_term}
            part_type = check_for_multiple_parts(definition)

            relevant_entries.append(Nonstandard(the_id, part_type, part, definition, crt, cxl_part)) 

def standard_main_entry(the_id, entry, relevant_entries, part):
    '''Handle standard complete entries.'''
    
    def_of_term = get_entry_definition(entry)  
    definition = {part: def_of_term}
    stems = entry['meta'].get("stems")

    dupe_part = standard_part_is_duplicate(relevant_entries, part, definition)
    if not dupe_part:
        dupe_def = def_is_duplicate(relevant_entries, def_of_term)
        if not dupe_def:
            StandardEntry.stems_and_parts[part] = stems
            relevant_entries.append(StandardEntry(the_id, "main_entry", part, definition))

def parse_entries(mw_response, item): 
    relevant_entries = []

    for entry in mw_response: 
        the_id = get_entry_id(entry)
        part = entry.get("fl")

        if the_id == item or the_id == item.capitalize():
            if part is None:
                cognate_cross_reference(the_id, entry, relevant_entries, item)            
            else:
                if part == "biographical name" or part == "auxiliary verb" or part == "abbreviation" or part == "symbol":
                    continue
              
                cxl_part = entry.get("cxs")
                if cxl_part is None:
                    standard_main_entry(the_id, entry, relevant_entries, part)
                else:
                    main_entry_with_cxs(the_id, entry, relevant_entries, part)
                
        else: 
            existing_entry = False
            ##this check excludes comparatives. EXPLAIN THIS.
            for k,v in StandardEntry.stems_and_parts.items():
                if k == part and the_id in v:
                    existing_entry = True
            if not existing_entry:
                variant_inflection_or_stem(the_id, item, entry, relevant_entries, part)

    to_format = [entry for entry in relevant_entries if entry.part_type != "one_diff_crts"]
    for entry in to_format:
        for k, v in entry.definition.items():
            entry.definition[k] = v.capitalize()

    crt_entry_combiner(relevant_entries)
    for i in relevant_entries:
        if i.part_type != "main_entry":
            i.to_display = Nonstandard.format_displayed_header(i)

    return relevant_entries

def standard_part_is_duplicate(relevant_entries, part, definition):
    dupe_part = False
    standards = [r for r in relevant_entries if r.part_type == "main_entry" and r.part == part]

    ##test with multiples (multiple defs for same part)
    for i in standards:
        if i.part == part:
            combined_defs = "; ".join([i.definition[part], definition[part]])
            i.definition[part] = combined_defs
            dupe_part = True

    return dupe_part

def crt_entry_combiner(relevant_entries):
    entries = [(i.cr_type, i) for i in relevant_entries if i.part_type == "one_diff_crts"]
    
    combined = defaultdict(list)
    for k,v in entries:
        combined[k].append(v)

    all_defs = []
    true_dict = dict(combined)
    discard = []
    
    for k, v in true_dict.items():
        for entry in v:
            if v.index(entry) == 0:
                keep = entry
            else:
                discard.append(entry)
            all_defs.append(entry.definition[entry.part])
       
        joined_defs = "; ".join(all_defs).capitalize()
        keep.definition[keep.part] = joined_defs
        keep.to_display = Nonstandard.format_displayed_header(keep)
   
    for item in discard:
        to_discard = relevant_entries.index(item)
        relevant_entries.pop(to_discard)
   