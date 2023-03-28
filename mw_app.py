
from collections import namedtuple, defaultdict
import urllib.request, urllib.parse, urllib.error
import json
import re
import html
from flask import Flask, request, render_template
from num2words import num2words
import grammar
from grammar_constants import ORDINALS
from classes import StandardEntry, Nonstandard, Number, Compound, CmosAnswerReady, ExistingCompound

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
        defs_to_get = [k for k,v in request.form.items() if v == "on"]
        def_list = [request_url_builder(item, is_a_compound=False, just_get_def=True) for item in defs_to_get]
        term_and_def_dict = dict(zip(defs_to_get, def_list))
        terms_page = render_template('_terms.html', answer=term_and_def_dict)

        return terms_page

    terms_page = render_template('_terms.html')
    return terms_page

@app.route('/_compounds.html', methods=['GET', 'POST'])
def hyphenation_answer():
    if request.method == 'POST':
        if request.form.get('start_compounds') is not None:
            return render_template('_compounds.html', first_page=True)
      
        if request.form.get("user_compound") is not None:        
            user_input = html.escape(request.form['user_compound']).lower()
            
            #Using a regex instead of "if '-' in user_input" to catch/ignore any 
            # stray characters/extra input
            hyphenated_compound = re.search(r"[\w\d]+-[\w\d]+", user_input)
            if hyphenated_compound is None:
                return render_template('_compounds.html', first_page=True,
                    mistake=True, no_hyphen=True)
            
            remaining = user_input[hyphenated_compound.end(): ]
            if "-" in remaining:
                return render_template('_compounds.html', first_page=True,
                    mistake=True, multiple_hyphens=True)
            
            compound_from_input = user_input[hyphenated_compound.start():hyphenated_compound.end()]
            elements_of_compound = compound_from_input.split("-") 
            compound = Compound(elements_of_compound, compound_from_input)

            has_numeral, idx_and_type = check_for_numerals(compound)
            if has_numeral:
                new_page = handle_num_elements(compound, idx_and_type)
                return new_page
            
            is_a_compound = True
            results = request_url_builder(compound, is_a_compound)
            if results.r_answer_ready is False:
                new_page = render_template('_compounds.html', defs_to_show=results.r_outcome, search_term=compound.elements, outcome_header = results.r_outcome_header)
            else:
                new_page = render_by_type(results)
            
            return new_page

        if request.form.get("part_of_speech_selections") is not None:
            if "non_numeric_element" in request.form.keys():
                selected = ["number", request.form['non_numeric_element']]
            else:
                selected = [request.form["first_part_of_speech"].lower(), 
                    request.form["second_part_of_speech"].lower()]
            final_outcome = grammar.cmos_rules(selected)

            newest_page = render_template('_compounds.html', standard=final_outcome)
            return newest_page

    return render_template('_compounds.html', first_page=True)

def check_for_numerals(compound):
    has_numeral = False
    idx_and_type = {}

    for idx, element in enumerate(compound.elements):
        if element.isnumeric():
            has_numeral = True
            idx_and_type[idx] = "cardinal"
        else:
            for ending in ORDINALS:
                if element.endswith(ending):
                    split_num = element.split(ending)
                    if split_num[0].isnumeric():
                        has_numeral = True
                        idx_and_type[idx] = ending        

    return has_numeral, idx_and_type

def handle_num_elements(compound, idx_and_type):
    num_results = grammar.check_cmos_num_rules(compound, idx_and_type)
    
    if num_results.num_answer_ready:             
        new_page = render_template('_compounds.html', num=num_results.num_outcome)                    
    
    else:
        NumericElementResults = namedtuple('Results', ['ne_answer_ready', 'ne_outcome', 'ne_outcome_type', 'ne_outcome_header'])
        ne_answer_ready = False
        is_a_compound = False
                        
        for k,v in idx_and_type.items():
            if v == "cardinal":
                spelled_out = num2words(compound.elements[k])
            else:
                ord_num = compound.elements[k].split(v)
                num_spelled_out = num2words(ord_num[0])
                spelled_out = num_spelled_out + v
        
            num_element = Number(compound.elements[k], spelled_out, {k:v})
          
        #This will always have a length of 1, because if both elements of the compound are numbers,
        #an answer will have been returned to the user.
        which = [j for i,j in enumerate(compound.elements) if i not in idx_and_type.keys()] 
        
        mw_response = request_url_builder(*which, is_a_compound)

        relevant_entries = parse_response(mw_response, *which)
        ne_outcome = [num_element, [relevant_entries]]
        ne_outcome_type = "comp_with_number"
        ne_outcome_header = "NUM"
        ne_results = NumericElementResults(ne_answer_ready, ne_outcome, ne_outcome_type, ne_outcome_header)
        new_page = render_template('_compounds.html', comp_with_number = ne_results.ne_outcome, search_term = compound.elements, header=ne_results.ne_outcome_header, type=ne_results.ne_outcome_type)
    
    return new_page

