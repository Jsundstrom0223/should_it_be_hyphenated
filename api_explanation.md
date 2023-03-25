# A Note on Merriam-Webster's Collegiate® Dictionary with Audio API

## Responses to Queries with Valid Search Terms
Every query sent to Merriam-Webster's Collegiate® Dictionary with Audio API includes a search term. If the search term is valid (i.e., not misspelled) and is defined in Merriam-Webster's Collegiate® Dictionary, the API will return a JSON response that includes all entries for the word. The word being defined in an entry is known as the "headword," and responses that include more than one entry are organized by "homographs"--that is, "headwords with identical spellings but distinct meanings and origins." Most entries include one functional label identifying the headword's part of speech, though some entries lack such a label (more on that below).

### Entry Metadata
Every entry begins with metadata. This metadata includes the entry's headword and any stems. According to the [API documentation](https://dictionaryapi.com/products/json#sec-2.meta), a headword's stems comprise the following:

    - Variants, or alternative spellings or stylings (e.g., a British spelling or less common spelling)
    - Inflections, which are other forms of the headword (e.g., the plural form of a noun or the forms of a verb) 
    - Undefined entry words, which are words "derived from or related to" the headword

The API's JSON response may also include entries for the headword's stems. For example, the response for the search term "well" includes five entries for "well," along with entries for "best" and "better" (the superlative and comparative forms of "well") and "well-adjusted," "well-advised," and "well-appointed" (compounds derived from "well").
    
If the headword is "a less common spelling of another word with the same meaning," its metadata will include a cognate cross-reference (CXS) field and, in most cases, a cross-reference label (CXL) field. The CXS field identifies that other word (the cross-reference target, or CRT), and the CXL field indicates the headword's relation to that other word. For example, the metadata of the sole entry for "flavour" identifies the word as a "chiefly British spelling of" "flavour." 

Some entries with a CXS field include a definition of the headword and a functional label. For example, the entry for "baloney" (a less common spelling of "bologna") has a CXS field but also a definition and functional label. Others, like the entry for "flavour," do not include a definition or functional label; instead, the headword is defined only in the entry for the CRT, which means that an app must send another API request with the CRT as the search term.

### Definitions and "Shortdefs"
A single entry for a headword can have many definitions. These definitions are contained in "sense" fields, each of which can also include subsenses. For example, the entry for the adverb form of "well" includes fifteen senses, several of which have subsenses. However, many entries returned by the API include an ["abridged version of the main definition section"](https://dictionaryapi.com/products/json#sec-2.shortdef)--specifically the definitions for the first three senses--in a "shortdef" array.

## Responses to Queries with Invalid Search Terms
If the search term sent to Merriam-Webster's Collegiate® Dictionary with Audio API is not in the dictionary, the API will return a list rather than a full JSON response. In some cases, the API will return spelling suggestions (as a list of strings), and in others, In other cases, it will simply return an empty list.