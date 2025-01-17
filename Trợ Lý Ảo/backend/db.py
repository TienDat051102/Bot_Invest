import psycopg2
from datetime import datetime
import uuid

# Kết nối tới cơ sở dữ liệu PostgreSQL
def get_connection():
    return psycopg2.connect(
        dbname="chatbot_db", 
        user="postgres",    
        password="0511", 
        host="localhost",
        port="5432"
    )

# Tạo cuộc trò chuyện mới và lưu ngữ cảnh
def create_conversation(category):
    conversation_id = str(uuid.uuid4()) 
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.now()
    
    # Lưu thông tin ngữ cảnh vào cơ sở dữ liệu
    query = """
    INSERT INTO conversations (conversation_id, category, timestamp)
    VALUES (%s, %s, %s)
    """
    cursor.execute(query, (conversation_id, category, timestamp))
    conn.commit()
    cursor.close()
    conn.close()
    
    return conversation_id

# Lưu tin nhắn vào cơ sở dữ liệu
def save_message(conversation_id, role, content, category="general"):
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.now()
    query = """
    INSERT INTO messages (conversation_id, timestamp, role, content, category)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (conversation_id, timestamp, role, content, category))
    conn.commit()
    cursor.close()
    conn.close()

# Truy vấn lịch sử trò chuyện từ CSDL PostgreSQL
def get_conversation(conversation_id, category=None):
    conn = get_connection()
    cursor = conn.cursor()
    if category:
        query = """
        SELECT role, content FROM messages
        WHERE conversation_id = %s AND category = %s
        ORDER BY timestamp
        """
        cursor.execute(query, (conversation_id, category))
    else:
        query = """
        SELECT role, content FROM messages
        WHERE conversation_id = %s
        ORDER BY timestamp
        """
        cursor.execute(query, (conversation_id,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result
