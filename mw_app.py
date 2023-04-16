
from collections import namedtuple
import urllib.request, urllib.parse, urllib.error
import json
import re
import html
from flask import Flask, request, render_template
import existing_compound_handler
import grammar
import entry_parser
from grammar_constants import ORDINALS, PART_OF_SPEECH_DEFS, IGNORED_PARTS_OF_SPEECH
from classes import ExistingCompound, NoEntries, Nonstandard, Number, StandardEntry

# with open("../../key.txt", "r") as key:
#     MW_KEY = key.read()

with open("/etc/secrets/key.txt", "r") as key:
    MW_KEY = key.read()

QUERY_STRING = "?"
BASE  = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/"

app = Flask(__name__)

@app.route("/", methods=['GET'])
def hello_world():
    """Render the landing page of the Flask app (the _base template)."""
    return render_template('_base.html')

@app.route("/how_it_works.html", methods=['GET', 'POST'])
def how_it_works():
    """Render the page that explains how the app works (the how_it_works template)."""
    return render_template('how_it_works.html')

@app.route("/_terms", methods=['GET', 'POST'])
def grammar_defs():
    """Render the _terms template, which lists grammar terms, and get their definitions.
    
    Render a list of grammar terms and retrieve two definitions of the terms selected by
    the user: the 'official' definition from Merriam-Webster's Collegiate® Dictionary and
    a 'plain English' definition written by the app's developer. 
    """
    Grammar_Defs = namedtuple('Grammar_Defs', ['term', 'official', 'plain_english'])
    defs_to_get = [k for k,v in request.form.items() if v == "on"]
    def_list = []
    
    for term in defs_to_get:
        official = call_mw_api(term, just_get_def=True)
        plain_english = PART_OF_SPEECH_DEFS.get(term)
        def_list.append(Grammar_Defs(term, official, plain_english))

    terms_page = render_template('_terms.html', answer=def_list)
    return terms_page

@app.route('/_compounds.html', methods=['GET', 'POST'])
def hyphenation_answer():
    """Render the _compounds template, which takes in a compound and displays results.
    
    Take a user-provided compound and check its validity. If the compound is valid, create an
    instance of the Compound class and pass it to the handle_comp_with_num or call_mw_api 
    function. Then render the _compounds template again, with the results of the function call.
    
    For more details, see the following documentation on the API:
    https://github.com/Jsundstrom0223/should_it_be_hyphenated/blob/main/api_explanation.md.
    """
    if request.method == 'POST':
        if request.form.get('start_compounds') is not None:
            return render_template('_compounds.html', first_page=True)

        if request.form.get("user_compound") is not None:
            user_input = html.escape(request.form['user_compound']).lower()

            #Using a regex instead of "if '-' in user_input" to catch/ignore any
            # stray characters/extra input
            hyphenated_compound = re.search(r"[\w\d]+-[\w\d]+", user_input)
            if hyphenated_compound is None:
                mistake_header = '''The input you provided lacks a hyphen ("-") or
                includes a hyphen with at least one space next to it. Please try again
                and ensure that your input includes one hyphen with no spaces around it
                (e.g., "well-being").'''
                return render_template('_compounds.html', mistake=mistake_header, first_page=True)

            remaining = user_input[hyphenated_compound.end(): ]
            if "-" in remaining:
                mistake_header = '''The input you provided includes multiple hyphens.
                Please enter a compound that has only one hyphen (e.g., "well-being").'''
                return render_template('_compounds.html', mistake=mistake_header, first_page=True)

            compound_from_input = user_input[hyphenated_compound.start(): hyphenated_compound.end()]
            elements_of_compound = compound_from_input.split("-")
            print("COMPOUND FROM INPUT", compound_from_input)

            if elements_of_compound[0] == elements_of_compound[1]:
                mistake_header = '''The elements of your compound are identical; please
                enter a compound with two unique elements.'''
                return render_template('_compounds.html', mistake=mistake_header, first_page=True)
            
            Compound = namedtuple('Compound', ['elements', 'full', 'open', 'closed'])
            open = elements_of_compound[0] + " " + elements_of_compound[1]
            closed = "".join(elements_of_compound)
            compound = Compound(elements_of_compound, compound_from_input, open, closed)

            has_numeral, idx_and_type = check_for_numerals(compound)
            if has_numeral:
                new_page = handle_comp_with_num(compound, idx_and_type)
                return new_page

            results = call_mw_api(compound, is_a_compound=True)

            if results.answer_ready is False:
                new_page = render_template('_compounds.html', display=results.outcome, search_term=compound.elements)
            else:
                new_page = render_by_type(results)

            return new_page

        if request.form.get("part_of_speech_selections") is not None:
            if "non_numeric_element" in request.form.keys():
                selected = ["number", request.form['non_numeric_element']]
            else:
                selected = [request.form["first_part_of_speech"].lower(),
                    request.form["second_part_of_speech"].lower()]
            final_outcome, final_header = grammar.cmos_rules(selected)

            final_page = render_template('_compounds.html', standard=final_outcome, header=final_header)
            return final_page

    return render_template('_compounds.html', first_page=True)

