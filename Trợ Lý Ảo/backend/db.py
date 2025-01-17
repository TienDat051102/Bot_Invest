
import psycopg2
from psycopg2.extras import RealDictCursor
import json

conn = psycopg2.connect(
        dbname="Bot", 
        user="postgres",    
        password="0511", 
        host="localhost",
        port="5432"
)
cursor = conn.cursor(cursor_factory=RealDictCursor)

def get_conversation_context(context_choice):
    try:
        # Thực thi truy vấn với tham số hóa
        query = """
            SELECT * 
            FROM public.conversation_context
            WHERE context_data = %s
            ORDER BY id ASC
        """
        cursor.execute(query, (context_choice,))
        result = cursor.fetchone()
        
        # Kiểm tra kết quả và trả về ID nếu tồn tại
        if result:
            return result["id"]
        else:
            print("Không tìm thấy ngữ cảnh phù hợp.")
            return None
    except Exception as e:
        print(f"Lỗi khi truy vấn dữ liệu ngữ cảnh: {e}")
        return None


def save_message(conversation_id, role, message):  
    with conn.cursor() as cursor:
        if role == "user":
            response_value = "N/A"  
        elif role == "assistant":
            response_value = "Bot"
        else:
            response_value = "Unknown"
        cursor.execute(
            """
            INSERT INTO activity_log (user_id, message, response, conversation_id, timestamp)
            VALUES (%s, %s, %s, %s, NOW());
            """,
            (1, message, response_value, conversation_id)  
        )
    conn.commit()

def get_conversation(conversation_id):
    cursor.execute(
        """
        SELECT message AS user_message, response AS bot_response
        FROM activity_log
        WHERE conversation_id = %s
        ORDER BY timestamp DESC
        LIMIT 10;
        """,
        (conversation_id,)
    )
    history = cursor.fetchall()
    messages = []
    
    for row in reversed(history):
        if row["user_message"]:
            messages.append({"role": "user", "content": row["user_message"]})
        if row["bot_response"]:
            messages.append({"role": "assistant", "content": row["bot_response"]})
    
    return messages


def get_training_data():
    try:
        query = "SELECT input, output FROM training_data"
        cursor.execute(query)
        
        training_data = cursor.fetchall()
        messages = []
        for row in training_data: 
            user_input = row.get("input")
            assistant_output = row.get("output")
            
            if user_input:
                messages.append({"role": "user", "content": user_input})
            if assistant_output:
                messages.append({"role": "assistant", "content": assistant_output})
                
        return messages
    except Exception as e:
        print(f"Lỗi khi tìm nạp dữ liệu đào tạo: {e}")
        return []
