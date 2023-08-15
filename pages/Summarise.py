import streamlit as st
import os
from utils.generate import generate
from utils.classify import classify
from utils.extract import extract
from classes import categories, sub_categories

st.title('Summarise')
st.markdown("## Hi Instructor, let me summarise your feedback for you 🎈")

file = st.file_uploader('Upload your feedback!')
if file:
    with open(os.path.join("./uploads/", file.name),"wb") as f:
        f.write(file.getbuffer())
        st.success("Saved File")
    
    qualitative, school = extract(file.name)

    st.success("Extracted Qualitative Feedback")

    if len(qualitative) == 0:
        st.write('No Qualitative Feedback Found')
    else:
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

        prompt = f'''
            Using the data in parenthesis, fill in the template in triple backticks

            ({ken_format})

            ```
            SGID I: What is helping you learn in this course? Please explain or give examples.
                for each code/category:
                    >Code/Category
                    Either direct quotes or examples 
                    [number of groups who discussed]
                    [number of individuals; helpful/suggestion]

            SGID II: What changes could be made that would assist you in learning?
                for each code/category:
                    >Code/Category
                    Either direct quotes or examples 
                    [number of groups who discussed]
                    [number of individuals; helpful/suggestion]
            ```
        '''

        response = generate(prompt, 'openai' if school == 'SMU' else 'bard')

        st.write(response)