def render_by_type(results):
    """Pass the results returned by handle_comp_with_num or call_mw_api to render_template.

    Create a dictionary of kwargs and pass them to Flask's render_template function. 

    Argument:
    results: A named tuple with four named fields:
        1. answer_ready: A boolean value. False means that the user needs to provide more 
        information on the compound's use. 
        2. outcome: The information that will be displayed to the user.
        3. outcome_type: A variable that tells the _compounds template how to display that
        information.
        4. header: A summary of that information or, if answer_ready is False, an empty string.

    Returns:
    new_page: The _compounds template, with the results to be displayed to the user.
    """
    arg_dict = {results.outcome_type: results.outcome, "header": results.header}
    new_page = render_template('_compounds.html', **arg_dict)

    return new_page

def check_for_numerals(compound):
    """Check whether the user input includes a cardinal or ordinal number.
    
    If either element of the compound is a number, add its index and the type 
    of the number ("cardinal" or, for an ordinal, its ending) to idx_and_type.

    Argument:
    compound: The 'compound' named tuple created in hyphenation_answer.

    Returns:
    has_numeral: A boolean value.
    idx_and_type: A dictionary that identifies the numeric element(s) of the compound.
    """
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

def handle_comp_with_num(compound, idx_and_type):
    """Handle compounds that contain at least one numeral.
    
    Call the check_cmos_num_rules function, which checks compounds against number-related 
    hyphenation rules. If none of the rules apply to the compound, call mw_api and 
    start_parsing with only the non-numeric element of the compound.
    
    Arguments:
    compound: The 'compound' named tuple created in hyphenation_answer.
    idx_and_type: A dictionary that identifies the numeric element(s) of the compound.

    Returns:
    new_page: The _compounds template, with the results to be displayed to the user.
    """
    num_results = grammar.check_cmos_num_rules(compound, idx_and_type)

    if num_results.answer_ready:
        new_page = render_by_type(num_results)
    else:
        for k,v in idx_and_type.items():
            num_element = Number(compound.elements[k], k)

        #This will always have a length of 1.
        non_num = [v for i,v in enumerate(compound.elements) if i not in idx_and_type.keys()]
        mw_response = call_mw_api(*non_num)
        mw_entries = start_parsing(mw_response, *non_num)
      
        new_page = render_template('_compounds.html',
        comp_with_number=mw_entries, search_term = compound.elements[num_element.other],   
            num=num_element)

    return new_page

def call_mw_api(term, is_a_compound=False, just_get_def=False):
    """Build and send a request to Merriam-Webster's Collegiate® Dictionary with Audio API.
    
    Arguments:
    term: The search term used in the API call.
    is_a_compound: A boolean value. True means that compound_checker should be called and
    that its return value should be returned to hyphenation_answer.
    just_get_def: A boolean value. True means that the return value should be just
    the shortdef field of the entry rather than the full API response.
    """
    if is_a_compound:
        search_term = term.full
    else:
        search_term = term

    constructed = BASE + search_term + QUERY_STRING + "key=" + MW_KEY
    with urllib.request.urlopen(constructed) as response:
        mw_response = json.load(response)

    if just_get_def:
        shortdef = mw_response[0]["shortdef"]
        return shortdef[0]

    if is_a_compound:
        return compound_checker(mw_response, term)

    return mw_response

