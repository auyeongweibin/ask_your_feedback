import streamlit as st
import openai
import google.generativeai as palm
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
palm.configure(api_key=os.getenv("PALM_KEY"))

st.title('Instructor-Feedback-GPT')
st.markdown("#### Hi Instructor, this tool is meant to help you make you feedback more effective and actionable, do try out the different features! 🎈")
st.markdown('#### Features:')
st.write('\nSummarise - Summarise the Feedback into Formats Focusing on What YOU Want to Know\n\nNegative Feedback - Rephrase Feedback to a More Positive Tone')