import os
from openai import OpenAI

class OpenAIApi:
    def __init__(self):

        self.openai = OpenAI(
            # This is the default and can be omitted
            api_key=os.environ.get(OPENAI_API_KEY),
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Say this is a test",
                }
            ],
            model="gpt-3.5-turbo",
        )

    def get_description(self, desc: str) -> str:
        try:
            description = self.openai.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Перепиши это описание по-другом: "+desc,
                }
            ],
            model="gpt-3.5-turbo",
            )
        except:
            return desc

        return description['choices'][0]['message']['content']