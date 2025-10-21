class OpenAIClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def call_openai_api(self, prompt):
        import openai
        openai.api_key = self.api_key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return self.handle_response(response)

    def handle_response(self, response):
        if 'choices' in response and len(response['choices']) > 0:
            return response['choices'][0]['message']['content']
        else:
            raise Exception("Invalid response from OpenAI API")