def render_by_type(results):
    #compounds.html template displays outcomes differently depending on the outcome type. To do that, 
    #render_template takes the outcome type as a keyword argument set to the outcome. This function
    #passes those values to render_template as kwargs.
    
    arg_dict = {results.r_outcome_type: results.r_outcome, "header": results.r_outcome_header}
    new_page = render_template('_compounds.html', **arg_dict)

    return new_page
    
def request_url_builder(term, is_a_compound, just_get_def=None):
    '''Build and send the request to Merriam-Webster's Collegiate® Dictionary with Audio API.'''
    if is_a_compound:
        search_term = term.full
    else:
        search_term = term
    
    constructed = BASE + search_term + QUERY_STRING + "key=" + MW_KEY
    with urllib.request.urlopen(constructed) as response:
        mw_response = json.load(response)
   
    if just_get_def is not None:
        shortdef = mw_response[0]["shortdef"]
        return shortdef[0]
    
    if is_a_compound:
        return compound_checker(mw_response, term)

    return mw_response

def compound_checker(mw_response, compound):
    Results = namedtuple('Results', ['r_answer_ready', 'r_outcome', 'r_outcome_type', 'r_outcome_header'])
    
    outcomes_by_comp_type = defaultdict(list)
    r_answer_ready = False
    r_outcome = None
    r_outcome_type = None
    r_outcome_header = None

    validity = confirm_entry_validity(mw_response)
    answers = []
    #If there is no entry for the compound, check whether any CMoS standards apply to the compound. If none do,
    #the compound will be split up, and each element of the compound will be handled separately.
    if validity == "empty" or validity == "typo":
        ele_answer_ready, ele_outcome = grammar.check_first_element_lists(compound)
        if ele_answer_ready:
            r_answer_ready = True
            r_outcome = ele_outcome
            r_outcome_type = "standard"
            r_outcome_header = "According to Chicago Manual of Style hyphenation standards, your compound should be handled as follows."
      
    else:  
        #Checks whether the term is in the dictionary as a closed or open compound
        all_forms = {compound.full: "hyphenated compound", compound.open: "open compound", compound.closed: "closed compound"}
        
        compound_entries = {}
        for k,v in all_forms.items():
            relevant_entries = parse_response(mw_response, k, comp_in_mw=True)
            if relevant_entries:
                compound_entries[k] = relevant_entries

        if len(compound_entries) == 0:
            r_answer_ready = False
        
        else:
            all_entries = []
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
                        entry_outcome = grammar.in_mw_as_main_entry(compound_type, ce, compound.full)        
                       
                    ##what to do with diff cxts?
                    if ce.part_type == "variant_or_cxs" or ce.part_type == "one_of_diff_parts":
                        entry_outcome = grammar.in_mw_as_variant(compound_type, ce, compound.full)
                    
                    all_entries.append(ExistingCompound({compound_type: entry_outcome}, "found_in_MW"))
     
            r_outcome = all_entries
            r_outcome_header = ExistingCompound.format_compound_header(compound)
            r_answer_ready = True
            r_outcome_type = "found_in_MW"   
        
    # #Handles each part of the compound separately
    if not r_answer_ready:
        is_a_compound = False
        r_answer_ready, r_outcome, r_outcome_type, r_outcome_header = handle_separately(is_a_compound, compound)
        
    results = Results(r_answer_ready, r_outcome, r_outcome_type, r_outcome_header)
    
    return results

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
        typo_in_input = all(isinstance(entry, str) for entry in mw_response)
        if typo_in_input:
            return "typo"
        else:
            return "valid"

