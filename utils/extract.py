from typing import List
from unstructured.partition.pdf import partition_pdf
import streamlit as st

def extract(filename:str) -> List[str]:
        
    processed = partition_pdf(f'./uploads/{filename}')

    school = ''

    for line in processed:
        text = str(line)
        if text.startswith('Faculty FACETS Report Undergraduate'):
            school = 'SMU'
            break
        elif text.startswith('University of Washington, Seattle College of Engineering Human Centered Design & Engr.'):
            school = 'UW'
            break

    # st.success(f'Identified {school} Report')

    is_qualitative = False

    result = []

    if school == 'SMU':
        for index, line in enumerate(processed):
            text = str(line)
            if text == 'Student Comments':
                is_qualitative = not is_qualitative 
                continue
            if is_qualitative and text[:-1].isnumeric():
                result.append(str(processed[index+1]))
    
    elif school == 'UW':
        for line in processed:
            text = str(line)
            if text == 'Interpreting IASystem Course Summary Reports':
                break
            if text == 'STANDARD OPEN-ENDED QUESTIONS' or text == 'INSTRUCTOR-ADDED OPEN-ENDED QUESTIONS':
                is_qualitative = True
                continue
            if text.startswith('©') or text.startswith('Printed'):
                continue
            if is_qualitative and text[0].isdigit():
                result.append(text[3:])

    return result, school

def extract_with_questions(filename:str) -> List[str]:
        
    processed = partition_pdf(f'./uploads/{filename}')

    school = ''

    for line in processed:
        text = str(line)
        if text.startswith('Faculty FACETS Report Undergraduate'):
            school = 'SMU'
            break
        elif text.startswith('University of Washington, Seattle College of Engineering Human Centered Design & Engr.'):
            school = 'UW'
            break
        
    
    # st.success(f'Identified {school} Report')

    is_qualitative = False

    result = []

    if school == 'SMU':
        for index, line in enumerate(processed):
            text = str(line)
            if text == 'Student Comments':
                is_qualitative = True 
                continue
            if is_qualitative and text[:-1].isnumeric():
                result.append(text + '\n' + str(processed[index+1]))
            elif is_qualitative and text.startswith('Question'):
                result.append(text)
    
    elif school == 'UW':
        for line in processed:
            text = str(line)
            if text == 'Interpreting IASystem Course Summary Reports':
                break
            if text == 'STANDARD OPEN-ENDED QUESTIONS' or text == 'INSTRUCTOR-ADDED OPEN-ENDED QUESTIONS':
                is_qualitative = True
                continue
            if text.startswith('©') or text.startswith('Printed'):
                continue
            if is_qualitative:
                result.append(text)
    
    return result, school


def extract_plus_questions(filename:str) -> List[str]:
    processed = partition_pdf(f'./uploads/{filename}')

    school = ''

    for line in processed:
        text = str(line)
        if text.startswith('Faculty FACETS Report Undergraduate'):
            school = 'SMU'
            break
        elif text.startswith('University of Washington, Seattle College of Engineering Human Centered Design & Engr.'):
            school = 'UW'
            break
        
    
    # st.success(f'Identified {school} Report')

    is_qualitative = False

    result = []

    question = ""

    if school == 'SMU':
        for index, line in enumerate(processed):
            text = str(line)
            if text == 'Student Comments':
                is_qualitative = True 
                continue
            if is_qualitative and text[:-1].isnumeric():
                result.append(f"Question: {question}" + " Answer: " + str(processed[index+1]))
            elif is_qualitative and text.startswith('Question'):
                question = text.split(": ")[1][3:]
    
    elif school == 'UW':
        for line in processed:
            text = str(line)
            if text == 'Interpreting IASystem Course Summary Reports':
                break
            if text == 'STANDARD OPEN-ENDED QUESTIONS' or text == 'INSTRUCTOR-ADDED OPEN-ENDED QUESTIONS':
                is_qualitative = True
                continue
            if text.startswith('©') or text.startswith('Printed'):
                continue
            if is_qualitative:
                if text[0].isdigit():
                    if text[1].isdigit():
                        result.append(f"Question: {question}" + " Answer: " + text[4:])
                    else: 
                        result.append(f"Question: {question}" + " Answer: " + text[3:])
                else:
                    question = text
    
    return result, school