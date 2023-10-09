from typing import List
from transformers import pipeline

model = pipeline("text-classification", model="unitary/toxic-bert")

def nasty_filter(feedback:List[str], threshold:int=0.001) -> List[List[str]]:

    predictions = model(feedback)
    nasty = [f for i, f in enumerate(feedback) if predictions[i]['score'] > threshold]
    not_nasty = [f for i, f in enumerate(feedback) if predictions[i]['score'] <= threshold]

    return [nasty, not_nasty]