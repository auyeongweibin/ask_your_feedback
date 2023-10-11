import streamlit as st
import os
from utils.classify import classify
from utils.generate import generate
from utils.extract import extract_plus_questions
from utils.nasty_filter import nasty_filter

file = st.file_uploader('Upload your feedback!')
if file:
    with open(os.path.join("./uploads/", file.name),"wb") as f:
        f.write(file.getbuffer())
    
    qualitative, school = extract_plus_questions(file.name)

    qualitative = list(filter(lambda x: x.split("Answer: ")[1].lower() not in ['nil', 'none', 'na', 'n/a', 'n.a.', ''], qualitative))

    nasty, qualitative = nasty_filter(qualitative)

    # st.success("Extracted Qualitative Feedback")

    if len(qualitative) == 0:
        st.error('No Qualitative Feedback Found')
    else:
        st.markdown('### Search By Category/Create Your Own Category')
        input_categories = st.text_input('Type in a Category. For multiple categories, please separate them with a comma')
        if input:
            input_categories.replace(', ', ',')
            input_categories=input_categories.split(',')

            coded = classify(items=qualitative, classes=input_categories, multilabel=True, threshold=0.85)

            for category in input_categories:
                st.markdown(f'#### {category}')

                if coded.get(category) is None:
                    st.write('No feedback was found in this category')
                else:
                    questions = {}

                    for feedback in coded[category]:
                        [question, answer] = feedback.split(' Answer: ')
                        question = question.split(': ')[1]
                        if questions.get(question) is None:
                            questions[question] = [answer]
                        else: questions[question].append(answer)

                    prompt = f'''
                    Using the data in parenthesis, generate a summary of the feedback. Rephrase any negative feedback or comments in a positive and constructive manner

                    ({questions})
                    '''

                    summarised = generate(prompt, 'gpt-3.5-turbo' if school=='UW' else 'gpt-3.5-turbo-16k')

                    st.write(summarised)

                    with st.expander(f"See Actual Feedback ({len(coded[category])} Comments)"):
                        for question in questions:
                            st.write('')
                            st.markdown(f'##### {question}')
                            for feedback in questions[question]:
                                st.markdown("- " + feedback)