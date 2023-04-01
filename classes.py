
import re
from collections import defaultdict

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

class ExistingCompound():
    c_types = []
    def __init__(self, outcome, outcome_type):
        self.outcome = outcome
        self.outcome_type = outcome_type
    
        for k,v in self.outcome.items():
            if k == "open compound":
                article = "an"
            else:
                article = "a"
            with_article = article + " " + k
        
            self.displayed_outcome = v
            self.compound_type = k.capitalize()
            if with_article not in ExistingCompound.c_types:
                ExistingCompound.c_types.append(with_article)
     
    def format_compound_header(compound):
        if len(ExistingCompound.c_types) == 2:
            final_types = " and ".join(ExistingCompound.c_types)
        elif len(ExistingCompound.c_types) > 2:
            ExistingCompound.c_types.insert(-1, "and ")
            final_types = ", ".join(ExistingCompound.c_types)
        else:
            final_types = ExistingCompound.c_types[0]
 
        header = f"M-W lists '{compound.full}' as {final_types}. Details are provided below."  
        return header

class StandardEntry():
    stems_and_parts = {}
    def __init__(self, the_id, part_type, part, definition):
        self.the_id = the_id
        self.part_type = part_type
        self.part = part
        self.definition = definition 
        
        if self.part_type == "main_entry":
            self.to_display = part.capitalize()
            self.menu_option = part

    def format_entries(entry):
        for k, v in entry.definition.items():
            if v.startswith("—"):
                v_without_leading_dash = re.sub(r"^—", "", v)
                entry.definition[k] = v_without_leading_dash.capitalize()
            else:
                entry.definition[k] = v.capitalize()

class Nonstandard(StandardEntry):
    grouped = {}
    def __init__(self, the_id, part_type, part, definition, cxt, cr_type):
        self.cxt = cxt
        self.cr_type = cr_type
        Nonstandard.grouped[cr_type] = self
      
        if self.cr_type == "participle of":
            self.menu_option = "participle" 
        elif self.cr_type == "inflection (conjugated form) of":
            self.menu_option = "inflection (conjugated form)"
        elif self.cr_type == "superlative of":
            self.menu_option = "superlative"
        else:
            self.menu_option = part

        self.to_display = None
        
        super().__init__(the_id, part_type, part, definition)

    def format_entry_header(self):    
        if self.part_type == "variant_or_cxs":
            to_display = f"{self.part.capitalize()}: {self.cr_type.capitalize()} {self.cxt}"
        
        if self.part_type == "one_of_diff_parts":
            to_display = f"{self.part.capitalize()}: {self.cr_type.capitalize()} {self.cxt}"
        
        if self.part_type == "one_diff_cxts":
            header_components = [] 
            header_components.append(self.cr_type)
            header_components.append(self.cxt) 
            to_display = f"{self.part.capitalize()}: {' '.join(header_components)}"

        return to_display

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
            StandardEntry.format_entries(keep)
            keep.to_display = Nonstandard.format_entry_header(keep)
    
        for item in discard:
            to_discard = relevant_entries.index(item)
            relevant_entries.pop(to_discard)
    
class Number():
    def __init__(self, numeral, idx_and_type):
        self.numeral = numeral
        self.idx_and_type = idx_and_type
        self.part_type = "number"
        self.to_display = f'''The first term in your compound is {self.numeral}. There's no need
        to provide information on its use.'''
