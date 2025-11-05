import os
import threading
import time
import requests
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from config import Config
from device_control import send_ir_command, TV_POWER_CODES

# --- การตั้งค่าพื้นฐาน ---
app = Flask(__name__)
app.config.from_object(Config)
ROOM_DATA = app.config['ROOM_DATA']
PROMPT_PAY_ID = app.config['PROMPT_PAY_ID']
USED_TRANS_REFS = set()
USED_SLIPS_FILE = "used_slips.txt"
PROMO_CODES = app.config.get('PROMO_CODES', {})

def load_used_slips():
    """ฟังก์ชันสำหรับโหลดเลขที่อ้างอิงของสลิปที่เคยใช้แล้วจากไฟล์"""
    try:
        with open(USED_SLIPS_FILE, "r") as f:
            # อ่านทุกบรรทัด, ตัดช่องว่าง, แล้วสร้างเป็น set
            return {line.strip() for line in f}
    except FileNotFoundError:
        # ถ้ายังไม่มีไฟล์ ให้เริ่มจาก set ว่างเปล่า
        print(f"INFO: '{USED_SLIPS_FILE}' not found. Starting with an empty set.")
        return set()
ACTIVE_TIMERS = {}
def save_used_slip(trans_ref):
    """ฟังก์ชันสำหรับบันทึกเลขที่อ้างอิงของสลิปลงในไฟล์"""
    # 'a' หมายถึง 'append' หรือการเขียนต่อท้ายไฟล์
    # ถ้ายังไม่มีไฟล์นี้ มันจะสร้างขึ้นมาให้โดยอัตโนมัติ
    if trans_ref:
        with open(USED_SLIPS_FILE, "a") as f:
            f.write(trans_ref + "\n")

# โหลดข้อมูลสลิปเก่าเข้ามาในระบบทันทีที่เริ่มโปรแกรม
USED_TRANS_REFS = load_used_slips()
# -------------------------------------------------------------

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# --- ที่เก็บนาฬิกาแยกต่างหาก ---
ACTIVE_TIMERS = {}

# --- ฟังก์ชันควบคุมอุปกรณ์ ---
def control_tv_power(room_id):
    """ฟังก์ชันสำหรับสั่ง เปิด/ปิด ทีวี โดยจะไปหารหัสที่ถูกต้องมาใช้เอง"""
    room = ROOM_DATA.get(room_id)
    if room and room.get('broadlink_ip') and room.get('tv_model'):
        broadlink_ip = room['broadlink_ip']
        tv_model = room['tv_model']
        power_code = TV_POWER_CODES.get(tv_model)
        
        print(f"Sending POWER command to room {room_id} (TV Model: {tv_model})")
        send_ir_command(broadlink_ip, power_code)
    else:
        print(f"ERROR: ไม่พบข้อมูล Broadlink IP หรือ TV Model สำหรับห้อง {room_id}")

def turn_off_tv_session(room_id):
    """ฟังก์ชันนี้จะถูกเรียกโดย Timer เมื่อหมดเวลา"""
    print(f"--- TIME'S UP for room {room_id}! ---")
    control_tv_power(room_id)
    
    room = ROOM_DATA.get(room_id)
    if room:
        room['status'] = 'available'
        room['end_time'] = None
        room['timer'] = None
        print(f"Room {room_id} is now available.")

