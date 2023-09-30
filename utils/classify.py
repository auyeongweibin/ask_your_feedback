from typing import List, Dict
from torch import Tensor
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
from transformers import pipeline

def classify(items: List[str], classes: List[str], class_descriptions: List[str]=None, embeddings: Tensor=None, multilabel: bool=False, threshold: int=0.9) -> Dict[str, List[str]]:
    result = {c:[] for c in classes}
    
    # if multilabel:
    #     model = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    #     labels = class_descriptions if class_descriptions is not None else classes
    #     for feedback in items:
    #         prediction = model(feedback, labels, multilabel=multilabel)
    #         print(prediction['scores'])
    #         for index, score in enumerate(prediction['scores']):
    #             if score >= threshold: result[classes[index]].append(feedback)
    
    # else:
    model = SentenceTransformer('thenlper/gte-large')
    if embeddings is None:
        embeddings = model.encode(classes)

    for feedback in items:
        embedding = model.encode(feedback)
        scores = [cos_sim(embedding, category) for category in embeddings]
        if multilabel:
            for index, score in enumerate(scores):
                if score > threshold:
                    result[classes[index]].append(feedback)
        else:
            result[classes[scores.index(max(scores))]].append(feedback)

    result = {key: value for key, value in result.items() if len(value) > 0}

    return result