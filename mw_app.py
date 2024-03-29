
from collections import namedtuple
import urllib.request, urllib.parse, urllib.error
import json
import re
import html
from flask import Flask, request, render_template
from existing_compound_handler import parse_existing_comps, format_outcome_header
import grammar
import entry_parser
from grammar_constants import ORDINALS, PART_OF_SPEECH_DEFS, IGNORED_PARTS_OF_SPEECH
from classes import NoEntries, Nonstandard, Number, StandardEntry

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
    
    Take a user-provided compound and check its validity. If the compound is valid, create a 
    named tuple for the compound and pass it to the handle_comp_with_num or call_mw_api
    function. Then render the _compounds template again, with the results of the function call.
    
    For more details, see the following documentation on the API:
    https://github.com/Jsundstrom0223/should_it_be_hyphenated/blob/main/api_explanation.md.
    """
    if request.method == 'POST':
        if request.form.get('start_compounds') is not None:
            return render_template('_compounds.html', first_page=True)

        if request.form.get('user_compound') is not None:
            user_input = html.escape(request.form['user_compound']).lower()
            print("USER INPUT", user_input)
            #Using a regex instead of "if '-' in user_input" to catch/ignore any
            # stray characters/extra input
            hyphenated_compound = re.search(r"[\w\d]+-[\w\d]+", user_input)
            mistake_template = validate_input(hyphenated_compound, user_input)

            if mistake_template is not None:
                return mistake_template
    
            compound_from_input = user_input[hyphenated_compound.start(): hyphenated_compound.end()]
            elements_of_compound = compound_from_input.split("-")
            Compound = namedtuple('Compound', ['elements', 'full', 'open', 'closed'])
            open_compound = elements_of_compound[0] + " " + elements_of_compound[1]
            closed = "".join(elements_of_compound)
            compound = Compound(elements_of_compound, compound_from_input, open_compound, closed)

            has_numeral, idx_and_type = check_for_numerals(compound)
            if has_numeral:
                new_page = handle_comp_with_num(compound, idx_and_type)
                return new_page

            results = call_mw_api(compound, is_a_compound=True)

            #If results.answer_ready is False, the app returns the definitions of the 
            # compound's elements and asks the user to select the relevant definitions. 
            # Then it uses the associated parts of speech to determine whether the compound should be hyphenated.
            if not results.answer_ready:
                new_page = render_template('_compounds.html', initial_results=results)
            else:
                new_page = render_by_type(results)
            return new_page

        if request.form.get('part_of_speech_selections') is not None:
            selected = [request.form['part_of_speech_1'].lower(), 
                        request.form['part_of_speech_2'].lower()]
            final_outcome, final_header = grammar.cmos_rules(selected)
            final_page = render_template('_compounds.html', standard=final_outcome, header=final_header)
            return final_page

    return render_template('_compounds.html', first_page=True)

def validate_input(hyphenated_compound, user_input):
    """Validate the user input.
    
    Arguments:
    hyphenated_compound: The user-provided compound.
    user_input: The full user input (as a string).
    
    Returns: 
        None: If the compound is valid.
        mistake_page: The _compounds template, with a message explaining the input issue.
    """
    if hyphenated_compound is None:
        return handle_input_mistakes(user_input, "no_hyphen")
    
    if "-" in user_input[hyphenated_compound.end(): ]:
        return handle_input_mistakes(user_input, "multiple_hyphens")
    
    extra_punctuation = re.findall(r"[^-\w\d]", user_input)
    if len(extra_punctuation) > 0:
        return handle_input_mistakes(user_input, "extra_punctuation")
    
    compound_from_input = user_input[hyphenated_compound.start(): hyphenated_compound.end()]
    elements_of_compound = compound_from_input.split("-")
    
    if elements_of_compound[0] == elements_of_compound[1]:
        return handle_input_mistakes(user_input, "dupe_elements")
    
    return None

def handle_input_mistakes(user_input, mistake_type):
    """Return the message that will be displayed if the user input is invalid.
    
    Arguments:
    user_input: The full user input (as a string).
    mistake_type: A variable set to either "no_hyphen," "multiple_hyphens," 
    "extra_punctuation," or "dupe_elements."
    
    Returns:
    mistake_page: The _compounds template, with a message explaining the input issue.
    """
    if mistake_type == "no_hyphen":
        mistake_header = '''The input you provided lacks a hyphen ("-") or
            includes a hyphen with at least one space next to it. Please try again
            and ensure that your input includes one hyphen with no spaces around it
            (e.g., "well-being").'''
        
    if mistake_type == "multiple_hyphens":
        mistake_header = '''The input you provided includes multiple hyphens.
            Please enter a compound that has only one hyphen (e.g., "well-being").'''
        
    if mistake_type == "extra_punctuation":
        mistake_header = '''The input you provided includes at least one punctuation mark
        other than a hyphen. Please enter a compound that has no punctuation marks other 
        than a hyphen. (If you entered a number with a comma in it, remove the comma.)'''
        
    if mistake_type == "dupe_elements":
        mistake_header = '''The elements of your compound are identical; please 
        enter a compound with two unique elements.'''

    mistake_args = {'input': user_input, 'mistake': mistake_header, 'first_page': True}
    mistake_page = render_template('_compounds.html', **mistake_args)

    return mistake_page

def render_by_type(results):
    """Pass the results returned by handle_comp_with_num or call_mw_api to render_template.

    Create a dictionary of kwargs and pass them to Flask's render_template function. 

    Argument:
    results: A named tuple with four named fields. Holds the information that will be
    displayed to the user and tells the _compounds template what kind of information
    to display.

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
    compound: A named tuple with four named fields. Holds information about the
    user-provided compound and open and closed versions of it.

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
    compound: A named tuple with four named fields. Holds information about the
    user-provided compound and open and closed versions of it.
    idx_and_type: A dictionary that identifies the numeric element(s) of the compound.
   
    Returns:
    new_page: The _compounds template, with the results to be displayed to the user.
    """
    num_results = grammar.check_cmos_num_rules(compound, idx_and_type)

    if num_results.answer_ready:
        new_page = render_by_type(num_results)
    else:
        Results = namedtuple('Results', ['answer_ready', 'outcome', 'outcome_type', 'header'])
        for idx in idx_and_type.keys():
            num_element = Number(compound.elements[idx], idx)
          
        non_num = compound.elements[num_element.other]
        mw_response = call_mw_api(non_num)
        mw_entries = start_parsing(mw_response, non_num)

        outcome = []
        if num_element.idx == 0:
            outcome = [[num_element], mw_entries]
        else:
            outcome = [mw_entries, [num_element]]
        
        outcome_type, header = get_outcome_type_and_header(outcome, compound)
        results = Results(num_results.answer_ready, outcome, outcome_type, header)
        new_page = render_template('_compounds.html', initial_results=results)

    return new_page

def call_mw_api(term, is_a_compound=False, just_get_def=False):
    """Build and send a request to Merriam-Webster's Collegiate® Dictionary with Audio API.
    
    Arguments:
    term: The search term to be used in the API call.
    is_a_compound: A boolean value. True means that the search term is the full
    user-provided compound and that check_compound should be called.
    just_get_def: A boolean value. True means that the user (via the _terms template) has
    requested the definition of a grammar term.

    Returns:
    shortdef: The shortdef field of a dictionary entry. Returned if just_get_def is True.
    results: The named tuple returned by check_compound. Returned if is_a_compound is True. 
    mw_response: The full API response. Returned if the search term is a single element
    of the user-provided compound.
    """
    if is_a_compound:
        search_term = term.full
    else:
        search_term = term

    constructed = BASE + search_term + QUERY_STRING + "key=" + MW_KEY
    with urllib.request.urlopen(constructed) as response:
        mw_response = json.load(response)

    if just_get_def:
        shortdef = mw_response[0]['shortdef']
        return shortdef[0]

    if is_a_compound:
        return check_compound(mw_response, term)

    return mw_response

def check_compound(mw_response, compound):
    r"""Check whether the compound is in the dictionary/any CMoS rules apply to it. 

    If the compound is not in the dictionary and there are no directly applicable Chicago 
    Manual of Style standards, call handle_separately to handle the individual elements of
    the compound.
    
    Arguments:
    mw_response: The API's response to the initial call, in which the search term is 
    the full compound.
    compound: A named tuple with four named fields. Holds information about the
    user-provided compound and open and closed versions of it.
    
    Returns:
    results: A named tuple with four named fields. Holds the information that will be
    displayed to the user and tells the _compounds template what kind of information
    to display.
    """
    Results = namedtuple('Results', ['answer_ready', 'outcome', 'outcome_type', 'header'])
    answer_ready, outcome = False, False
    outcome_type, header = None, None

    answer_ready, ele_outcome = grammar.check_first_element_lists(compound)
    if answer_ready:
        header = '''According to Chicago Manual of Style hyphenation standards, 
        your compound should be handled as follows:'''
        results = Results(answer_ready, ele_outcome, "standard", header)
        return results
    
    response_type = validate_response(mw_response)
    if response_type == "valid":
        all_versions = {
            compound.full: "hyphenated compound",
            compound.open: "open compound",
            compound.closed: "closed compound"
            }

        existing_comps = []
        for version_of_comp in all_versions.keys():
            mw_entries = start_parsing(mw_response, version_of_comp, full_compound=True)
            for entry in mw_entries:
                existing_comps.append(entry)
             
        outcome = parse_existing_comps(existing_comps, compound)
        compound_types = []
        if len(outcome) > 0:
            for comp in outcome:
                if comp.with_article not in compound_types:
                    compound_types.append(comp.with_article)

            header = format_outcome_header(compound_types, compound)
            answer_ready = True
            outcome_type = "found_in_MW"

    if not answer_ready:
        answer_ready, outcome, outcome_type, header = handle_separately(compound)

    results = Results(answer_ready, outcome, outcome_type, header)
    Nonstandard.relations = {}
    
    return results

def validate_response(mw_response):
    """Check for empty responses and responses that contain only spelling suggestions.

    Argument:
    mw_response: The API's JSON response.

    Returns:
    response_type: A variable set to either "empty," "typo," or "valid." "Typo" means
    that the search term is misspelled, but the API returned a list of spelling suggestions
    (strings). "Empty" means that the term is misspelled, and no spelling suggestions were
    returned.
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
    """Handle the individual elements of the compound separately.
    
    Call the call_mw_api function with each element of the compound. If the compound is
    valid, make two calls to start_parsing, one for each element and the associated API
    response.
    
    Argument:
    compound: A named tuple with four named fields. Holds information about the
    user-provided compound and open and closed versions of it.

    Returns:
    answer_ready, outcome, outcome_type, header: The fields that form the named tuple 
    returned by check_compound.
    """
    mw_responses = [call_mw_api(element) for element in compound.elements]
    response_types = [validate_response(mw_response) for mw_response in mw_responses]
    outcome_type, header = None, None

    if all(response_type == "valid" for response_type in response_types):
        compound_and_responses = dict(zip(compound.elements, mw_responses))
        outcome = [start_parsing(v, k) for k, v in compound_and_responses.items()]
        answer_ready = False
        outcome_type, header = get_outcome_type_and_header(outcome, compound)

    else:
        answer_ready = True
        outcome_type = "typo_or_empty"
        outcome, header = handle_invalid_entries(mw_responses, compound, response_types)

    return answer_ready, outcome, outcome_type, header

