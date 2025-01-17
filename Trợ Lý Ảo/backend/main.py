from openai import OpenAI
from db import save_message, get_conversation, get_training_data,get_conversation_context
from collections import deque

# Kết nối OpenAI
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

def start(conversation_id):
    messages = []
    
    training = get_training_data()[-10:]
    for item in training:
        messages.append(item)
    
    conversation = get_conversation(conversation_id)[-10:]
    messages.extend(conversation)
    
    return messages[-20:]


def start_conversation():
    print("Chào bạn! Hãy chọn ngữ cảnh bạn muốn làm việc:")
    print("1. Công việc")
    print("2. Giải trí")
    print("3. Cá nhân")
    
    context_map = {
        "1": "work",
        "2": "entertainment",
        "3": "personal"
    }
    
    context_choice = input("Chọn ngữ cảnh (1, 2, 3): ").strip()
    
    if context_choice not in context_map:
        print("Lựa chọn không hợp lệ. Chọn 'Công việc' theo mặc định.")
        return "work"
    
    return context_map[context_choice]

category = start_conversation()
conversation_id = get_conversation_context(category)

messages = deque(start(conversation_id), maxlen=20)
print(f"AI Bot đã sẵn sàng! Ngữ cảnh hiện tại: {category}. Gõ 'exit' để thoát.\n")

while True:
    user_input = input("Tiến Đạt :").strip()
    if user_input.lower() == "exit":
        print("Tạm biệt!")
        break

    messages.append({"role": "user", "content": user_input})
    save_message(conversation_id, "user", user_input)


    try:
        response = client.chat.completions.create(
            model="gemma2:2b",
            messages=list(messages)
        )
        reply = response.choices[0].message.content
        
        print(f"Trợ lý riêng : {reply.strip()}")
        save_message(conversation_id, "assistant", reply.strip())
        messages.append({"role": "assistant", "content": reply.strip()})
    
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")
