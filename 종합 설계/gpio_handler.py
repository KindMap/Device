# gpio_handler.py

import RPi.GPIO as GPIO
import time

# 버튼을 연결할 GPIO 핀 번호 (BCM 모드 기준)
BUTTON_PIN = 17 

def setup_button(callback_function):
    """
    버튼 핀을 초기화하고, 버튼이 눌렸을 때 실행될 콜백 함수를 등록함.
    """
    try:
        GPIO.setmode(GPIO.BCM)
        # GPIO 17번 핀을 입력으로 설정하고, 내부 풀업 저항을 활성화함.
        # 버튼은 BUTTON_PIN과 GND(접지) 사이에 연결함.
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # 버튼이 눌렸을 때(Falling edge) 콜백 함수를 실행함.
        # bouncetime: 버튼 채터링(떨림)을 방지하기 위한 디바운스 시간 (ms)
        GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, 
                              callback=callback_function, 
                              bouncetime=300)
        
        print(f"[GPIO] {BUTTON_PIN}번 핀에서 버튼 입력을 기다림...")

    except Exception as e:
        print(f"[GPIO] 오류: {e}")
        print("    GPIO 초기화에 실패함. (sudo 권한으로 실행했는지 확인)")
        cleanup()

def cleanup():
    """
    GPIO 리소스를 정리함.
    """
    print("[GPIO] GPIO 리소스를 정리함.")
    GPIO.cleanup()

