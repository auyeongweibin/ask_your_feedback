import streamlit as st
import os
from utils.classify import classify
from classes import categories
from utils.generate import generate
from utils.extract import extract


st.title('Summary V2')
st.markdown("## Hi Instructor, let me summarise your feedback for you 🎈")

file = st.file_uploader('Upload your feedback!')
if file:
    with open(os.path.join("./uploads/", file.name),"wb") as f:
        f.write(file.getbuffer())
    
    qualitative, school = extract(file.name)

    qualitative = list(filter(lambda x: x.lower() not in ['nil', 'none', 'na', ''], qualitative))

    st.success("Extracted Qualitative Feedback")

    if len(qualitative) == 0:
        st.error('No Qualitative Feedback Found')
    else:
        coded = classify(qualitative, categories)
        st.success("Coded Qualitative Feedback")
        
        # TODO: Add cards on top

        for code in coded:
            st.markdown(f'#### {code}')

            prompt = f'''
            Using the data in parenthesis, generate a summary of the feedback. Rephrase any negative feedback or comments in a positive and constructive manner

            ({coded[code]})
            '''

            summarised = generate(prompt, 'gpt-3.5-turbo')

            st.write(summarised)

            with st.expander("See Actual Feedback"):
                for feedback in coded[code]:
                    st.markdown("- " + feedback)