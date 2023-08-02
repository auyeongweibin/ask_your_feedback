import streamlit as st
from unstructured.partition.pdf import partition_pdf
import openai
import google.generativeai as palm
import os
from dotenv import load_dotenv
import torch.nn.functional as F
from torch import Tensor
from transformers import AutoTokenizer, AutoModel
from transformers import pipeline

# TODO: Refactor code

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
palm.configure(api_key=os.getenv("PALM_KEY"))

categories = [
    'Class Environment',
    'Classmates',
    'Course Content/Topics',
    'Course Materials',
    'Course Structure',
    'Evaluation/Feedback',
    'Facilities/Equipment',
    'Feedback to Instructor',
    'General',
    'Guests',
    'Instruction',
    'Instructor Characteristics',
    'Learning Activities',
    'Learning/Cognition',
    'Program Curriculum',
    'Staff',
    'TA',
    'Feedback to Program',
    'Program Environment',
    'Program Materials',
    'Program Policy/Procedure',
    'None'
]

category_descriptions = [
    'Class Environment: The psychological and affective atmosphere of the course, such as friendliness, comfort level, level of stress. (References to physical setting are usually coded Facilities/Equipment.)', 
    'Classmates: Information regarding classmates/peers, such as their abilities to work in groups, behavior in class (e.g., excessive talking or asking off-topic questions), helpfulness, and language proficiency. (General references to group work that do not indicate how students do/don’t benefit from peers are usually coded Learning Activities.)',
    'Course Content/Topics: Information regarding the quantity, quality, or relevance of topics or ideas covered, or suggestions for additional content. Example student comment: “More real-world applications.”',
    'Course Materials: Information regarding quantity or quality of instructional supplies or tools that students use, including course handouts, slides, overheads, course website, videos, textbooks, or readings. Includes comments about how assignment expectations are conveyed (e.g., confusing or disorganized instructions). Example student comment: “The syllabus [as a document] was unclear and lacked important information.” (References to readings-based assignments should be coded Learning Activities. References to exam solutions should be coded Evaluation/Feedback. References to prior student work and assignment solutions should be coded Learning Activities.)',
    'Course Structure: Information regarding the sequence, flow, alignment, organization, size, modality (in person vs. online, synchronous vs. asynchronous), or scheduling of course activities/content, including office hours, assignment deadlines. Also includes references to number of credits and proportionality of coursework. Example student comments: “Assignments on a topic should follow the lecture on that topic,” “Having a small class size helps us learn,” “Class is too long” or “early.” (References to how individual class sessions are structured should be coded Instruction. General references to assignment milestones should be coded Learning Activities.)',
    'Evaluation/Feedback: Information regarding grading, tests, quizzes, evaluation criteria,credit, or quality/quantity of feedback on course work, learning progress, or performance. Includes references to practice exams and solutions, exam review sessions, general references to peer review,as well the use of rubrics in grading or providing feedback.(References to rubrics provided in advance should be coded Learning Activities.)',
    'Facilities/Equipment: Information regarding the classroom space, physical infrastructure,technology, building, location, availability, or accessibility.',
    'Feedback to Instructor: Information regarding opportunities to provide input on the course for teaching, as well as the instructor’s responsiveness to that feedback. Includes course changes made in response to student input. Example student comments: “Instructor gathered too much feedback,” “Nice that she collected and responded to feedback before the end of the quarter.” (General references to instructor flexibility should be coded Instructor Characteristics.)',
    'General: Information that is not specific to any of the other codes, such as comments about the course overall. Example student comment: “This Course was great/terrible.”',
    'Guests: Information regarding the guest speakers, project advisors, project evaluators, or other visitors.',
    'Instruction: Information regarding the pedagogy or practices of the instructor,i.e., what the instructor does in class (i.e., lesson planning,use/management of class time), office hours, lecturing, presenting, explaining, demonstrating, and questioning. (Note: This includes pace of instruction in a given class session,general references to in-class examples, instructor contributions to online discussion, number of but not timing of office hours, use of humor or encouragement as a pedagogical tool/strategy.)',
    'Instructor Characteristics: Information regarding instructor’s nature or personality, such as knowledge, passion/enthusiasm, friendliness, sense of humor, carefor students (e.g., well-being, learning, success), general references to flexibility, etc., but not teaching style (cf. Instruction).',
    'Learning Activities: Information regarding activities students engage in to learn, such asin-class exercises, assignments (including examples of prior studentwork, solutions), practice problems, lab activities and assignments,group work, readings-based assignments, writing, involvement on discussion boards, presenting, or participating. Also includes general references to workload, to rubrics provided in advance to clarify assignment expectations, to assignment milestones. (Generalreferences to reading materials should be codedCourse Materials.Specific references to number or timing of milestones should be coded Course Structure.)',
    'Learning/Cognition: Information regarding whether or not learning was happening, level of challenge, progress toward learning objectives, clarity of learning objectives, how the instructor motivates learning, etc.',
    'Program Curriculum: Information regarding the programmatic curricula, such as thecourse’s placement in the curriculum, pre-requisite courses, its relation to other courses, conflicts with other courses (e.g., due to scheduling, workload, due dates, etc.).',
    'Staff: Information regarding course-related personnel who are neither instructors nor TAs (e.g., lab technicians).',
    'TA: Any information regarding the TA, unless the TA was acting as the instructor, in which case all codes regarding “instructor” will apply.Includes general references to lab/quiz sections. (Note: In cases where the professor requested the assessment and the TA acted as instructor for part of the evaluation period, this code would be used for any TA-related student feedback.)',
    'Feedback to Program: Analogous to Feedback to Instructor except applying to the program or department as a whole, rather than an individual course.',
    'Program Environment: Analogous to Class Environment except applying to multiple courses or the program as a whole, rather than an individual course.',
    'Program Materials: Information regarding quantity or quality of instructional supplies or tools that students use, but not specific to a course. Example student comment: “Update web pages on program requirements.”',
    'Program Policy/Procedure: Information regarding policies/procedures that affect multiple courses or the program as a whole. Excludes those related to course selection (cf. Program Curriculum)',
    'None, N/A, NIL'
]

