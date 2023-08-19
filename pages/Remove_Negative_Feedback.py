import streamlit as st
import os
from utils.extract import extract_with_questions
from utils.format_word_doc import format_word_doc
from transformers import pipeline

st.title('Remove Negative Feedback')
st.markdown("## Hi Instructor, let me process your feedback for you 🎈")

file = st.file_uploader('Upload your feedback!')
if file:
    with open(os.path.join("./uploads/", file.name),"wb") as f:
        f.write(file.getbuffer())
        st.success("Saved File")
    
    qualitative, school = extract_with_questions(file.name)

    questions = list(filter(lambda x: len(x) and not x[0].isdigit(), qualitative))
    
    if len(questions) == 0:
        st.write('No Qualitative Feedback Found')
    else:
        # TODO: Original w/o negative feedback
        pipe = pipeline("text-classification", model="siebert/sentiment-roberta-large-english")
        result = pipe(qualitative)
        tag = [{'feedback':qualitative[i], 'label':result[i]['label']} for i in range(len(qualitative))]
        negative_feedback = [feedback['feedback'] for feedback in list(filter(lambda x: x['label']=='NEGATIVE', tag))]

        qualitative_without_negative = []

        for q in qualitative:
            if q in questions:
                qualitative_without_negative.append(q)
            elif q not in negative_feedback:
                qualitative_without_negative.append(q)

        filename = os.path.join("./processed_pdfs/", file.name.replace('.pdf', '_No_Negative.docx'))
        format_word_doc(qualitative_without_negative, school, filename, 'Original w/o Negative')
        with open(filename,"rb") as f:
            st.download_button(
                label='Download Original without Negative',
                data=f,
                file_name=filename
            )