def compound_checker(mw_response, compound):
    """Check whether the compound is in M-W as an open, closed, or hyphenated compound.
    
    Arguments:
    mw_response: The API's response to the initial call, in which the search term is 
    the full compound.
    compound: The 'compound' named tuple created in hyphenation_answer.

    Returns:
    results: A named tuple with four named fields:
        1. answer_ready: A boolean. False means that the user needs to provide more 
        information on the compound's use. 
        2. outcome: The information that will be displayed to the user.
        3. outcome_type:  A variable that tells the _compounds template how to display that
        information.
        4. header: A summary of that information or, if answer_ready is False, an empty string.
    """
    Results = namedtuple('Results', ['answer_ready', 'outcome', 'outcome_type', 'header'])
    answer_ready, outcome = False, False
    outcome_type, header = None, None

    answer_ready, ele_outcome = grammar.check_first_element_lists(compound)
    if answer_ready:
        outcome = ele_outcome
        outcome_type = "standard"
        header = '''According to Chicago Manual of Style hyphenation standards, 
        your compound should be handled as follows:'''
    else:
        response_type = validate_response(mw_response)
        if response_type == "valid":
            all_forms = {
                compound.full: "hyphenated compound",
                compound.open: "open compound",
                compound.closed: "closed compound"
                }

            existing_compounds = []
            for k in all_forms.keys():
                mw_entries = start_parsing(mw_response, k, comp_in_mw=True)
                if mw_entries:
                    existing_compounds.append(existing_compound_handler.sort_entries
                    (mw_entries, compound))

            outcome = existing_compounds
            compound_types = []

            if existing_compounds:
                for comp in existing_compounds:
                    if comp.with_article not in compound_types:
                        compound_types.append(comp.with_article)

                header = ExistingCompound.format_outcome_header(compound_types, compound)
                answer_ready = True
                outcome_type = "found_in_MW"

    if not answer_ready:
        answer_ready, outcome, outcome_type, header = handle_separately(compound)

    results = Results(answer_ready, outcome, outcome_type, header)
    Nonstandard.grouped = {}

    return results

def validate_response(mw_response):
    """Check for empty responses and responses that contain only spelling suggestions.

    When a word isn't in the dictionary but there are other similar words in the dictionary,
    the API returns a list of those words (a list of strings). If there are no similar words,
    it returns an empty list.

    Argument:
    mw_response: The API's JSON response.

    Returns:
    response_type: A variable set to either "empty," "typo," or "valid." "Typo" means
    that the search term is misspelled, but the API returned a list of spelling suggestions.
    "Empty" means that the term is misspelled, and no spelling suggestions were returned.
    """
    if len(mw_response) == 0:
        response_type = "empty"
    else:
        typo_in_input = all(isinstance(entry, str) for entry in mw_response)
        if typo_in_input:
            response_type = "typo"
        else:
            response_type = "valid"

    return response_type

def handle_separately(compound):
    """Handle compounds that are not in the dictionary.
    
    Call the call_mw_api function with each element of the compound. If the compound is valid,
    make two calls to start_parsing, one for each element and the associated API response.
    
    Argument:
    compound: The 'compound' named tuple created in hyphenation_answer.

    Returns:
    answer_ready, outcome, outcome_type, header: The fields that form the named tuple 
    created in compound_checker. See the compound_checker docstring for more info.
    """
    mw_responses = [call_mw_api(element) for element in compound.elements]
    response_types = [validate_response(i) for i in mw_responses]
    outcome_type, header = None, None

    if all(response_type == "valid" for response_type in response_types):
        compound_and_responses = dict(zip(compound.elements, mw_responses))
        mw_entries = [start_parsing(v, k) for k, v in compound_and_responses.items()]
        answer_ready = False
        outcome = mw_entries
    else:
        answer_ready = True
        outcome_type = "typo"
        outcome, header = handle_invalid_entries(mw_responses, compound, response_types)

    return answer_ready, outcome, outcome_type, header

