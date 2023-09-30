# from typing import List
# import torch

# model_path = '../ucc_model.pt'
# model = torch.load(model_path)

# def nasty_filter(feedback:List[str]) -> List[List[str]]:

#     predictions = model(feedback)
#     nasty = list(filter(lambda x:x, predictions))
#     not_nasty = list(filter(lambda x:x, predictions))

#     return [nasty, not_nasty]