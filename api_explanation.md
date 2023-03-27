# A Note on Merriam-Webster's Collegiate® Dictionary with Audio API
Should It Be Hyphenated? relies on Merriam-Webster's Collegiate® Dictionary with Audio API.  
When a user enters a compound, the app first attempts to retrieve the compound's definitions  
from the dictionary, via a call to the API. If the dictionary does not include the compound  
and there are no directly applicable Chicago Manual of Style standards, the app splits the  
compound into two and sends two new requests to the API (one for each element of the  
compound). It then provides each element's definitions to the user and asks the user to pick  
the relevant definition (e.g., whether the user intends for "well" to be an adverb or a noun).  
Finally, the app returns an answer to the user's hyphenation question.

This documentation provides general information on the JSON responses returned by the API  
as well as the app's use and parsing of those responses. For more specific information on  
the app's handling of those responses, see the docstrings in the source code. 

## The API's JSON Responses  

### Responses to Queries with Valid Search Terms  
Every query sent by the app to Merriam-Webster's Collegiate® Dictionary with Audio API  
includes a search term. If the search term is valid (i.e., is not misspelled and is defined    
in Merriam-Webster's Collegiate® Dictionary), the API will return a JSON response that  
includes all entries for the word. The word being defined in an entry is known as the  
"headword," and responses that include more than one entry are organized by  
"homographs"--that is, "headwords with identical spellings but distinct meanings and  
origins." Most entries include one functional label identifying the headword's part of  
speech, though some entries lack such a label (more on that below).

#### Entry Metadata  
Every entry begins with metadata. This metadata includes the entry's headword and any stems.  
According to the [API documentation](https://dictionaryapi.com/products/json#sec-2.meta), a headword's stems can comprise the following:

- Variants, or alternative spellings or stylings (e.g., a British spelling or less common  
spelling)
- Inflections, which are other forms of the headword (e.g., the plural form of a noun or the  
forms of a verb) 
- Undefined entry words, which are words "derived from or related to" the headword

The API's JSON response may also include entries for the headword's stems. For example, the  
response for the search term "well" includes five entries for "well," along with entries for  
"best" and "better" (the superlative and comparative forms of "well") and "well-adjusted,"  
"well-advised," and "well-appointed" (compounds derived from "well").

If the search term is itself a variant, inflection, or stem of another word, the headword may  
be that other word rather than the search term. [LINK TO ADAPTOR TEXT]

#### Cognate Cross-References  
If the headword of an entry is "a less common spelling of another word with the same meaning,"  
the actual content of the entry will include a cognate cross-reference (`cxs`) field and, in  
most cases, a cross-reference label (`cxl`) field. The `cxl` field indicates the headword's   
relationship to that other word (the cross-reference target, or CXT), and the `cxt` field  
identifies that other word. For example, the sole entry for "flavour" identifies the word as  
a "chiefly British spelling of" the CXT "flavor."  

Many entries with a `cxs` field lack a functional label field. Note, though, that an entry's  
`cxl` field may be indicative of the headword's part of speech. This is the case with one of the  
entries for the word "lit," the `cxl` field of which identifies "lit" as the "past tense and past  
participle of" the CXT "light."

#### Definitions and "Shortdefs"  
A single entry for a headword can contain many definitions. These definitions are contained in  
`sense` fields, each of which can also include subsenses. For example, the entry for the   
adverb form of "well" includes fifteen senses, several of which have subsenses. However, many  
entries returned by the API include an ["abridged version of the main definition section"](https://dictionaryapi.com/products/json#sec-2.shortdef)--the  
definitions for only the first three senses--in a `shortdef` array.

To avoid providing an overwhelming amount of information to the user, the app returns "shortdefs"   
rather than full definition sections whenever possible.

**Definitions in CXS Entries**  
Some entries with a `cxs` field include both a functional label and a definition of the headword.  
For example, the entry for "baloney" (a less common spelling of "bologna") has a `cxs` field as  
well as a definition and functional label. Others, like the entry for "flavour," do not include   
a definition; instead, the headword is defined only in the entry for the CXT, which means that  
the app must send another API request with the CXT as the search term. 

### Responses to Queries with Invalid Search Terms  
If the search term sent to Merriam-Webster's Collegiate® Dictionary with Audio API is not in  
the dictionary, the API will return a list of spelling suggestions or an empty list rather  
than a full JSON response. In those cases, the app will return an error message to the user;  
if spelling suggestions are available, it will return those too. 

## The Impact on Should It Be Hyphenated?  

### Parsing the JSON  
The `parse_response` function parses the JSON returned by the API and sorts all relevant  
entries into four entry types, each of which has a corresponding function. Those functions,  
described below, further parse the entries and prepare the entry information that will be  
shown to the user. 

1. `cognate_cross_reference`  
    The `cognate_cross_reference` function handles entries that have a `cxs` field  
    (e.g., "chiefly British spelling of") instead of a functional label (part of speech)  
    field. It sends a new request to the API to retrieve the CXT's definition and part  
    of speech. If the entry's `cxs` field indicates that the headword is a form of a verb  
    (e.g., "past tense and past participle of"), the `cognate_cross_reference`  
    function retrieves only the definition of the CXT as a verb.

    The user receives the following information about a "CXS entry":  
    -The CXT itself and the headword's relationship to the CXT (or an abbreviated  
    version of that relationship)  
    -The CXT's part of speech  
    -The CXT's definition  

    **Example (search term: "lit")**  
    Verb: participle of light  
    To become light : brighten —usually used with up; to take fire; to ignite something  
    (such as a cigarette) —often used with up  

2. `standard_main_entry`  
    The `standard_main_entry` function handles standard entries that have their own  
    functional label and definition and do not have a `cxs` field. 

    The user receives the following information about a "standard main entry":  
    -The headword's definition and part of speech  

    **Example (search term: "well")**  
    Adverb  
    In a good or proper manner : justly, rightly; satisfactorily with respect to  
    conduct or action; in a kindly or friendly manner  

3. `main_entry_with_cxs`  
    The `main_entry_with_cxs` function handles standard entries that have their own  
    functional label and definition in addition to a `cxs` field. 

    The user receives the following information about a "main entry with CXS":  
    -The CXT itself and the headword's relationship to the CXT (or an abbreviated  
    version of that relationship)  
    -The headword's part of speech and definition  

    **Example (search term: "baloney")**  
    Noun: less common spelling of bologna  
    A large smoked sausage of beef, veal, and pork; also : a sausage made (as of  
    turkey) to resemble bologna  

4. `variant_inflection_or_stem`  
    The `variant_inflection_or_stem` function begins the process of parsing entries  
    in which the headword *is not the search term*--that is, cases in which the  
    search term is a variant, inflection, or stem of another word. It checks an entry  
    for variant (`vrs`), inflection (`ins`), and stem (`stems`) fields, in that order. 

    If the entry includes one of those fields, `variant_inflection_or_stem` passes the  
    entry to the `is_variant`, `is_inflection`, or `is_stem` function, which returns a  
    boolean value indicating whether the field contains the search term. The search term  
    may not be present in the field, since some entries include definitions of terms   
    related to the search term. If the search term is not included in an entry's `vrs`,  
    `ins`, or `stems` field, the app will not return any information on that entry to   
    the user. (Recall that the API returns entries for "well-adjusted," "well-advised,"  
    and "well-appointed" alongside entries for "well." Because those entries do not list  
    "well" as a variant, inflection, or stem, the app does not return information on  
    those entries to the user.)

    Otherwise, the user receives the following information about a "variant, inflection,  
    or stem" entry:  
    -The headword itself and the search term's relationship to the headword (or an  
    abbreviated version of that relationship)  
    -The headword's part of speech and definition  

    **Example (search term: "adaptor")**  
    Noun: less common spelling of adapter  
    One that adapts; a device for connecting two parts (as of different diameters) of an  
    apparatus; an attachment for adapting apparatus for uses not originally intended
