import broadlink
import time

# ==============================================================================
# == คลังเก็บรหัสรีโมต (IR Code Storage) ==
# ==============================================================================

# 1. คลังเก็บรีโมตทีวี (คุณต้องนำรหัสที่เรียนรู้จากรีโมต Hisense มาใส่ที่นี่)
TV_POWER_CODES = {
    'HISENSE_TV': b'26005000000128931412131213371411131214111412131213121337143714361437143714111411141114371411143714111437143713371412131213121312133714371437133714000d05000000000000'
}

# 2. คลังเก็บรีโมตแอร์ (รอให้คุณนำรหัสจริงมาใส่)
# คุณต้องใช้ learn_ir_codes.py เพื่อเรียนรู้รหัสจากรีโมตแอร์จริงๆ แล้วนำมาใส่ที่นี่
AC_CODES = {
    'DEFAULT_AC': {
        'POWER_TOGGLE': b'YOUR_AC_POWER_CODE_HERE',
        'TEMP_UP': b'YOUR_AC_TEMP_UP_CODE_HERE',
        'TEMP_DOWN': b'YOUR_AC_TEMP_DOWN_CODE_HERE',
        'SET_25_DEGREES': b'YOUR_AC_SET_25_CODE_HERE'
    }
}


# ==============================================================================
# == ฟังก์ชันสำหรับส่งสัญญาณ (ใช้งานจริง) ==
# ==============================================================================
def send_ir_command(broadlink_ip, command_code):
    """
    ฟังก์ชันสำหรับส่งคำสั่ง IR ไปยัง Broadlink ที่กำหนด (ส่วนนี้สมบูรณ์แล้ว)
    """
    if not command_code or b'YOUR_' in command_code:
        print(f"ERROR: ไม่ได้รับ IR Code หรือยังเป็นรหัสตัวอย่างสำหรับส่งไปยัง {broadlink_ip}")
        return False
        
    try:
        device = broadlink.hello(broadlink_ip, timeout=5)
        
        if not device:
            print(f"ERROR: ไม่สามารถเชื่อมต่อกับ Broadlink ที่ IP: {broadlink_ip}")
            return False
        
        device.auth()
        device.send_data(command_code)
        
        print(f"SUCCESS: ส่งคำสั่งไปยัง Broadlink ที่ {broadlink_ip} สำเร็จ!")
        return True

    except Exception as e:
        print(f"ERROR: เกิดข้อผิดพลาดในการส่งคำสั่ง IR: {e}")
        return False
