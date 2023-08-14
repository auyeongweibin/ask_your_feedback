import openai
# import google.generativeai as palm

def generate(prompt: str, model:str) -> str:

    # Using OpenAI
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            # {"role": "system", "content": "You are a helpful assistant and you need to summarise instructor course feedback."},
            {"role": "user", "content": prompt}
        ],
        temperature = 0
    )

    return response.choices[0].message.content

    # Using Bard (PaLM)
    # defaults = {
    # 'model': 'models/chat-bison-001',
    # 'temperature': 0,
    # 'candidate_count': 1,
    # 'top_k': 40,
    # 'top_p': 0.95,
    # }
    # context = ""
    # examples = []
    # messages = [
    #     prompt
    # ]
    # # messages.append("NEXT REQUEST")
    # response = palm.chat(
    #     **defaults,
    #     context=context,
    #     examples=examples,
    #     messages=messages
    # )
    # return response.last