import streamlit as st
from unstructured.partition.pdf import partition_pdf
import openai
import google.generativeai as palm
import os
from dotenv import load_dotenv
from generate import generate
from classify import classify
from classes import categories, sub_categories


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
palm.configure(api_key=os.getenv("PALM_KEY"))

st.title('Instructor-Feedback-GPT')
st.markdown("## Hi Instructor, let me summarise your feedback for you 🎈")

file = st.file_uploader('Upload your feedback!')
if file:
    with open(os.path.join("./uploads/", file.name),"wb") as f:
        f.write(file.getbuffer())
        st.success("Saved File")
    
    processed = partition_pdf(f'./uploads/{file.name}')

    is_qualitative = False

    qualitative = []

    for line in processed:
        text = str(line)
        if text == 'STANDARD OPEN-ENDED QUESTIONS' or text == 'Interpreting IASystem Course Summary Reports':
            is_qualitative = not is_qualitative
            continue
        if text.startswith('©') or text.startswith('Printed'):
            continue
        if is_qualitative and text[0].isdigit():
            qualitative.append(text[3:])
    
    st.success("Extracted Qualitative Feedback")

    # Classifying qualitative feedback into ken's sub-categories
    ken_format = classify(qualitative, sub_categories)

    st.success("Sub-categorised Qualitative Feedback")

    # Classifying qualitative feedback into respective codes
    categories.append('None')

    for sub_category in ken_format:
        ken_format[sub_category] = classify(ken_format[sub_category], categories)
        if ken_format[sub_category].get(categories[-1]) is not None: del ken_format[sub_category][categories[-1]]
 
    ken_format = {s:dict(filter(lambda item: item[1], ken_format[s].items())) for s in ken_format}

    st.success("Coded Qualitative Feedback")

    response = generate(ken_format)

    st.write(response)