# factory_cat.py
#
# Writes a pre-formatted json category file 
#
# @TODO Change blank categories to template variables:
# {{ eC1 }},  {{ mC23 }},  etc.
#
# Each var is mC23 = "A, MDL", etc.

import argparse

ap = argparse.ArgumentParser()
ap.add_argument('--test_code', '-tc', required=True, help='An ACT test code: yyyymm')
args = ap.parse_args()

# declare whitespace globals
sp1 = chr(32)*1
sp2 = chr(32)*2
sp6 = chr(32)*6
sp8 = chr(32)*8
sp12 = chr(32)*12
sp14 = chr(32)*14
sp13 = chr(32)*13
sp19 = chr(32)*19
sp21 = chr(32)*21

def generate_questions(sid, numQ):
    """
    Generates a string of valid json representing categories within an ACT section.

    Parameters
    ----------
        char : sid
            The section ID, one of ('e', 'm', 'r', 's')

        int : numQ
            the number of questions in the section
        
    Returns
    -------
        str : a string of valid json

    Examples
    --------
        {
            "1": { "cat":[] },
            "2": { "cat":[] }
        }
    """
    m = sp8 + '"q":{\n'

    # Write first n-1 questions with trailing commas
    for i in range(1,numQ+1):
        if i < 10:
            m += sp1  # add extra whitespace for alignment
        m += sp13 + f'"{i}": {{ "cat":[{{{{ {sid}C{i} }}}}] }}'
        if i < numQ: 
            m += ',\n'
    # write final question without trailing comma
    # m += sp13 + f'"{numQ}":' + ' { "cat":[] }\n'
    m += '\n'
    m += sp12 + '}\n'

    return m

def generate_section(sid, numQ, comma=True):
    """
    Generates a string of valid json representing categories within an ACT section.
    
    Inputs
    ------
        char : sid 
            The section id (e, m, r, s)

        int : numQ 
            The number of questions in the section

        bool : comma
            Whether to add a trailing comma at the end of the string

    return: a string of valid json
    """
    m = f'  "{sid}":' + '{\n'

    if sid == 'e':
        m += sp8 + '"reporting_categories":{\n'
        m += sp12 + '"pow" : "Production of Writing",\n'
        m += sp12 + '"kla" : "Knowledge of Language",\n'
        m += sp12 + '"cse" : "Conventions of Standard English"\n'
        m += sp8 + '},\n\n'

        m += sp8 + '"passage-breaks":["1", "16", "31", "46", "61"],\n\n'

    elif sid == 'm':
        m += sp8 + '"reporting_categories":{\n'
        m += sp12 + '"phm" : "Preparing for Higher Math",\n'
        m += sp12 + '"n"   : "Number & Quantity",\n'
        m += sp12 + '"a"   : "Algebra",\n'
        m += sp12 + '"f"   : "Functions",\n'
        m += sp12 + '"g"   : "Geometry",\n'
        m += sp12 + '"s"   : "Statistics & Probability",\n'
        m += sp12 + '"ies" : "Integrating Essential Skills",\n'
        m += sp12 + '"mdl" : "Modeling"\n'
        m += sp8 + '},\n\n'

        m += sp8 + '"passage-breaks":["1", "21", "41"],\n\n'
        

    elif sid == 'r':
        m += sp8 + '"reporting_categories":{\n'
        m += sp12 + '"kid" : "Key Ideas and Details",\n'
        m += sp12 + '"cs"  : "Craft & Structure",\n'
        m += sp12 + '"iki" : "Integration of Knowledge & Ideas",\n'
        m += sp12 + '"f"   : "Fiction",\n'
        m += sp12 + '"ln"  : "Literary Narrative",\n'
        m += sp12 + '"ss"  : "Social Science",\n'
        m += sp12 + '"h"   : "Humanities",\n'
        m += sp12 + '"ns"  : "Natural Science",\n'
        m += sp12 + '"c"   : "Comparison"\n'
        m += sp8 + '},\n\n'

        m += sp8 + '"passage_categories":{\n'
        m += sp12 + '"1":["ln"],\n'
        m += sp12 + '"2":["ss"],\n'
        m += sp12 + '"3":["h"],\n'
        m += sp12 + '"4":["ns"]\n'
        m += sp8 + '},\n\n'

        m += sp8 + '"passage-breaks":["1", "11", "21", "31"],\n\n'


        
    elif sid == 's':
        m += sp8 + '"reporting_categories":{\n'
        m += sp12 + '"iod" : "Interpretation of Data",\n'
        m += sp12 + '"sin" : "Scientific Investigation",\n'
        m += sp12 + '"emi" : "Evaluation of Models, Inferences, & Experimental Results",\n'
        m += sp12 + '"se"  : "Single Experiment",\n'
        m += sp12 + '"me"  : "Multiple Experiments",\n'
        m += sp12 + '"cv"  : "Conflicting Viewpoints",\n'
        m += sp12 + '"nsc" : "Non-standard Chart"\n'
        m += sp8 + '},\n\n'

        m += sp8 + '"passage_categories":{\n'
        m += sp21 + '"1":["", ""],\n'
        m += sp21 + '"2":["", ""],\n'
        m += sp21 + '"3":["", ""],\n'
        m += sp21 + '"4":["", ""],\n'
        m += sp21 + '"5":["", ""],\n'
        m += sp21 + '"6":["", ""]\n'
        m += sp19 + '},\n\n'

        m += sp8 + '"passage-breaks":["", "", "", "", "", ""],\n\n'


    m += generate_questions(sid, numQ)

    m += sp6 + '}'

    if comma:
        m += ','
    m += '\n\n'

    return m

    

m = '{\n  "test_code":"' + args.test_code + '",\n\n' 

# english section
m += generate_section('e', 75)

# math section
m += generate_section('m', 60)

# reading section
m += generate_section('r', 40)

# science section
m += generate_section('s', 40, False)

m += '}'


outfile = f'cat_ACT_{args.test_code}.json'
with open(outfile, 'w') as f:
    print(m, file=f)