# --- ฟังก์ชันตรวจสอบสลิปกับ "SlipOK" (ฉบับแก้ไข Header) ---
def verify_slip_with_slipok(slip_path, expected_amount, expected_receiver_account):
    """ฟังก์ชันสำหรับตรวจสอบสลิปกับ SlipOK โดยเช็คยอดเงินและบัญชีผู้รับ"""
    api_key = ('SLIP_API_KEY')
    api_url = " https://api.slipok.com/api/line/apikey/54559"

    if not api_key:
        return {'status': 'error', 'message': 'ตั้งค่า API Key ไม่สมบูรณ์'}

    try:
        with open(slip_path, 'rb') as slip_file:
            files = {'files': slip_file}
            
            # --- แก้ไขจุดสำคัญ: เปลี่ยนรูปแบบ Header ตามที่ SlipOK แนะนำ ---
            headers = {'x-authorization': 'SLIPOK7I5XHWR' }
            
            response = requests.post(api_url, files=files, headers=headers, timeout=20)          

            print("\n--- RAW SLIPOK API RESPONSE ---")
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
            print("--------------------------------\n")

            if response.status_code == 200:
                response_data = response.json()
                
                if response_data.get('success') is False:
                    return {'status': 'rejected', 'message': response_data.get('message', 'SlipOK ปฏิเสธสลิป')}

                data = response_data.get('data', {})
                
                # --- 2. อัปเกรด: เพิ่มด่านตรวจสลิปซ้ำด้วยตัวเอง ---
                trans_ref = data.get('transRef')
                if not trans_ref:
                    return {'status': 'rejected', 'message': 'ไม่สามารถอ่านเลขที่อ้างอิงจากสลิปได้'}
                
                if trans_ref in USED_TRANS_REFS:
                    return {'status': 'rejected', 'message': 'สลิปนี้เคยถูกใช้งานแล้ว'}
                # ----------------------------------------------------

                # --- ด่านที่ 2: ตรวจสอบยอดเงิน (ถูกต้องแล้ว) ---
                amount_from_slip = data.get('amount') 
                if amount_from_slip is None or float(amount_from_slip) != float(expected_amount):
                    return {'status': 'rejected', 'message': f'ยอดเงินไม่ถูกต้อง (สลิป: {amount_from_slip}, ที่ต้องการ: {expected_amount})'}

                # --- ด่านที่ 3: ตรวจสอบบัญชีผู้รับ (ถูกต้องแล้ว) ---
                receiver_account = data.get('receiver', {}).get('proxy', {}).get('value')
                if not receiver_account or not str(receiver_account).endswith(str(expected_receiver_account)[-4:]):
                    return {'status': 'rejected', 'message': 'บัญชีผู้รับไม่ถูกต้อง'}

                # --- ถ้าผ่านทุกด่าน: บันทึกสลิปและอนุมัติ ---
                save_used_slip(trans_ref)
                USED_TRANS_REFS.add(trans_ref)
                print(f"SUCCESS: Transaction {trans_ref} verified and recorded.")
                return {'status': 'approved', 'message': 'Payment confirmed.'}
            else:
                error_message = response.json().get('message', 'ไม่สามารถติดต่อบริการตรวจสอบสลิปได้')
                return {'status': 'error', 'message': error_message}
                
    except requests.exceptions.RequestException as e:
        print(f"A network exception occurred: {e}")
        return {'status': 'error', 'message': 'เกิดข้อผิดพลาดในการเชื่อมต่อเครือข่าย'}
    except Exception as e:
        print(f"An unexpected exception occurred: {e}")
        return {'status': 'error', 'message': 'เกิดข้อผิดพลาดภายในระบบ'}

        USED_SLIPS_FILE = "used_slips.txt"

def load_used_slips():
    try:
        with open(USED_SLIPS_FILE, "r") as f:
            return {line.strip() for line in f}
    except FileNotFoundError:
        return set()

def save_used_slip(trans_ref):
    if trans_ref:
        with open(USED_SLIPS_FILE, "a") as f:
            f.write(trans_ref + "\n")

USED_TRANS_REFS = load_used_slips()

# --- ส่วนของหน้าเว็บ (Routes) ---
@app.route('/')
def index():
    return render_template('index.html', rooms=ROOM_DATA)

# -------------------------------------------------------------
# --- จุดที่ 1: แก้ไข Route และฟังก์ชัน payment_page ---
# -------------------------------------------------------------
@app.route('/pay/<room_id>/<hours>') # <--- ลบ 'float:' ออก
def payment_page(room_id, hours):
    
    try:
        # --- เพิ่มเข้ามา: แปลง hours (string) เป็น float ---
        hours_float = float(hours)
    except ValueError:
        return "Invalid duration format", 400 # กันคนพิมพ์ URL มั่ว
        
    if room_id not in ROOM_DATA:
        return "Room not found", 404
        
    room = ROOM_DATA[room_id]
    # --- เปลี่ยน hours เป็น hours_float ---
    original_price = room['prices'].get(hours_float) 
    
    if original_price is None:
        return "Invalid duration", 404

    promo_code = request.args.get('promo', None)
    discount_percent = PROMO_CODES.get(promo_code, 0)
    
    discount_amount = round((original_price * discount_percent) / 100)
    final_price = original_price - discount_amount

    qr_img_path = "static/bank_qr.png"

    return render_template('payment.html', 
                           room=room, 
                           room_id=room_id, 
                           hours=hours_float, # --- ส่ง hours_float ไปหน้าเว็บ
                           price=final_price, 
                           original_price=original_price,
                           discount_amount=discount_amount,
                           promo_code=promo_code,
                           qr_image=qr_img_path)