def get_outcome_type_and_header(outcome, compound):
    """Check the type(s) of info being returned and generate headers summarizing that info.
    
    Check whether the user will need to provide more information on either element of the 
    compound. Also create the header that will be shown to the user.
    
    Returns:
    outcome_types: A list of variables that tell the _compounds template how to display the 
    information being returned to the user.
    headers: A list of summaries of that information (one for each element of the compound).
    """
    idx_as_ord = {0: "first", 1: "second"}
    headers = []
    outcome_types = []
    numeral_or_no_entries = ["no_entries", "number"]
    
    for entry_list_idx, entry_list in enumerate(outcome):
        if len(entry_list) == 1 and entry_list[0].entry_type in numeral_or_no_entries:
            headers.append(entry_list[0].to_display)
            outcome_types.append("no_defs_to_show")
        else:
            headers.append(f'''The {idx_as_ord[entry_list_idx]} term in your compound is
            '{compound.elements[entry_list_idx]}.' How is it being used?''')
            outcome_types.append("defs_to_show")

    return outcome_types, headers

def handle_invalid_entries(mw_responses, compound, response_types):
    """Prepare the information that is returned when the compound includes a misspelling.
    
    Arguments:
    mw_responses: The API's responses (for both elements of the compound).
    compound: A named tuple with four named fields. Holds information about the
    user-provided compound and open and closed versions of it.
    response_types: A list of variables set to either "typo," "valid," or "empty."

    Returns:
    outcome: The information that will be displayed to the user.
    header: A summary of that information or, in some cases, an empty string.
    """
    both_formatted = []
    for mw_response in mw_responses:
        formatted = str(mw_response).strip("[]")
        both_formatted.append(formatted)
   
    if all(response_type == "typo" for response_type in response_types):
        header = (f'''Both elements of the compound you entered, '{compound.full},'
        are misspelled. However, the dictionary returned spelling suggestions for both elements. Please review those suggestions and re-enter the compound.''')

        #Some parts of the _compounds template preserve whitespace. Using quotation marks at the start/end of each line prevents the displayed string from breaking at the end of each line but preserves newline characters. https://stackoverflow.com/a/3077017
        outcome = (f"Spelling suggestions for the first element, '{compound.elements[0]},'"
                   f" are as follows: {both_formatted[0]}.\n\nSpelling suggestions for the"
                   f" second element, '{compound.elements[1]},' are as follows:"
                   f" {both_formatted[1]}.")

    elif all(response_type == "empty" for response_type in response_types):
        header = " "
        outcome = (f"Both elements of the compound you entered, '{compound.full},'"
                   " are misspelled, and the dictionary did not return any alternative"
                   " spellings. Please check the spelling of your compound and enter it"
                   " again.")
        
    else:
        if not "valid" in response_types:
            header = f'''Both elements of the compound you entered, '{compound.full},'
            are misspelled.'''
        else:
            header = f'''One of the elements of the compound you entered, '{compound.full},'
            is misspelled.'''
     
        outcomes = []
        for index, response_type in enumerate(response_types):
            if response_type == "typo":
                outcomes.append("The dictionary returned the following spelling" 
                                f" suggestions for '{compound.elements[index]},'"
                                f" which is misspelled: {both_formatted[index]}.\n\n")
                
            if response_type == "empty":
                outcomes.append("The dictionary did not return any spelling"
                                f" suggestions for '{compound.elements[index]},'"
                                " which is misspelled.\n\n")

        outcome = " ".join(outcomes).strip("'[]")

    return outcome, header

