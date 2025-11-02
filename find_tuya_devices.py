import tinytuya
import json

print("Scanning for Tuya devices for 20 seconds...")
print("Please wait...")

try:
    # --- นี่คือคำสั่งสแกนเวอร์ชันใหม่ที่ถูกต้อง ---
    # ฟังก์ชัน deviceScan() จะทำการสแกนและคืนค่าอุปกรณ์ที่เจอทั้งหมด
    devices = tinytuya.deviceScan(False, 20)
    
    print("\n--- Scan Complete! Devices Found: ---")
    
    # จัดรูปแบบผลลัพธ์ให้อ่านง่ายขึ้น
    # ผลลัพธ์ที่ได้จะเป็น Dictionary ซ้อนกันอยู่
    formatted_devices = {}
    if devices:
        for ip, data in devices.items():
            device_id = data.get('gwId')
            if device_id:
                formatted_devices[device_id] = {
                    'id': device_id,
                    'ip': ip,
                    'key': data.get('key'),
                    'version': data.get('version')
                }
    
    print(json.dumps(formatted_devices, indent=4))
    print("\n------------------------------------")
    print("Please look for your IR Blaster devices in the list above.")
    print("You will need the 'id', 'ip', and 'key' for each device.")

except Exception as e:
    print(f"\n!!! An error occurred during scanning: {e}")
    print("Please ensure your computer is on the same WiFi network as your Tuya devices.")


#### **2. เริ่ม "การสืบสวน"**


