import streamlit as st
import os
from utils.generate import generate
from utils.extract import extract
from transformers import pipeline

st.title('Negative Feedback (In Progress)')
st.markdown("## Hi Instructor, let me make your feedback less negative for you 🎈")

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
        # Identify negative feedback
        pipe = pipeline("text-classification", model="siebert/sentiment-roberta-large-english")
        result = pipe(qualitative)
        tag = [{'feedback':qualitative[i], 'label':result[i]['label']} for i in range(len(qualitative))]
        negative_feedback = [feedback['feedback'] for feedback in list(filter(lambda x: x['label']=='NEGATIVE', tag))]
        st.success('Identified Negative Feedback')
        if len(negative_feedback) == 0:
            st.write('No Negative Feedback Found')
        else:
            # Rephrase negative feedback in a positive manner
            prompt = f'''
                Rephrase the data in parenthesis into a more positive and constructive manner
                ({negative_feedback})

                Structure the output in a table with the original feedback in 1 column and the rephrased feedback in another
            '''

            response = generate(prompt, 'openai' if school == 'SMU' else 'bard')
            st.markdown('#### Rephrase Negative Feedback')
            st.write(response)