def start_parsing(mw_response, search_term, full_compound=False): 
    """Parse the API response and pass each entry in the response to the appropriate 
    function.
    
    Arguments:
    mw_response: The API's JSON response.
    search_term: The search term used in the API call.
    full_compound: A boolean value. True means that the search term is a full compound, not an element of a compound, and that the app is essentially checking whether the full
    compound is in the dictionary. Necessary because information on existing compounds is displayed to the user differently.
    
    Returns:
    mw_entries: A list of StandardEntry and Nonstandard class instances--i.e., 
    entry information that will be returned to the user. Alternatively, if no 
    entries are retrieved, a list consisting of a sole NoEntries class instance.
    """
    mw_entries = []
    for entry in mw_response:
        the_id = entry_parser.get_entry_id(entry)
        part = entry.get('fl')

        if the_id == search_term or the_id == search_term.capitalize():
            cxs = entry.get('cxs')
            if part is None:
                cxt = cxs[0].get('cxtis')[0]['cxt']
                cxt_search_term, cxt_only = entry_parser.get_cxt_search_term(cxt)
                cxs_mw_response = call_mw_api(cxt_search_term)
                entry_parser.cognate_cross_reference(the_id, cxs_mw_response, mw_entries,
                                                    cxt_only, cxs)            
            else:
                if part in IGNORED_PARTS_OF_SPEECH:
                    continue
                if cxs is None:
                    entry_parser.standard_main_entry(the_id, entry, mw_entries, part)
                else:
                    entry_parser.main_entry_with_cxs(the_id, entry, mw_entries, part, cxs)
        else: 
            #A response can include entries for words related to the search term (its stems).
            #If a stem entry has the same part of speech as an entry for the search term,
            #the entry is ignored. (This basically ignores superlatives and comparatives.) 
            #Entries for prefixes are also ignored if the entry ID != the search term.
            existing_entry = False
            for part_of_speech, stems in StandardEntry.stems_and_parts.items():
                if part_of_speech == part and the_id in stems:
                    existing_entry = True
   
            if not existing_entry and part != "prefix":
                entry_parser.var_inf_or_stem(the_id, search_term, entry, mw_entries, part)

    if not full_compound:
        if len(mw_entries) == 0:
            mw_entries.append(NoEntries(search_term))
        else:
            prep_entries_for_display(mw_entries)

    return mw_entries

def prep_entries_for_display(mw_entries):
    """Check the collected entries' types and pass them to the appropriate formatting functions.
    
    Argument:
    mw_entries: A list of StandardEntry and Nonstandard class instances--i.e., 
    entry information that will be returned to the user.
    """
    for entry in mw_entries:
        if entry.entry_type != "one_diff_cxts":
            entry.format_entry_defs()

    Nonstandard.cxt_entry_combiner(mw_entries)
    for i in mw_entries:
        if i.entry_type != "main_entry":
            i.format_entry_header()
