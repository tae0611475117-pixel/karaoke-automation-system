import os
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env เข้ามาในระบบ
load_dotenv()

class Config:
    """
    คลาสสำหรับรวบรวมการตั้งค่าทั้งหมดของโปรเจกต์
    """
    UPLOAD_FOLDER = 'uploads/'

    PROMPT_PAY_ID = os.getenv('PROMPT_PAY_ID')
    SLIPOK_API_KEY = os.getenv('SLIPOK_API_KEY')

    # --- 1. เพิ่ม: ฐานข้อมูลโค้ดส่วนลด ---
    # รูปแบบคือ 'โค้ดส่วนลด': เปอร์เซ็นต์ส่วนลด
    PROMO_CODES = {
        'RUKLUNGTH': 50,  # <-- ลด 50%
        'naruk': 20, # <-- ลด 10%
        'DOKBOU': 15   # <-- ลด 15%
    }

    # --- ข้อมูลของห้องทั้ง 7 ห้อง (เหมือนเดิม) ---
    ROOM_DATA = {
        'VIP1': {'name': 'PREMIUM 1', 'ip': '192.168.1.101', 'status': 'available', 'end_time': None,
                 'capacity': 8,
                 'broadlink_ip': '192.168.1.201', 'tv_model': 'DEFAULT_TV',
                 'prices': {1: 250, 2: 480, 3: 940, 0.5: 125}},
        
        'VIP2': {'name': 'PREMIUM 2', 'ip': '192.168.1.102', 'status': 'available', 'end_time': None,
                 'capacity': 8,
                 'broadlink_ip': '192.168.1.202', 'tv_model': 'DEFAULT_TV',
                 'prices': {1: 250, 2: 480, 3: 940, 0.5: 125}},
        
        'SUB1': {'name': 'VIP 1', 'ip': '192.168.1.103', 'status': 'available', 'end_time': None,
                 'capacity': 5,
                 'broadlink_ip': '192.168.1.203', 'tv_model': 'DEFAULT_TV',
                 'prices': {1: 150, 2: 280, 3: 540, 0.5: 75}},
                 
        'SUB2': {'name': 'VIP 2', 'ip': '192.168.1.104', 'status': 'available', 'end_time': None,
                 'capacity': 5,
                 'broadlink_ip': '192.168.1.204', 'tv_model': 'DEFAULT_TV',
                 'prices': {1: 150, 2: 280, 3: 540, 0.5: 75}},

        'SUB3': {'name': 'VIP 3', 'ip': '192.168.1.105', 'status': 'available', 'end_time': None,
                 'capacity': 5,
                 'broadlink_ip': '192.168.1.205', 'tv_model': 'DEFAULT_TV',
                 'prices': {1: 150, 2: 280, 3: 540, 0.5: 75}},

        'SUB4': {'name': 'VIP 4', 'ip': '192.168.1.106', 'status': 'available', 'end_time': None,
                 'capacity': 5,
                 'broadlink_ip': '192.168.1.206', 'tv_model': 'DEFAULT_TV',
                 'prices': {1: 150, 2: 280, 3: 540, 0.5: 75}},
                 
        'FAM1': {'name': 'Family', 'ip': '192.168.1.107', 'status': 'available', 'end_time': None,
                 'capacity': 15,
                 'broadlink_ip': '192.168.1.207', 'tv_model': 'DEFAULT_TV',
                 'prices': {1: 300, 2: 580, 3: 1140, 0.5: 150}},
    }