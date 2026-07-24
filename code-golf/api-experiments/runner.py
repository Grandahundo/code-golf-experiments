# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI

# print(response.choices[0].message.content)
def run(model, api_key, task_id, prompt):
    client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompt},
        ],
        stream=False,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )

    code = response.choices[0].message.content
    log(code)