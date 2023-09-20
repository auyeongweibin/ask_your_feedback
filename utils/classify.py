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

    result = {key: value for key, value in result.items() if len(value) > 0}

    return result