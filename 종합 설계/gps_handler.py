# gps_handler.py

import serial
import pynmea2
import time

# SIM7600G-H HAT 모듈은 보통 /dev/ttyS0 (GPIO) 또는 /dev/ttyUSBx (USB) 포트를 사용함.
# `ls /dev/tty*` 명령어로 포트를 확인하고 수정해야 할 수 있음.
SERIAL_PORT = "/dev/ttyS0"  # 라즈베리파이 3/4의 GPIO 시리얼 포트
BAUDRATE = 115200

def get_current_location(timeout=30):
    """
    GPS 모듈에서 현재 위치(위도, 경도)를 가져옴.
    타임아웃(초) 내에 유효한 신호를 찾지 못하면 None을 반환함.
    """
    print(f"[GPS] {SERIAL_PORT}에서 GPS 신호를 찾음... (최대 {timeout}초)")
    
    try:
        # 시리얼 포트 열기
        ser = serial.Serial(SERIAL_PORT, baudrate=BAUDRATE, timeout=1)
    except serial.SerialException as e:
        print(f"[GPS] 오류: 시리얼 포트({SERIAL_PORT})를 열 수 없음.")
        print(f"    {e}")
        print("    1. `sudo raspi-config` -> 3 Interface Options -> P6 Serial Port 에서")
        print("       'login shell'은 <No>, 'serial port hardware'는 <Yes>로 설정했는지 확인.")
        print("    2. SERIAL_PORT 변수가 올바른지 확인 (예: /dev/ttyUSB2)")
        return None

    start_time = time.time()
    
    try:
        while time.time() - start_time < timeout:
            # 시리얼 포트에서 한 줄 읽기
            line = ser.readline().decode('ascii', errors='replace').strip()
            
            # $GPRMC 또는 $GPGGA NMEA 문장인지 확인
            if line.startswith(('$GPRMC', '$GPGGA')):
                try:
                    msg = pynmea2.parse(line)
                    
                    # $GPRMC 문장이고 상태가 'A'(Active)인 경우
                    if isinstance(msg, pynmea2.RMC) and msg.status == 'A':
                        print(f"[GPS] RMC 신호 수신 성공: {msg.latitude}, {msg.longitude}")
                        ser.close()
                        return {"latitude": msg.latitude, "longitude": msg.longitude}
                        
                    # $GPGGA 문장이고 GPS 품질이 0(Fix 없음)보다 큰 경우
                    if isinstance(msg, pynmea2.GGA) and msg.gps_qual > 0:
                        print(f"[GPS] GGA 신호 수신 성공: {msg.latitude}, {msg.longitude}")
                        ser.close()
                        return {"latitude": msg.latitude, "longitude": msg.longitude}
                        
                except pynmea2.ParseError:
                    # 문장 파싱 실패 시 (불완전한 데이터 등), 무시하고 다음 줄 읽기
                    continue
                    
        print(f"[GPS] 오류: {timeout}초 내에 유효한 GPS 신호(Fix)를 찾지 못함.")
        ser.close()
        return None
        
    except Exception as e:
        print(f"[GPS] 데이터 읽기 중 오류 발생: {e}")
        if ser.is_open:
            ser.close()
        return None

