import streamlit as st
import os
from utils.classify import classify
from classes import categories, category_embeddings, category_descriptions
from utils.generate import generate
from utils.extract import extract_plus_questions
from streamlit_carousel import carousel



st.title('Summary V2')
st.markdown("## Hi Instructor, let me summarise your feedback for you 🎈")

file = st.file_uploader('Upload your feedback!')
if file:
    with open(os.path.join("./uploads/", file.name),"wb") as f:
        f.write(file.getbuffer())
    
    qualitative, school = extract_plus_questions(file.name)

    qualitative = list(filter(lambda x: x.split("Answer: ")[1].lower() not in ['nil', 'none', 'na', 'n/a', ''], qualitative))

    st.success("Extracted Qualitative Feedback")

    if len(qualitative) == 0:
        st.error('No Qualitative Feedback Found')
    else:
        coded = classify(items=qualitative, classes=categories, embeddings=category_embeddings, multilabel=True, threshold=0.85)
        st.success("Coded Qualitative Feedback")

        coded_without_questions = [[feedback.split(" Answer: ")[1] for feedback in coded[code]] for code in coded]

        prompt = f"""
            Using the feedback in parenthesis, summarise the feedback into the instructor's top strengths, what students loved about the class, what students loved about and what improvements students would like, and output it in the format in triple backticks. Keep the summary for each category within 1 short and concise sentence.

            ({qualitative})

            ```
            Your Top Strengths: [one sentence summary for first category]
            What Students Loved About Your Class: [one sentence summary for second category]
            What Students Loved About You: [one sentence summary for third category]
            What Students Want: [one sentence summary for fourth category]
            ```
        """

        for_cards = generate(prompt, 'gpt-3.5-turbo' if school=='UW' else 'gpt-3.5-turbo-16k').split('\n')[1:-1]
        for_cards = [card.split(': ')[1] for card in for_cards]

        image = "https://wallpapers.com/images/featured-full/plain-black-background-02fh7564l8qq4m6d.jpg"

        cards = [
            dict(
                title="Your Top Strengths",
                text=for_cards[0],
                interval=None,
                img=image
            ),
            dict(
                title="What Students Loved About Your Class",
                text=for_cards[1],
                img=image
            ),
            dict(
                title="What Students Loved About You",
                text=for_cards[2],
                img=image
            ),
            dict(
                title="What Students Want",
                text=for_cards[3],
                img=image
            )
        ]

        carousel(items=cards, width=1)

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