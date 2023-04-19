import openai

class GPT4:
    def __init__(self):
        self.model = "gpt-4"
        self.temperature = 0
        self.max_tokens = 1000

    def set_api_key(self, api_key):
        openai.api_key = api_key

    def chat(self, messages):
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return response
