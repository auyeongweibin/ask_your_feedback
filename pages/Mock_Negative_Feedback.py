import streamlit as st
import os
from utils.extract import extract_with_header
from utils.generate import generate
from docx import Document


st.title('Mock Negative Feedback')
st.markdown("## Hi Instructor, let me add some negative feedback for you 🎈")

file = st.file_uploader('Upload your feedback!')
if file:
    with open(os.path.join("./uploads/", file.name),"wb") as f:
        f.write(file.getbuffer())
        st.success("Saved File")

    qualitative, school = extract_with_header(file.name)

    st.success("Extracted Qualitative Feedback")

    questions = list(filter(lambda x: len(x) and not x[0].isdigit(), qualitative))

    if len(questions) == 0:
        st.write('No Qualitative Feedback Found')
    else:
        # TODO: Add negative feedback by question
        prompt = f'''
            generate and add 2 negative responses for each questions in parenthesis and output them in the format below
            ({questions})

            ```
            1. 'first negative response to the first question'
            2. 'second negative response to the first question'
            3. 'first negative response to the second question'
            4. 'second negative response to the second question'
            5. 'first negative response to the third question'
            6. 'second negative response to the third question'
            7. 'first negative response to the fourth question'
            8. 'second negative response to the fourth question'
            ```
        '''

        result = generate(prompt, 'gpt-3.5-turbo')
        
        st.success('Generated Negative Feedback')

        st.markdown('#### Negative Feedback: ')
        st.write(result)

        result = list(filter(lambda x: x != '', result.split('\n')))

        document = Document()

        question_number = 0

        for line in qualitative:
            if line[0].isdigit():
                if school == 'SMU':
                    document.add_paragraph(line.split('\n')[1])
                elif school == 'UW':
                    document.add_paragraph(''.join(line.split('. ')[1:]))
            else:
                document.add_heading(line+'\n', level=4)
                document.add_paragraph(result[question_number][4:-1]+'\n\n'+result[question_number+1][4:-1])

                question_number += 2
        
        document.save(os.path.join("./processed_pdfs/", file.name.replace('.pdf', '.docx')))

        with open(os.path.join("./processed_pdfs/", file.name.replace('.pdf', '.docx')),"rb") as f:
            st.download_button(
                label='Download File',
                data=f,
                file_name=os.path.join("./processed_pdfs/", file.name.replace('.pdf', '.docx'))
            )

        