# -------------------------------------------------------------
# --- จบจุดที่ 1 ---
# -------------------------------------------------------------

@app.route('/status/<room_id>')
def room_status(room_id):
    room = ROOM_DATA.get(room_id)
    if room and room['status'] == 'occupied' and room.get('end_time'):
        remaining = max(0, room['end_time'] - time.time())
        return jsonify({'status': room['status'], 'remaining_seconds': remaining})
    return jsonify({'status': 'available', 'remaining_seconds': 0})

# -------------------------------------------------------------
# --- จุดที่ 2: แก้ไข Route และฟังก์ชัน upload_slip ---
# -------------------------------------------------------------
@app.route('/upload_slip/<room_id>/<hours>', methods=['POST']) # <--- ลบ 'float:' ออก
def upload_slip(room_id, hours):
    file = request.files.get('slip')
    if not file or file.filename == '':
        return jsonify({'status': 'error', 'message': 'กรุณาเลือกไฟล์สลิป'})

    try:
        # --- เพิ่มเข้ามา: แปลง hours (string) เป็น float ---
        try:
            hours_float = float(hours)
        except ValueError:
            return jsonify({'status': 'error', 'message': 'รูปแบบเวลาไม่ถูกต้อง'}), 400

        room = ROOM_DATA.get(room_id)
        
        # --- เปลี่ยน hours เป็น hours_float ---
        original_price = room['prices'].get(hours_float)
        if original_price is None:
            return jsonify({'status': 'error', 'message': 'แพ็กเกจราคาไม่ถูกต้อง'})
        
        promo_code = request.args.get('promo', None)
        discount_percent = PROMO_CODES.get(promo_code, 0)
        final_price = original_price - round((original_price * discount_percent) / 100)

        filename = secure_filename(f"{room_id}_{int(time.time())}_{file.filename}")
        slip_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(slip_path)
        
        verification_result = verify_slip_with_slipok(slip_path, expected_amount=final_price, expected_receiver_account=PROMPT_PAY_ID)
        
        if verification_result.get('status') == 'approved':
            # --- เปลี่ยน hours เป็น hours_float ---
            duration_seconds = hours_float * 3600
            
            if room['status'] == 'occupied' and room.get('end_time'):
                # --- เปลี่ยน hours เป็น hours_float ---
                print(f"Extending time for room {room_id} by {hours_float} hour(s).")
                if ACTIVE_TIMERS.get(room_id):
                    ACTIVE_TIMERS[room_id].cancel()
                
                new_end_time = room['end_time'] + duration_seconds
                room['end_time'] = new_end_time
                total_remaining_seconds = new_end_time - time.time()
                message = f'ต่อเวลาสำเร็จ! ใช้งานห้อง {room["name"]} ต่อได้เลย'
            else:
                # --- เปลี่ยน hours เป็น hours_float ---
                print(f"Session started for {room_id} for {hours_float} hour(s).")
                control_tv_power(room_id)
                room['status'] = 'occupied'
                room['end_time'] = time.time() + duration_seconds
                total_remaining_seconds = duration_seconds
                message = f'ชำระเงินสำเร็จ! เริ่มใช้งานห้อง {room["name"]} ได้เลย'
                
            new_timer = threading.Timer(total_remaining_seconds, turn_off_tv_session, args=[room_id])
            new_timer.start()
            ACTIVE_TIMERS[room_id] = new_timer
            return jsonify({'status': 'success', 'message': message})
        else:
            error_msg = verification_result.get('message', 'การตรวจสอบสลิปไม่สำเร็จ')
            return jsonify({'status': 'error', 'message': error_msg})
    except Exception as e:
        print(f"An exception occurred during slip upload: {e}")
        return jsonify({'status': 'error', 'message': 'เกิดข้อผิดพลาดในการประมวลผลไฟล์'})
# -------------------------------------------------------------
# --- จบจุดที่ 2 ---
# -------------------------------------------------------------

# --- ส่วนสำหรับรันแอปพลิเคชัน ---
if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    port = os.getenv('PORT', 5000)
    app.run(host='0.0.0.0', port=int(port), debug=False)
