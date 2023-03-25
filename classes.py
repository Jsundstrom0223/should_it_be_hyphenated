###IF ITS A PARTCIPLE MENU OPTION NEEDS TP BE PARTICIPLE

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
    def __init__(self, the_id, part_type, part, definition, crt, cr_type):
        self.crt = crt
        self.cr_type = cr_type
        Nonstandard.grouped[cr_type] = self
      
        
        if self.cr_type == "participle of":
            self.menu_option = "participle" 
        elif self.cr_type == "inflection (conjugated form) of":
            print("CR!! PART OR INF", self.cr_type)
            self.menu_option = "inflection (conjugated form)"
        elif self.cr_type == "superlative of":
            self.menu_option = "superlative"
        else:
            self.menu_option = part


        self.to_display = None
        
        super().__init__(the_id, part_type, part, definition)

    def format_displayed_header(self):    
        if self.part_type == "variant_or_cxs":
            to_display = f"{self.part.capitalize()}: {self.cr_type.capitalize()} {self.crt}"
        
        if self.part_type == "one_of_diff_parts":
            to_display = f"{self.part.capitalize()}: {self.cr_type.capitalize()} {self.crt}"
        
        if self.part_type == "one_diff_crts":
            header_components = [] 
            header_components.append(self.cr_type)
            header_components.append(self.crt) 
            to_display = f"{self.part.capitalize()}: {' '.join(header_components)}"

        return to_display

class Number():
    def __init__(self, numeral, spelled_out, ordinal):
        if ordinal:
            self.num_type = "ordinal"
        else:
            self.num_type = "cardinal"

        self.numeral = numeral
        self.spelled_out = spelled_out
        self.part_type = "number"
        self.to_display = f'''The first term in your compound is {self.numeral}. There's no need
        to provide information on its use.'''