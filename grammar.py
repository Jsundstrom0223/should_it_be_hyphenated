
def check_by_word(split_compound_from_input):
    # print(num2words(5, to='ordinal'), "___________________")
    outcome = None
    adverbs = ["more", "most", "less", "least", "very"]
    if split_compound_from_input[0].isnumeric():
        if split_compound_from_input[1].isnumeric():
            outcome = f"The input you entered, {'-'.join(split_compound_from_input)} appears to be a simple fraction. CMoS recommends spelling out simple fractions and states that they should generally be hyphenated unless the second number is hyphenated (e.g., 'one twenty-fifth')."
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
    
            final_outcome = "When a verb-noun pair forms a compound, it is generally closed up (e.g., 'pick' + 'pocket' = 'pickpocket') and listed in Merriam-Webster's Collegiate® Dictionary as such; because the verb-noun pair you entered is not in that dictionary, it should likely be left open."
        elif item[1] == "adverb" or item[1] == "preposition":
            final_outcome = "Since Merriam-Webster's Collegiate® Dictionary does not list the term you entered as a compound, it should likely be left open. There may be edge cases not included in the dictionary, though, so read on for a quick word on the treatement of verb-adverb and verb-preposition pairs.\n A verb followed by a preposition or adverb can be hyphenated, left open, or closed up; it all depends on how the pair of words is functioning.Pairs that are used as verbs (i.e., phrasal verbs) are not hyphenated, although their noun or adjectival equivalents can be hyphenated or closed up. For example, take 'break down.' As a phrasal verb--'I'm worried that my car will break down'--there's no hyphen. As a noun, the term is closed up ('There was a breakdown in negotiations.') \n Note tooIf the second word in the pair is a two-letter particle like 'by', 'in', or 'up', a hyphen is likely appropriate."
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
