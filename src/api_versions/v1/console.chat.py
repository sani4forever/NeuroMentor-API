import requests

BASE_URL = "http://localhost:8000/api/v1"


def start_test():
    print("--- NeuroMentor Console Tester ---")

    user_name = input("Введите ваше имя: ")
    user_age = input("Ваш возраст: ")

    reg_data = {"name": user_name, "age": int(user_age), "gender": "male"}

    try:
        response = requests.post(f"{BASE_URL}/user", json=reg_data)
        response.raise_for_status()  # Проверка на ошибки (4xx, 5xx)
        user_res = response.json()

        user_id = user_res.get("id")
        if user_id is None:
            print("Ошибка: Сервер не вернул ID пользователя")
            return

        session_id = 0

        print(f"\nПривет, {user_name}! (Твой ID в базе: {user_id}).")
        print("Теперь пиши сообщения (или 'exit' для выхода):")

        while True:
            text = input("\nВы: ")
            if text.lower() in ['exit', 'выход', 'quit']:
                break

            payload = {
                "user_id": user_id,
                "session_id": session_id,
                "message": text
            }

            chat_response = requests.post(f"{BASE_URL}/chat", json=payload)

            if chat_response.status_code == 200:
                answer = chat_response.json().get('answer')
                print(f"\nNeuroMentor: {answer}")
            else:
                print(f"\nОшибка API ({chat_response.status_code}): {chat_response.text}")

    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")


if __name__ == "__main__":
    start_test()