def handle_invalid_entries(mw_responses, compound, response_types):
    """Prepare the info that is returned to the user when the compound includes a typo.
    
    Arguments:
    mw_responses: The API's responses (for both elements of the compound).
    compound: The 'compound' named tuple created in hyphenation_answer.
    response_types: A list of variables set to either "typo," "valid," or "empty."

    Returns:
    outcome: The information that will be displayed to the user.
    header: A summary of that information or, in some cases, an empty string.
    """
    if all(response_type == "typo" for response_type in response_types):
        header = f'''Both elements of the compound you entered, '{compound.full},' 
        are misspelled. However, the dictionary returned spelling suggestions 
        for both elements. Please review the suggestions and enter another compound.'''
        outcome = f'''Spelling suggestions for the first element, '{compound.elements[0]},' 
        are as follows: {mw_responses[0]}. Spelling suggestions for the second element, 
        '{compound.elements[1]},' are as follows: {mw_responses[1]}.'''

    elif all(response_type == "empty" for response_type in response_types):
        header = " "
        outcome = f'''Both parts of the compound you entered, '{compound.full},' 
        are misspelled, and the dictionary did not return any alternative spellings.
        Please check the spelling of your compound and enter it again.'''

    else:
        header = f'''At least one element of the compound you entered,
        '{compound.full}', appears to be misspelled.'''
        outcomes = []
        both = {0: response_types[0], 1: response_types[1]}
        for index, response_type in both.items():
            if response_type == "typo":
                outcomes.append(f'''The dictionary returned the following spelling 
                suggestions for '{compound.elements[index]}', which is misspelled: 
                {mw_responses[index]}.''')
                
            if response_type == "empty":
                outcomes.append(f'''The dictionary did not return any spelling suggestions 
                for '{compound.elements[index]}', which is misspelled.''')

        outcome = " ".join(outcomes).strip("'[]")

    return outcome, header

def start_parsing(mw_response, search_term, comp_in_mw=False): 
    """Parse the API responses and pass each entry in the responses to the appropriate 
    function.
    
    Arguments:
    mw_response: The API's JSON response.
    search_term: The search term used in the API call (an element of the compound).
    comp_in_mw: A boolean value. False means that the compound is an existing compound (one
    that is in the dictionary) and that the information that will be displayed to the user
    does not need to be formatted.
    
    Returns:
    mw_entries: A list of StandardEntry and Nonstandard class instances--i.e., 
    entry information that will be returned to the user.
    """
    mw_entries = []
    
    for entry in mw_response:
        the_id = entry_parser.get_entry_id(entry)
        part = entry.get("fl")

        if the_id == search_term or the_id == search_term.capitalize():
            if part is None:
                cxl = entry.get("cxs")[0]["cxl"]
                cxt = entry.get("cxs")[0]["cxtis"][0]["cxt"]
                cxt_search_term, cxt_only = entry_parser.get_cxt_search_term(cxt)
                print("\n", cxt_search_term)
                cxs_mw_response = call_mw_api(cxt_search_term)
                entry_parser.cognate_cross_reference(the_id, cxs_mw_response, mw_entries, cxt_only, cxl)            
            else:
                if part in IGNORED_PARTS_OF_SPEECH:
                    continue

                cxs = entry.get("cxs")
                if cxs is None:
                    entry_parser.standard_main_entry(the_id, entry, mw_entries, part)
                else:
                    entry_parser.main_entry_with_cxs(the_id, entry, mw_entries, part)
        else: 
            existing_entry = False
            for k,v in StandardEntry.stems_and_parts.items():
                if k == part and the_id in v:
                    existing_entry = True
            ###Avoid retrieving prefix entries if the entry ID != the search term
            if not existing_entry and part != "prefix":
                entry_parser.var_inf_or_stem(the_id, search_term, entry, mw_entries, part)

    if not comp_in_mw:
        if len(mw_entries) == 0:
            mw_entries.append(NoEntries(search_term))
        else:
            prep_entries_for_display(mw_entries)

    return mw_entries

def prep_entries_for_display(mw_entries):
    '''Check the collected entries' types and pass them to the appropriate formatting functions.
    
    Argument:

    mw_entries: A list of StandardEntry and Nonstandard class instances--i.e., 
    entry information that will be returned to the user.
    '''
    to_format = [entry for entry in mw_entries if entry.entry_type != "one_diff_cxts"]
    [entry.format_entry_defs() for entry in to_format]

    Nonstandard.cxt_entry_combiner(mw_entries)
    for i in mw_entries:
        if i.entry_type != "main_entry":
            i.format_entry_header()