sub_categories = [
    'What is helping you learn',
    'What changes could be made'
]

# tokenizer = AutoTokenizer.from_pretrained("thenlper/gte-large")
# model = AutoModel.from_pretrained("thenlper/gte-large")

# def average_pool(last_hidden_states: Tensor,
#                  attention_mask: Tensor) -> Tensor:
#     last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
#     return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

st.title('Instructor-Feedback-GPT')
st.markdown("## Hi Instructor, let me summarise your feedback for you 🎈")

file = st.file_uploader('Upload your feedback!')
if file:
    file_details = {"FileName": file.name, "FileType": file.type}
    # st.write(file_details)

    with open(os.path.join("./uploads/", file.name),"wb") as f:
        f.write(file.getbuffer())
        st.success("Saved File")
    
    processed = partition_pdf(f'./uploads/{file.name}')

    is_qualitative = False

    qualitative = []

    for line in processed:
        text = str(line)
        if text == 'STANDARD OPEN-ENDED QUESTIONS' or text == 'Interpreting IASystem Course Summary Reports':
            is_qualitative = not is_qualitative
            continue
        if text.startswith('©') or text.startswith('Printed'):
            continue
        if is_qualitative and text[0].isdigit():
            qualitative.append(text[3:])
    
    st.success("Extracted Qualitative Feedback")

    # Prints out qualitative feedback
    # st.subheader(f'{file.name.replace(".pdf", "")} Qualitative Feedback:')
    # st.write('\n\n'.join(qualitative))

    # Save qualitative data into .txt file
    # with open(os.path.join("./processed_pdfs/", file.name.replace('pdf', 'txt')),"w") as f:
    #     f.write(qualitative)
    #     st.success("Saved Procesed File")

    # Classifying qualitative feedback into respective codes
    # TODO: Remove N/A kind of values before classifying
    # TODO: Pre-compute embeddings of categories and edit input layer ot GTE
    coded = {c:[] for c in categories}

    classifier = pipeline("zero-shot-classification", model="mjwong/e5-large-mnli")
    
    for feedback in qualitative:
        # result = classifier(feedback, category_descriptions)
        result = classifier(feedback, categories)
        index = result['scores']
        coded[categories[result['scores'].index(max(result['scores']))]].append(feedback)

    # for feedback in qualitative:
    #     input_texts = [feedback, *category_descriptions]
    #     batch_dict = tokenizer(input_texts, max_length=1024, padding=True, truncation=True, return_tensors='pt')

    #     outputs = model(**batch_dict)
    #     embeddings = average_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
    #     coded[categories[(embeddings[:1] @ embeddings[1:].T)[0].argmax().item()]].append(feedback)

    if coded.get(categories[-1]) is not None: del coded[categories[-1]]

    st.success("Coded Qualitative Feedback")

    # Classifying qualitative feedback into sub-categories within each code
    ken_format = {s:{c:[] for c in categories[:-1]} for s in sub_categories}

    # for key in coded:
    #     for feedback in coded[key]:
    #         input_texts = [feedback, *sub_categories, '']
    #         batch_dict = tokenizer(input_texts, max_length=512, padding=True, truncation=True, return_tensors='pt')

    #         outputs = model(**batch_dict)
    #         embeddings = average_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
    #         ken_format[sub_categories[(embeddings[:1] @ embeddings[1:].T)[0][:-1].argmax().item()]][key].append(feedback)
    
    for key in coded:
        for feedback in coded[key]:
            result = classifier(feedback, sub_categories)
            index = result['scores']
            ken_format[sub_categories[result['scores'].index(max(result['scores']))]][key].append(feedback)

    ken_format = {s:dict(filter(lambda item: item[1], ken_format[s].items())) for s in ken_format}

    st.success("Sub-categorised Qualitative Feedback")

    # TODO: Prepare prompt to generate ken template
    prompt = f'''
        Using the data in parenthesis, fill in the template in triple backticks

        ({ken_format})

        ```
        SGID I: What is helping you learn in this course? Please explain or give examples.
            for each code/category:
                Code/Category
                >One line header for this category
                Either direct quotes or examples 
                [number of groups who discussed]
                [number of individuals; helpful/suggestion]

        SGID II: What changes could be made that would assist you in learning?
            for each code/category:
                >Code/Category
                One line header for this category
                Either direct quotes or examples 
                [number of groups who discussed]
                [number of individuals; helpful/suggestion]
        ```
    '''

    # Using OpenAI
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "system", "content": "You are a helpful assistant and you need to summarise instructor course feedback."},
    #         {"role": "user", "content": prompt}
    #     ],
    #     temperature = 0
    # )

    # st.write(response.choices[0].message.content)

    # Using Bard
    defaults = {
    'model': 'models/chat-bison-001',
    'temperature': 0,
    'candidate_count': 1,
    'top_k': 40,
    'top_p': 0.95,
    }
    context = ""
    examples = []
    messages = [
        "Using the data in parenthesis, fill in the template in triple backticks\n\n        ({'What is helping you learn': {'Classmates': ['I think that the group projects contributed the most to my learning bc of how it helped me bounce ideas and get opinions from others.', 'Group work'], 'Course Content/Topics': ['Yes, the reports due for each research method caused me to think a lot about the data collected and find ways to show them in an interesting light.', 'Yes it was it got me think my about user research and the intentionality of the research.', 'Yes, I am learning to become a UX researcher, so I learned a lot about research methods.', ' I already had a lot of experience conducting user research, so a lot of the class felt like review. However, I still found it very useful to have validation for methods that I had learned out in the field.', \" Yes, I definitely learned a lot about user research and this was my first user research class that I've ever taken.\", ' The course overall is pretty good, and maybe giving more examples for the assignments could be better!', ' The lectures were quite long and were redundant with the textbook readings; it felt like a waste of time to read the book if we were going to have a lecture on the exact same material. I also felt that there were too many guest speakers and their lectures were not super helpful to me', 'Maybe provide more sample project ideas at the beginning of the class.', ' I think it would be cool to give the students more flexibility about what projects they want to do. People will feel more motivated/passionate if the project is something they care about (other than just for the purpose of the class)'], 'Feedback to Instructor': ['Studio time and feedback from assignments contributed most to my learning.', ' The practical assignments that I did, such as interviews and observations, were most helpful in teaching me how the concepts we learned in class are applicable in research', \" I think practicing new skills like coding contributed most to my learning. I also liked how Gary was flexible and understanding of students' needs and wants.\", ' The projects and having ongoing feedback on the projects, and the availability of the course staff were all very helpful', 'Some of the lectures midway through the course were not as helpful as I had hoped.', ' I think that at the beginning we spent a lot of time on the HUB example of researching when we wanted to spend more time in class working. However, Gary did see this want of the students and I really appreciated how he pivoted class content and gave us more time in class to work.'], 'General': ['Not having more specific examples of how to conduct certain types of user research.'], 'Guests': ['Going out into the field and conducting the user research.', 'Some guest speakers were really useful, especially the last one (when she presented on how to present your findings). When the guest speakers had a topic to teach us about, that was useful.', ' Probably the quarter long project.', 'Guest speakers because less time to work on reports and asks questions in class.'], 'Instruction': [' The instructors is very good at explaining the materials and gives us hands on activities to help us understand the concepts better.', ' Being early in the morning and 2 hours straight of lecturing/working with no break.', 'More work time with teacher on assignments.', ' Include a 10 minute break in the middle of lecturing.'], 'Learning/Cognition': ['I learned the different aspects of user research. Although I completed interviews previously, I truly learned how to conduct deep hang outs and surveys. I also learned the difference between deep hang outs and observations, which I believe was very important.', \"Yes; learned some valuable information and concepts that I knew existed, but didn't have a name for.\", 'This class was intellectually stimulating because it exposed me to user research for the first time.', ' This class was indeed intellectually stimulating because I was able to practice the concepts that we learned in the real world.', ' Yes, it was intellectually stimulating. It walked us through the research process from start to finish.', ' I think this class is very intellectually simulating. It helps me to think about the fundamentals for the usability testings and other user researches methods. This will be extremely helpful for my future career exploration process and becoming a user researcher. Additionally, this class helps me to think about the biases and ethical considerations within the researches methods and help me to become a better data researchers;.', ' This class was intellectually stimulating & did stress my thinking. The curriculum was rigorous and provided a lot of new information (which is not always the case)'], 'Program Curriculum': ['Too much homework.'], 'Staff': [' I enjoyed working on a team', \"Can you do checkins individually with team members? I know it's hard to meet with people one on one, but I experienced some interpersonal conflict with a team member and it was slightly difficult to navigate; some mentorship and guidance might've been useful. (We did these kind of check-in's in HCDE 318 and they were helpful)\"], 'Feedback to Program': ['Yes, and yes.', 'Yes, coming up with research questions and methods and revising them based on the feedback actually is very intellectually stimulating', 'Being able to work in groups on a quarter-long project to practice and apply skills we learned in class.', 'Classes were long :( 4. We picked a bad topic so that made it hard to learn and succeed in the course. I kinda wish Gary had rejected the project idea but that it was our idea', 'We picked a bad topic so that made it hard to learn and succeed in the course. I kinda wish Gary had rejected the project idea but that it was our idea and our responsibility', 'Something that detracted from my learning was not having moved to work in class to get feedback', 'Making it more hands-on. Providing more concrete examples rather than making it lecture-based.', 'I suggest prerecording lectures to leave more i class times and keeping the reduced amount of quizzes.', ' I think the time for the class should be later in the day if possible.', \" Unrelated to the professor but I just have difficulty waking up so early for 9:30's.\"], 'Program Materials': ['Less homework.']}, 'What changes could be made': {'Course Content/Topics': ['Class discussions', 'Not much...'], 'Feedback to Instructor': ['Feedback after turning in a report.'], 'General': [' I think everything so far is good!'], 'Guests': [' I honestly was not a huge fan of the guest speakers, or the random calling in the beginning (although that stopped eventually)'], 'Learning/Cognition': [' Yes, the high expectations on each report made writing it challenging.']}})\n\n        ```\n        SGID I: What is helping you learn in this course? Please explain or give examples.\n            Code/Category\n            >One line header for this category\n            Either direct quotes or examples \n            [number of groups who discussed]\n            [number of individuals; helpful/suggestion]\n\n        SGID II: What changes could be made that would assist you in learning?\n            Code/Category\n            >One line header for this category\n            Either direct quotes or examples \n            [number of groups who discussed]\n            [number of individuals; helpful/suggestion]\n        ```",
    ]
    # messages.append("NEXT REQUEST")
    response = palm.chat(
        **defaults,
        context=context,
        examples=examples,
        messages=messages
    )

    st.write(response.last)



