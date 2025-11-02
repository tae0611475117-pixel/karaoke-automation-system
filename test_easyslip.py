import requests

# ===============================================================
# == กรุณาใส่ข้อมูลของคุณในส่วนนี้ก่อนทำการทดสอบ ==
# ===============================================================

# 1. ใส่ API Key "ของจริง" ของ SlipOK ที่นี่
YOUR_API_KEY = "SLIPOK7I5XHWR"

# 2. ตรวจสอบให้แน่ใจว่าชื่อไฟล์ตรงกับสลิปที่คุณเตรียมไว้
SLIP_IMAGE_PATH = "test_slip.png" 

# 3. URL สำหรับ SlipOK (กรุณาตรวจสอบจากเอกสารของ SlipOK อีกครั้ง)
# โดยทั่วไปมักจะเป็น URL สำหรับ Production
API_URL = "https://api.slipok.com/api/v1/verify/image"

# ===============================================================


def run_test():
    """
    ฟังก์ชันสำหรับทดสอบการเชื่อมต่อกับ SlipOK โดยตรง
    """
    if YOUR_API_KEY == "YOUR_SLIPOK_API_KEY_HERE":
        print("!!! ข้อผิดพลาด: กรุณาใส่ API Key ของคุณในตัวแปร YOUR_API_KEY ก่อนรัน")
        return

    print(f"กำลังจะทดสอบส่งไฟล์ '{SLIP_IMAGE_PATH}' ไปยัง '{API_URL}'...")

    try:
        # เปิดไฟล์สลิปในโหมด binary
        with open(SLIP_IMAGE_PATH, 'rb') as slip_file:
            
            # --- แก้ไขจุดสำคัญ: เปลี่ยนชื่อ field จาก 'file' เป็น 'data' ---
            # ตามที่ Error message ของ SlipOK แนะนำ
            files = {'data': slip_file}
            
            # SlipOK อาจจะใช้ชื่อ Header ที่แตกต่างออกไป (เช่น x-api-key)
            # แต่เราจะลองใช้ Bearer Token ซึ่งเป็นมาตรฐานก่อน
            headers = {'Authorization': f'Bearer {YOUR_API_KEY}'}

            # ส่งคำขอ
            response = requests.post(API_URL, files=files, headers=headers, timeout=20)

            # พิมพ์ผลลัพธ์ที่ได้รับกลับมาทั้งหมด
            print("\n--- ผลลัพธ์จากเซิร์ฟเวอร์ SlipOK ---")
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
            print("------------------------------------")

    except FileNotFoundError:
        print(f"\n!!! ข้อผิดพลาด: ไม่พบไฟล์สลิปที่ชื่อ '{SLIP_IMAGE_PATH}'")
        print("กรุณานำไฟล์สลิปทดสอบมาวางไว้ในโฟลเดอร์เดียวกันนี้")
    except Exception as e:
        print(f"\n!!! เกิดข้อผิดพลาดร้ายแรงระหว่างการเชื่อมต่อ: {e}")


if __name__ == '__main__':
    run_test()