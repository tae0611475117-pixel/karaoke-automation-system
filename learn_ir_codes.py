import tinytuya
import time

# ==============================================================================
# == โหมดจำลองการทำงาน (Simulation Mode) ==
# ==============================================================================
# ตั้งค่าเป็น True เพื่อทดสอบระบบโดย "ไม่ต้อง" มีข้อมูลอุปกรณ์จริง
# เมื่อคุณได้ข้อมูลครบแล้ว ให้เปลี่ยนค่านี้เป็น False
SIMULATION_MODE = True
# ==============================================================================


# ==============================================================================
# == ข้อมูลอุปกรณ์ Tuya (ต้องหาข้อมูลมาใส่) ==
# ==============================================================================
# คุณต้องใช้ tinytuya-cli wizard เพื่อหาข้อมูลเหล่านี้
# ดูขั้นตอนได้ที่: https://github.com/jasonacox/tinytuya#get-local-keys

# --- ใส่ข้อมูลของ IR Blaster แต่ละห้องที่นี่ ---
# คุณต้องหา Device ID, IP Address, และ Local Key ของ IR Blaster ทุกตัว
TUYA_DEVICES = {
    'VIP1': {
        'id': 'DEVICE_ID_OF_VIP1_IR_BLASTER',
        'ip': '192.168.1.201', # IP ของ IR Blaster (ต้องเช็คจาก Router)
        'key': 'LOCAL_KEY_OF_VIP1_IR_BLASTER'
    },
    'SUB1': {
        'id': 'DEVICE_ID_OF_SUB1_IR_BLASTER',
        'ip': '192.168.1.203',
        'key': 'LOCAL_KEY_OF_SUB1_IR_BLASTER'
    },
    # ... เพิ่มข้อมูลของห้องอื่นๆ ให้ครบ ...
}
# ==============================================================================


# ==============================================================================
# == ฟังก์ชันสำหรับส่งสัญญาณ (ฉบับ Tuya) ==
# ==============================================================================
def send_tuya_command(room_id, command):
    """
    ฟังก์ชันสำหรับส่งคำสั่งไปยัง Tuya IR Blaster ที่กำหนด
    command คือ Dictionary ของคำสั่ง เช่น {'control': 'Power'}
    """
    if room_id not in TUYA_DEVICES:
        print(f"ERROR: ไม่พบข้อมูลอุปกรณ์ Tuya สำหรับห้อง {room_id} ใน TUYA_DEVICES")
        return False

    device_info = TUYA_DEVICES[room_id]
    device_id = device_info['id']
    device_ip = device_info['ip']
    local_key = device_info['key']

    if 'DEVICE_ID' in device_id or 'LOCAL_KEY' in local_key:
        print(f"ERROR: ข้อมูลสำหรับห้อง {room_id} ยังไม่สมบูรณ์")
        # --- โหมดจำลองการทำงาน ---
        if SIMULATION_MODE:
            print("\n===============================================")
            print("      >>> SIMULATION MODE - NO HARDWARE INFO <<< ")
            print(f"      จำลองการส่งคำสั่งไปห้อง: {room_id}")
            print(f"      คำสั่งที่ส่ง: {command}")
            print("      [จำลองว่าส่งสัญญาณสำเร็จ]")
            print("===============================================\n")
            return True
        return False
        
    try:
        print(f"Connecting to Tuya device {room_id} at {device_ip}...")
        # สร้างการเชื่อมต่อกับอุปกรณ์
        d = tinytuya.Device(device_id, device_ip, local_key)
        d.set_version(3.3) # IR Blasters ส่วนใหญ่ใช้เวอร์ชัน 3.3

        # ส่งคำสั่ง
        print(f"Sending command {command} to {room_id}")
        payload = d.generate_payload('send_ir_code', command)
        d.send(payload)
        
        print(f"SUCCESS: ส่งคำสั่งไปยัง Tuya IR Blaster ห้อง {room_id} สำเร็จ!")
        return True

    except Exception as e:
        print(f"ERROR: เกิดข้อผิดพลาดในการส่งคำสั่ง Tuya: {e}")
        return False

# --- ส่วนสำหรับทดสอบ ---
if __name__ == '__main__':
    # เปลี่ยนเป็น ID ห้องที่ต้องการทดสอบ
    test_room_id = 'VIP1'
    
    # นี่คือ "ตัวอย่าง" Dictionary คำสั่งสำหรับเปิดทีวี
    # คุณต้องหาคำสั่งที่ถูกต้องจากแอป Smart Life
    tv_power_command = {
        "control": "Power",
        "remote_index": "tv", # ชื่อรีโมตที่คุณตั้งในแอป
        "code": "Power"       # ชื่อปุ่มที่คุณกดในแอป
    }

    print(f"\n--- กำลังทดสอบส่งคำสั่งไปยังห้อง {test_room_id} ---")
    send_tuya_command(test_room_id, tv_power_command)
```

---

### **ขั้นตอนต่อไปที่คุณต้องทำ**

1.  **ตั้งค่าในแอป Smart Life:**
    * เพิ่มอุปกรณ์ Tuya IR Blaster ทั้ง 7 ตัวของคุณเข้าไปในแอป
    * ในแอป ให้เข้าไปที่อุปกรณ์ IR Blaster แต่ละตัว แล้วกด **"เพิ่มรีโมต" (Add Remote)**
    * เพิ่มรีโมตสำหรับ **"ทีวี"** และ **"แอร์"** ของคุณ โดย "สอน" หรือเลือกยี่ห้อให้ตรงกับที่คุณใช้ ตั้งชื่อรีโมตให้จำง่าย เช่น `tv`, `ac`

2.  **ติดตั้งเครื่องมือ `tinytuya`:**
    * เปิด Terminal ที่มี `(.venv)` activate อยู่
    * รันคำสั่ง: `pip install tinytuya`

3.  **หาข้อมูลลับของอุปกรณ์ (สำคัญที่สุด):**
    * ใน Terminal เดิม ให้รันคำสั่ง "พ่อมด" ของ `tinytuya`:
      ```bash
      tinytuya-cli wizard
      