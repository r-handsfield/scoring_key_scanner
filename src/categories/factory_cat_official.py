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


def generate_questions(numQ):
    """
    Generates a string of valid json representing categories within an ACT section.
    
    Inputs
    ------
        int : numQ
            the number of questions in the section
        
    Returns
    -------
        str : a string of valid json

    Examples
    --------
        {
            "1": { "strat":[], "cat":[], "pres":[] },
            "2": { "strat":[], "cat":[], "pres":[] }
        }
    """
    m = chr(32)*8 + '"q":{\n'
    for i in range(1,numQ):
        if i < 10:
            m += ' '
        m += chr(32)*13 + f'"{i}":' + ' { "strat":[], "cat":[""], "pres":[] },\n'

    m += chr(32)*13 + f'"{numQ}":' + ' { "strat":[], "cat":[""], "pres":[] }\n'
    m += chr(32)*12 + '}\n'

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
        m += chr(32)*8 + '"passage-breaks":["1", "16", "31", "46", "61"],\n\n'

    elif sid == 'r':
        m += chr(32)*8 + '"passages":{\n'
        m += chr(32)*21 + '"1":[""],\n'
        m += chr(32)*21 + '"2":[""],\n'
        m += chr(32)*21 + '"3":[""],\n'
        m += chr(32)*21 + '"4":[""]\n'
        m += chr(32)*19 + '},\n\n'
        m += chr(32)*8 + '"passage-breaks":["1", "11", "21", "31"],\n\n'

    elif sid == 's':
        m += chr(32)*8 + '"passages":{\n'
        m += chr(32)*21 + '"1":["", ""],\n'
        m += chr(32)*21 + '"2":["", ""],\n'
        m += chr(32)*21 + '"3":["", ""],\n'
        m += chr(32)*21 + '"4":["", ""],\n'
        m += chr(32)*21 + '"5":["", ""],\n'
        m += chr(32)*21 + '"6":["", ""]\n'
        m += chr(32)*19 + '},\n\n'
        m += chr(32)*8 + '"passage-breaks":["", "", "", "", "", ""],\n\n'


    m += generate_questions(numQ)

    m += chr(32)*6 + '}'

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

