from typing import List, Dict
from torch import Tensor
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

def classify(items: List[str], classes: List[str], embeddings: Tensor=None) -> Dict[str, List[str]]:
    result = {c:[] for c in classes}

    model = SentenceTransformer('thenlper/gte-large')

    if embeddings is None:
        embeddings = model.encode(classes)

    for feedback in items:
        embedding = model.encode(feedback)
        scores = [cos_sim(embedding, category) for category in embeddings]
        result[classes[scores.index(max(scores))]].append(feedback)

    return result


# TODO: Get embeddings of category descriptions

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