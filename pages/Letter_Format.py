import streamlit as st
import os
from utils.generate import generate
from utils.classify import classify
from utils.extract import extract
from classes import categories, sub_categories

st.title('Letter Format')
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
            Using the data in parenthesis, write a letter to summarise the feedback, an example is given in triple backticks

            ({ken_format})

            ```
            Subject: Positive Feedback and Constructive Suggestions for Improvement - HCDE Class

            Dear Instructor,

            I hope this email finds you well. I wanted to take a moment to share my thoughts on the HCDE class we recently completed. Firstly, I want to express my gratitude for your efforts and dedication throughout the course. Your commitment to our learning experience was evident, and I appreciate the hard work you put into creating a stimulating environment for us.

            When reflecting on the class, there were several aspects that I found to be extremely valuable in enhancing my understanding of the subject matter. Your support and availability were crucial in making the learning process smoother for me. Your willingness to address our questions, encourage exploration beyond the course scope, and provide real-life examples made the concepts come to life. It was evident that you genuinely cared about our progress and learning outcomes.

            Additionally, I found the integration of R programming and statistical analysis to be highly beneficial. These hands-on experiences allowed me to not only grasp the theoretical aspects but also apply them practically. The assignments were well-paced, and the prompt feedback enabled me to navigate the challenges effectively. Moreover, the opportunity to work on a group project that required the application of statistical concepts to a real-world scenario was a highlight of the course. This bridging of theory and practice greatly contributed to my learning.

            Furthermore, I want to acknowledge the effort you put into structuring the course. The balance between lectures, homework, readings, in-class activities, and office hours created a comprehensive learning journey that catered to various learning styles.

            While the course was largely positive, I believe there are some areas where minor improvements could be considered to make the learning experience even more enriching. Firstly, I appreciated the pace of the course; however, providing additional time and examples to delve deeper into the methods of analysis, particularly in the latter half of the course, could aid in better understanding. This adjustment could help students fully grasp complex concepts and feel more confident in their application.

            Moreover, considering the availability of supplementary resources or materials for those who may require a foundation in statistics could be helpful. This could ensure that students with varying levels of prior knowledge are better equipped to engage with the course material.

            Lastly, while the class size was conducive to a supportive environment, it might be beneficial to explore ways to maintain this environment as class sizes potentially increase. Your engagement and the interactions within our smaller class significantly contributed to our positive experience.

            I want to reiterate my appreciation for your commitment to our learning journey. Your dedication and approach to teaching left a lasting positive impression on me. I am grateful for the opportunity to have been a part of this class and to have learned from you.

            Thank you once again for your hard work and support. I look forward to applying the knowledge gained from this course to my future endeavors.

            Best regards,

            Ken-bot
            ```
        '''

        response = generate(prompt, 'gpt-3.5-turbo' if school == 'SMU' else 'gpt-3.5-turbo-16k')

        st.write(response)