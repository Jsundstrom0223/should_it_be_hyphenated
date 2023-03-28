

class Compound():
    def __init__(self, elements, full):
        self.elements = elements
        self.full = full
        self.open = self.elements[0] + " " + self.elements[1]
        self.closed = self.elements[0] + self.elements[1]

class CmosAnswerReady():
    def __init(self, outcome, outcome_type):
        self.outcome = outcome
        self.outcome_type = outcome_type

class ExistingCompound():
    outcomes = []
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
 
        outcome_header = f"M-W lists '{compound.full}' as {final_types}. Details are provided below."  
        return outcome_header

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

    def format_displayed_header(self):    
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

class Number():
    def __init__(self, numeral, spelled_out, idx_and_type):
        self.numeral = numeral
        self.spelled_out = spelled_out
        self.idx_and_type = idx_and_type
        self.part_type = "number"
        self.to_display = f'''The first term in your compound is {self.numeral}. There's no need
        to provide information on its use.'''