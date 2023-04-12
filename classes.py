
import re
from collections import defaultdict
from grammar_constants import VALID_PARTS_OF_SPEECH

class Compound():
    def __init__(self, elements, full):
        self.elements = elements
        self.full = full
        self.open = self.elements[0] + " " + self.elements[1]
        self.closed = self.elements[0] + self.elements[1]

class GrammarDef():
    def __init__(self, term, official, plain_english):
        self.term = term
        self.official = official
        self.plain_english = plain_english

class StandardEntry():
    stems_and_parts = {}
    def __init__(self, the_id, entry_type, part, definition):
        self.the_id = the_id
        self.entry_type = entry_type
        self.part = part
        self.definition = definition

        if self.entry_type == "main_entry":
            self.to_display = part.capitalize()
            self.menu_option = part

    def format_entries(self):
        for k, v in self.definition.items():
            if v.startswith("—"):
                v_without_leading_dash = re.sub(r"^—", "", v)
                self.definition[k] = v_without_leading_dash.capitalize()
            else:
                self.definition[k] = v.capitalize()

class Nonstandard(StandardEntry):
    grouped = {}
    def __init__(self, the_id, entry_type, part, definition, cxt, relation):
        self.cxt = cxt
        self.relation = relation
        if part == "verb":
            self.shorten_verb_labels()
        else:
            if self.relation == "superlative of":
                self.menu_option = "superlative"
            else:
                self.menu_option = part

        Nonstandard.grouped[relation] = self
        self.to_display = None

        super().__init__(the_id, entry_type, part, definition)

    def shorten_verb_labels(self):
        if "participle of" in self.relation:
            self.relation = "participle of"
            self.menu_option = "participle"
        else:
            if "tense" in self.relation or "conjugated form" in self.relation:
                self.relation = "inflection (conjugated form) of"
                self.menu_option = "inflection (conjugated form)"
            else:
                self.menu_option = self.part

    def format_entry_header(self):
        if self.entry_type == "variant_or_cxs":
            to_display = f"{self.part.capitalize()}: {self.relation.capitalize()} {self.cxt}"

        if self.entry_type == "one_diff_cxts":
            header_components = []
            header_components.append(self.relation)
            header_components.append(self.cxt)
            to_display = f"{self.part.capitalize()}: {' '.join(header_components)}"

        return to_display

    @staticmethod
    def cxt_entry_combiner(mw_entries):
        entries = [(i.relation, i) for i in mw_entries if i.entry_type == "one_diff_cxts"]

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
            StandardEntry.format_entries(keep)
            keep.to_display = Nonstandard.format_entry_header(keep)

        for item in discard:
            to_discard = mw_entries.index(item)
            mw_entries.pop(to_discard)

class ExistingCompound(StandardEntry):
    def __init__(self, the_id, entry_type, part, definition, outcome, outcome_type):
        self.outcome = outcome
        self.outcome_type = outcome_type
        for k,v in definition.items():
            part = k.strip("'").capitalize()
            definition = v.capitalize()

        self.outcome = outcome
        self.outcome_type = outcome_type

        if entry_type == "open compound":
            self.with_article = "an open compound"
        else:
            self.with_article = f"a {entry_type}"

        super().__init__(the_id, entry_type, part, definition)

    @staticmethod
    def format_compound_header(compound_types, compound):
        if len(compound_types) == 2:
            final_types = " and ".join(compound_types)
        elif len(compound_types) > 2:
            compound_types.insert(-1, "and ")
            final_types = ", ".join(compound_types)
        else:
            final_types = compound_types[0]

        header = f"M-W lists '{compound.full}' as {final_types}. Details are provided below."
        return header

class NoEntries():
    def __init__(self, search_term):
        self.search_term = search_term
        self.entry_type = "no_entries"
        self.to_display = f'''The app did not retrieve any definitions for one of the
        elements in your compound, '{self.search_term}'. This may mean that the element
        is a biographical name, a symbol, a trademark, an abbreviation, or a term that 
        should be written as more than two words. Unfortunately, it may also mean that 
        Should It Be Hyphenated? encountered an error. If you know the part of speech of
        the term, you can select it from the drop-down menu below. If not, please enter 
        another compound.'''
        self.menu_option = VALID_PARTS_OF_SPEECH

class Number():
    def __init__(self, numeral, idx_and_type):
        self.numeral = numeral
        self.idx_and_type = idx_and_type
        self.entry_type = "number"
        self.to_display = f'''The first term in your compound is {self.numeral}. There's no 
        need to provide information on its use.'''
