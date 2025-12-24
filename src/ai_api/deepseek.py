import openai
from .base import APIError
import os

__all__ = ['DeepSeekAPI']


class DeepSeekAPI:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise APIError("DeepSeek API Key not found in environment variables")

        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )

    async def get_chat_response(self, user_info: dict, history: list, user_message: str):
        try:
            system_prompt = (
                f"Ты — ИИ-психолог NeuroMentor. "
                f"Твой собеседник: {user_info.get('name', 'Пользователь')}. "
                f"Пол: {user_info.get('gender', 'не указан')}, возраст: {user_info.get('age', 'не указан')}. "
                f"Общайся дружелюбно, учитывая эти данные."
            )

            messages = [{"role": "system", "content": system_prompt}]

            messages.extend(history[-10:])

            messages.append({"role": "user", "content": user_message})

            response = self.client.chat.completions.create(  # noqa
                model="deepseek-chat",
                messages=messages,
                stream=False
            )

            return {
                "text": response.choices[0].message.content,
                "tokens": response.usage.total_tokens
            }

        except Exception as e:
            raise APIError(f"DeepSeek API Error: {str(e)}")