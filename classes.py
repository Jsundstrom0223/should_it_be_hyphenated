###IF ITS A PARTCIPLE MENU OPTION NEEDS TP BE PARTICIPLE
class StandardEntry():
    g = []
    def __init__(self, the_id, part_type, part, definition):
        self.the_id = the_id
        self.part_type = part_type
        self.part = part
        self.definition = definition
        
        if self.part_type == "main_entry":
            self.to_display = part.capitalize()
            self.menu_option = part
        print("\n\nSTANDARD", definition)

class Nonstandard(StandardEntry):
    def __init__(self, the_id, part_type, part, definition, crt, cr_type):
        self.crt = crt
        self.cr_type = cr_type
        if self.cr_type == "participle of" or self.cr_type == "inflection (conjugated form) of":
            self.menu_option = self.cr_type
        else:
            self.menu_option = part

        if part_type == "variant_diff_crts":
            self.to_display = Nonstandard.format_displayed_header(self)
        
        if part_type == "cxs_entry" or part_type == "variant":
            to_display = f"{part.capitalize()}: {self.cr_type.capitalize()} {self.crt}"
            self.to_display = to_display 
            
            print("NONSTANDARD DISPLAY", self.to_display, part)

        if part_type == "one_of_diff_parts":
            to_display = f"{part.capitalize()}: {self.cr_type.capitalize()} {self.crt}"
            self.to_display = to_display 
            print("NONSTANDARD DISPLAY", self.to_display)
   
        print(f"\nNONSTANDARD. DEF {definition}. CRT {self.crt}. CR TYPE {cr_type} MENU {self.menu_option}\n")
        super().__init__(the_id, part_type, part, definition)

    def format_displayed_header(self):
        header_components = []
        
        header_components.append(self.cr_type)
        # if len(self.crt) == 2:
        #     targets = " and ".join(self.crt)
        # elif len(self.crt) > 2:
        #     self.crt.insert(-1, "and ")
        #     targets = ", ".join(self.crt)
        # else:
            # targets = self.crt

        header_components.append(self.crt) 
        to_display = " ".join(header_components)

        return to_display

# class GroupedVariants():
#     def __init__(self, part_type, part, definition, crt, cr_type):
        
#         self.crt = crt
#         self.cr_type = cr_type
#         print("GROUPED\n\n\n", self.part)
        
#         self.to_display = Nonstandard.format_displayed_header(self)
#         if self.cr_type == "participle of" or self.cr_type == "inflection (conjugated form) of":
#             self.menu_option = self.cr_type
#         else:
#             self.menu_option = part
        
    
#         # for k,v in self.type_and_targets.items():
#         #     header_components.append(k) 
#         #     if len(v) == 2:
#         #         targets = " and ".join(v)
#         #     elif len(v) > 2:
#         #         v.insert(-1, "and ")
#         #         targets = ", ".join(v)
#         #     else:
#         #         targets = v

#         #     header_components.append(targets)   
        
#     super().__init__(part_type, part, definition)

#     def get_menu_option(self, option):
#         for k,v in self.type_and_targets.items():
#             if k == "participle of" or k == "inflection (conjugated form) of":
#                 menu_option = k
#             else:
#                 menu_option = option.get('part')

#         return menu_option
