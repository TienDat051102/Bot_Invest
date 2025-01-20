from openai import OpenAI
import uuid
from db import save_message, get_conversation, get_training_data,get_conversation_context,get_jobversion,save_data_faq
from collections import deque

# Kết nối OpenAI
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)
jobversion = str(uuid.uuid4())
def start(conversation_id):
    messages = []
    
    training = get_training_data()
    for item in training:
        messages.append(item)
    
    conversation = get_conversation(conversation_id)
    messages.extend(conversation)
    
    return messages
def save_faq():
    faq = get_jobversion(jobversion)
    print('faq',faq)
    for entry in faq:
        if entry['type'] == 'question':
            question = entry['content']
            conversation_id = entry['conversation_id']
            timestamp = entry['timestamp']
        elif entry['type'] == 'answer':
            answer = entry['content']
            save_data_faq(question, answer, conversation_id, timestamp)

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

messages = deque(start(conversation_id))
print(f"AI Bot đã sẵn sàng! Ngữ cảnh hiện tại: {category}. Gõ 'exit' để thoát.\n")

while True:
    user_input = input("Tiến Đạt :").strip()
    if user_input.lower() == "exit":
        print("Tạm biệt!")
        break
    if(user_input.lower()== "save"):
        save_faq()
        print("Tạm biệt!")
        break
    messages.append({"role": "user", "content": user_input})
    save_message(conversation_id, "user", user_input,jobversion)
    try:
        response = client.chat.completions.create(
            model="gemma2:2b",
            messages=list(messages)
        )
        reply = " ".join(response.choices[0].message.content.split()).strip()
        
        print(f"Trợ lý riêng : {reply.strip()}")
        save_message(conversation_id, "assistant", reply.strip(),jobversion)
        messages.append({"role": "assistant", "content": reply.strip()})
    
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")
