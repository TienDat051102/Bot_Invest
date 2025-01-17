from openai import OpenAI
from db import save_message, get_conversation, create_conversation
from collections import deque

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

# Hàm để khởi tạo cuộc trò chuyện
def start_conversation():
    print("Chào bạn! Hãy chọn ngữ cảnh bạn muốn làm việc:")
    print("1. Công việc")
    print("2. Giải trí")
    print("3. Cá nhân")
    
    context_choice = input("Chọn ngữ cảnh (work, entertainment, personal): ").strip().lower()
    
    if context_choice in ["work", "entertainment", "personal"]:
        return context_choice
    else:
        print("Lựa chọn không hợp lệ. Chọn 'work' theo mặc định.")
        return "work"

# Bắt đầu cuộc trò chuyện và lưu ngữ cảnh vào CSDL
category = start_conversation()
conversation_id = create_conversation(category)

# Sử dụng deque để lưu tin nhắn một cách hiệu quả (lưu giới hạn 10 tin nhắn gần nhất)
messages = deque(maxlen=10)

print(f"AI Bot đã sẵn sàng! Ngữ cảnh hiện tại: {category}. Gõ 'exit' để thoát.\n")

while True:
    user_input = input("Tiến Đạt :").strip()
    
    if user_input.lower() == "exit":
        print("Tạm biệt!")
        break

    # Truy vấn CSDL nếu cần thiết
    if len(messages) == 0:  # Nếu chưa có tin nhắn trong bộ nhớ, truy vấn CSDL
        history = get_conversation(conversation_id, category)
        for role, content in history:
            messages.append({"role": role, "content": content})

    # Thêm tin nhắn mới của người dùng vào bộ nhớ
    messages.append({"role": "user", "content": user_input})

    # Lưu tin nhắn người dùng vào CSDL
    save_message(conversation_id, "user", user_input, category)

    try:
        # Gửi yêu cầu tới OpenAI với lịch sử tin nhắn đã tối ưu hóa
        response = client.chat.completions.create(
            model="gemma2:2b",
            messages=list(messages)
        )
        reply = response.choices[0].message.content
        
        # Hiển thị phản hồi của bot
        print(f"Trợ lý riêng : {reply}")

        # Lưu phản hồi của bot vào CSDL
        save_message(conversation_id, "assistant", reply, category)

        # Thêm phản hồi của bot vào bộ nhớ
        messages.append({"role": "assistant", "content": reply})

    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")
