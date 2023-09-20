import streamlit as st
import os
from utils.classify import classify
from classes import categories, category_embeddings
from utils.generate import generate
from utils.extract import extract
from streamlit_carousel import carousel



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
        coded = classify(qualitative, categories, category_embeddings)
        st.success("Coded Qualitative Feedback")
        
        # TODO: Add cards on top

        prompt = f"""
            Using the feedback in parenthesis, summarise the feedback into the instructor's top strengths, what students loved about the class, what students loved about and what improvements students would like, and output it in the format in triple backticks. Keep the summary for each category within 1 short and concise sentence.

            ({qualitative})

            ```
            Your Top Strengths:
            What Students Loved About Your Class:
            What Students Loved About You:
            What Students Want:
            ```
        """

        for_cards = generate(prompt, 'gpt-3.5-turbo').split('\n')[1:-1]
        for_cards = [card.split(': ')[1] for card in for_cards]

        image = "https://img.freepik.com/free-photo/smooth-green-background_53876-108464.jpg?w=1800&t=st=1695203570~exp=1695204170~hmac=c92ce6fb6daa3caebe142090e1e2ed96186d9a02b337f51e23646a5fb6c088bc"

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