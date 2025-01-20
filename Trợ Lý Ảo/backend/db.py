
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

# Hàm lưu thông tin nhắn hỏi
def save_message(conversation_id, role, message,jobversion):  
    with conn.cursor() as cursor:
        if role == "user":
            response_value = "N/A"  
        elif role == "assistant":
            response_value = "Bot"
        else:
            response_value = "Unknown"
        cursor.execute(
            """
            INSERT INTO activity_log (user_id, message, response, conversation_id, timestamp,jobversion)
            VALUES (%s, %s, %s, %s, NOW(),%s);
            """,
            (1, message, response_value, conversation_id,jobversion)  
        )
    conn.commit()
#Hàm lấy dữ 
def get_conversation(conversation_id):
    cursor.execute(
        """
        SELECT question AS user_message, answer AS bot_response
        FROM faq
        WHERE conversation_id = %s
 	ORDER BY timestamp DESC
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

def get_jobversion(jobversion):
    cursor.execute(
        """
       Select message,response,conversation_id,timestamp from activity_log where jobversion = %s
 	ORDER BY timestamp ASC;
        """,
        (jobversion,)
    ) 
    history = cursor.fetchall()
    messages = []
    for row in history:
        message = row['message']
        response = row['response']
        conversation_id = row['conversation_id']
        timestamp = row['timestamp']
        
        if response == 'N/A':
            messages.append({"type": "question", "content": message, "conversation_id": conversation_id, "timestamp": timestamp})
        elif response == 'Bot':
            messages.append({"type": "answer", "content": message, "conversation_id": conversation_id, "timestamp": timestamp})
    return messages

def save_data_faq(question, answer,conversation_id, timestamp):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            insert into faq (question,answer,conversation_id,timestamp)
            VALUES (%s, %s, %s, %s);
            """,
            ( question, answer, conversation_id,timestamp)  
        )
    conn.commit()
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