def handle_separately(is_a_compound, compound):
    mw_responses = [request_url_builder(element, is_a_compound) for element in compound.elements]

    validity = [confirm_entry_validity(i) for i in mw_responses]
    
    if validity[0] == "valid" and validity[1] == "valid":
        compound_and_responses = dict(zip(compound.elements, mw_responses))
        relevant_entries = [parse_response(v, k) for k, v in compound_and_responses.items()]
      
        answer_ready = False
        outcome = relevant_entries
        outcome_type = "need user input"
        outcome_header = "Please pick a part of speech."
    else:
        answer_ready, outcome, outcome_type, outcome_header =\
            handle_invalid_entries(mw_responses, compound, validity)
    
    return answer_ready, outcome, outcome_type, outcome_header

def handle_invalid_entries(mw_responses, compound, validity):
    answer_ready = True
    outcome_type = "typo"
    outcome_header = f'''At least one element of the compound you entered,
        '{compound.full}', appears to be misspelled.'''
    
    if validity[0] == "typo" and validity[1] == "typo":
        outcome = (f"Both elements of the compound you entered are misspelled. "
        f"However, the dictionary returned spelling suggestions for both elements. "
        f"Please review the suggestions and enter another compound. "
        f"Spelling suggestions for the first element, '{compound.elements[0]},' are as follows: "
        f"{mw_responses[0]}. "
        f"Spelling suggestions for the second element, '{compound.elements[1]},' are as follows: "
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
                f"for '{compound.elements[k]}', which is misspelled: "
                f"{mw_responses[k]}.")
                outcomes.append(o)
            if v == "empty":
                o = (f"The dictionary did not return any spelling suggestions for "
                f"'{compound.elements[k]}', which is misspelled.")
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

    If the search term (X) is a less common spelling of another word (Y), X may not
    have its own entry. In that case, M-W will return the entry for Y (with Y's ID),
    with X listed as a variant, inflection, or stem of Y.

    All variants and inflections are stems, but all stems are not variants/inflections.

    An inflection is "the change of form that words undergo in different grammatical contexts,
    such as tense or number." 
    A variant is "a different spelling or styling" of a word. 
    Stems include all variants and inflections but also include "undefined entry words," which are words "derived from or related to" the word being defined.
    
    """
    add = False
    
    vrs = entry.get("vrs")
    inflections = entry.get("ins")
    stems = entry['meta'].get("stems")
               
    if vrs is None and inflections is None and stems is None:
        return

    if vrs is not None:
        term_is_variant = is_variant(item, vrs)
        if term_is_variant: 
            add, stem_defs, relation_to_variant = get_variants(entry, vrs, relevant_entries, part_of_speech)
        
    elif inflections is not None:
        term_is_inflection, inflection_label = is_inflection(inflections, item)
        if term_is_inflection:
            add, stem_defs, relation_to_variant = get_inflections(entry, inflection_label, relevant_entries, part_of_speech)
        
    else:
        term_is_stem=is_stem(stems, item)
        if term_is_stem:
            add, stem_defs, relation_to_variant = get_stems(entry, relevant_entries, part_of_speech)  
        
    if add:    
        part_type = check_for_multiple_parts(stem_defs)
        for k, v in stem_defs.items():
            ###ADD CHECKS OF BAD PARTS OF SPEECH HERE?
            if relation_to_variant in Nonstandard.grouped.keys():
                here = Nonstandard.grouped[relation_to_variant]
                if here.part == k:
                    new_cxt = here.cxt + " and " + the_id
                    here.cxt = new_cxt
                    here.part_type = "one_diff_cxts"
                    relevant_entries.append(Nonstandard(the_id, "one_diff_cxts", k, stem_defs, new_cxt, relation_to_variant))  
            else:
                relevant_entries.append(Nonstandard(the_id, part_type, k, stem_defs, the_id, relation_to_variant))  

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

    add, stem_defs = get_stem_defs(relevant_entries, entry, part_of_speech)
    
    return add, stem_defs, relation_to_variant

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
    
    add, stem_defs = get_stem_defs(relevant_entries, entry, part_of_speech)
  
    return add, stem_defs, relation_to_variant

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
   
    add, stem_defs = get_stem_defs(relevant_entries, entry, part_of_speech)
    
    return add, stem_defs, relation_to_variant

def get_stem_defs(relevant_entries, entry, part_of_speech):
    '''Retrieve definitions of variants, inflections, and stems.

    Although the function's name is "get_stem_defs," it also retrieves the
    definitions of headwords that are variants or inflections or another word,
    since variants and inflections are also considered stems.
    '''

    add = False
    stem_defs = None
    
    def_of_term = get_entry_definition(entry)  
    if def_of_term:   
        dupe_def = def_is_duplicate(relevant_entries, def_of_term)
        if not dupe_def:
            stem_defs = {part_of_speech: def_of_term}
            add = True

    return add, stem_defs

def cognate_cross_reference(the_id, entry, relevant_entries, item):
    '''Handle entries that have a cognate cross-reference (cxs) field.
    
    If an entry for a word (X) has a cxs field instead of a part of speech,
    the word is a less common spelling or a conjugated form of another word.
    This other word, Y, is the entry's cross-reference target (CRT). X will not have its
    own definition separate from Y's.
    '''

    cxl_part = entry.get("cxs")[0]["cxl"]
    cxt = entry.get("cxs")[0]["cxtis"][0]["cxt"]
    if cxl_part is None:
        return
    
    is_a_compound = False
    split_id = cxt.split(" ")
    if len(split_id) > 1:
        search_term = split_id[0] + "%20" + split_id[1]
    else:
        search_term = cxt

    cxs_mw_response = request_url_builder(search_term, is_a_compound)
    cxs_defs = {}
    part_of_speech = None

    #Avoid long cxls like "present tense second-person singular and present tense plural of"
    if "participle of" in cxl_part:
        cxl_part = "participle of"
    elif "tense" in cxl_part:
        cxl_part = "inflection (conjugated form) of"

    for i in cxs_mw_response:
        part_of_speech = i.get("fl")
        
        #If the original search term is a verbal inflection, retrieve only verb definitions.
        if "tense" in cxl_part or "participle" in cxl_part or "conjugated form" in cxl_part:
            if part_of_speech == "verb":
                cxs_target_def = get_entry_definition(i)
                dupe_def = def_is_duplicate(relevant_entries, cxs_target_def)
                if not dupe_def:
                    cxs_defs[part_of_speech] = cxs_target_def
                break
        else:
            if part_of_speech == "biographical name" or part_of_speech == "auxiliary verb" or part_of_speech == "abbreviation" or part_of_speech == "symbol" or part_of_speech == "trademark":
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
        relevant_entries.append(Nonstandard(the_id, part_type, k, cxs_defs, cxt, cxl_part))  

def def_is_duplicate(relevant_entries, definition):
    dupe_def = False

    for i in relevant_entries:  
        for k, v in i.definition.items():
            if v == definition:
                dupe_def = True

    return dupe_def

def main_entry_with_cxs(the_id, entry, relevant_entries, part):
    cxl_part = entry.get("cxs")[0]["cxl"]
    cxt = entry.get("cxs")[0]["cxtis"][0]["cxt"]
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
            relevant_entries.append(Nonstandard(the_id, part_type, part, definition, cxt, cxl_part)) 

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

def parse_response(mw_response, item, comp_in_mw=False): 
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
            ##This check excludes comparatives. TODO: EXPLAIN THIS.
            for k,v in StandardEntry.stems_and_parts.items():
                if k == part and the_id in v:
                    existing_entry = True
            if not existing_entry:
                variant_inflection_or_stem(the_id, item, entry, relevant_entries, part)
    
    if not comp_in_mw:
        to_format = [entry for entry in relevant_entries if entry.part_type != "one_diff_cxts"]
        [format_entries(entry) for entry in to_format]
        
        cxt_entry_combiner(relevant_entries)
        for i in relevant_entries:
            if i.part_type != "main_entry":
                i.to_display = Nonstandard.format_displayed_header(i)
   
    return relevant_entries

def format_entries(entry):
    for k, v in entry.definition.items():
        if v.startswith("—"):
            v_without_leading_dash = re.sub(r"^—", "", v)
            entry.definition[k] = v_without_leading_dash.capitalize()
        else:
            entry.definition[k] = v.capitalize()

def cxt_entry_combiner(relevant_entries):
    entries = [(i.cr_type, i) for i in relevant_entries if i.part_type == "one_diff_cxts"]
    
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
       
        joined_defs = "; ".join(all_defs)
        keep.definition[keep.part] = joined_defs
        format_entries(keep)
        keep.to_display = Nonstandard.format_displayed_header(keep)
   
    for item in discard:
        to_discard = relevant_entries.index(item)
        relevant_entries.pop(to_discard)
   