import streamlit as st
from unstructured.partition.pdf import partition_pdf
import os
from generate import generate
from transformers import pipeline

st.title('Negative Feedback')
st.markdown("## Hi Instructor, let me make your feedback less negative for you 🎈")

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
        if text == 'Interpreting IASystem Course Summary Reports':
            break
        if text == 'STANDARD OPEN-ENDED QUESTIONS':
            is_qualitative = True
            continue
        if text.startswith('©') or text.startswith('Printed'):
            continue
        if is_qualitative and text[0].isdigit():
            qualitative.append(text[3:])
    
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

            response = generate(prompt)
            st.markdown('#### Rephrase Negative Feedback')
            st.write(response)