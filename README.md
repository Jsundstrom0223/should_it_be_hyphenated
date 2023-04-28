# Should It Be Hyphenated?

Should “ad hoc” be hyphenated?
What about “well lit”?
Is it “break-in” or “break in”?

The question of whether a compound should be hyphenated can be surprisingly tricky  to answer. Hyphenation often depends on context and part of speech; some terms, for  example, are hyphenated before but not after a noun. Others are hyphenated when used  as nouns but not as verbs. In other cases, it may be best to forgo hyphenation (or  to include it) to maintain consistency within a document. And Googling a hyphenation  question may be more confusing than helpful, because different style guides and  sources have different (and often contradictory) standards.

Should It Be Hyphenated?, created by a technical editor, aims to help answer those questions.

Should It Be Hyphenated? is a work-in-progress web application with a Python/Flask back end. The app relies on Merriam-Webster's Collegiate® Dictionary with Audio API and is [hosted on Render] (https://should-it-be-hyphenated-kmfc.onrender.com/).

## Usage 

[Enter a two-element compound](https://should-it-be-hyphenated-kmfc.onrender.com/_compounds.html) (i.e., two words, a word and a number, or two numbers). The elements of your compound should be separated by a hyphen even if you think the compound should not be hyphenated.

After you’ve entered your compound, one of two things will happen: You'll receive an explanation of whether the compound should be hyphenated, or you'll be asked a quick question about your use of the compound.  

You'll receive an answer right away in the following cases:

- The Chicago Manual of Style includes a hyphenation rule that's directly applicable to the compound you entered
- The compound is in Merriam-Webster's Collegiate® Dictionary as a hyphenated compound (e.g., "well-being"), a closed compound (e.g., "hardworking"), or an open compound (e.g., "close call")

Otherwise, Should It Be Hyphenated? will use the part of speech of each element of the compound to make its determination--and you'll need to tell it which part of speech to use. (Don't worry; it's a quick and easy process. And if you're a bit rusty on the parts of speech, you can [brush up on your grammar](https://should-it-be-hyphenated-kmfc.onrender.com/_terms) before getting started.)

**Example 1: An immediate answer**

Say that Gilligan wants to know whether "multi-threading" should be hyphenated. The term's not in the dictionary, but there is an applicable Chicago Manual of Style standard: the manual's excellent hyphenation table (section 7.89) says that compounds beginning with the prefix "multi" should generally be written as one word. As a result, Gilligan will receive an answer right away.

<img width="1426" alt="Screen Shot 2023-04-27 at 4 56 23 PM" src="https://user-images.githubusercontent.com/80280440/234989299-6315f8be-9e3e-43be-a798-18e402042b33.png">

**Example 2: First, a quick question**

Now let's say that Gilligan wants to know whether "local environment" should be hyphenated. The term's not in the dictionary, and there are no directly applicable Chicago Manual standards. Should It Be Hyphenated? will make two calls to Merriam-Webster's Collegiate® Dictionary with Audio API--one for "local" and another for "environment." Then it will return the definitions of "local" and "environment" to Gilligan. Here's what he'll see:

<img width="1426" alt="Screen Shot 2023-04-27 at 4 42 09 PM" src="https://user-images.githubusercontent.com/80280440/234990849-10d1244d-c6c7-450e-902e-7c5cfcc36727.png">

Gilligan will then pick the definition of "local" that matches his use of the term. He knows that "local" is describing "environment," so it's being used as an adjective. And since "Adjective" is the first item in the drop-down menu, he won't need to change anything; he'll just need to click Submit. And then he'll receive his answer:

<img width="1437" alt="Screen Shot 2023-04-27 at 6 14 44 PM" src="https://user-images.githubusercontent.com/80280440/235002659-8358aebe-8c11-4018-979e-d0d8d9eb74ed.png">

## Try It Out

If you're curious about Should It Be Hyphenated? but don't have any burning hyphenation questions, try it out with the following compounds:

- 10-GB
- well-done
- camel-case

## Other Documentation

For details on the JSON responses returned by the API and the app's handling of those responses, see "[The App and the API: A Note on Merriam-Webster's Collegiate® Dictionary with Audio API](https://github.com/Jsundstrom0223/should_it_be_hyphenated/blob/main/api_explanation.md)." For more extensive and general information on the API, see the Merriam-Webster Developer Center's [FAQ page](https://dictionaryapi.com/info/frequently-asked-questions) or [JSON documentation](https://dictionaryapi.com/products/json).
