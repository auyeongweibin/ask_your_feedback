import streamlit as st
import os
from utils.extract import extract
from transformers import pipeline
from pdf2docx import parse

st.title('Negative Feedback')
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

        if len(negative_feedback) < 3:
            # TODO: Convert file to word doc
            parse(f'./uploads/{file.name}', f'./uploads/{file.name.replace(".pdf", ".docx")}')


            # TODO: Add negative feedback by question


            # TODO: Convert file back to pdf and serve it as a download


        else:
            st.write('Sufficient Negative Feedback Found')


        