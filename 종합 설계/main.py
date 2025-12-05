# main.py
import time
import os
import RPi.GPIO as GPIO
import audio_handler
import gps_handler
import websocket_client
import tts_handler
import config

# 녹음 파일 저장 경로
ORIGIN_WAV = "origin.wav"
DEST_WAV = "destination.wav"

def main_process():
    """버튼이 눌렸을 때 실행되는 전체 시나리오"""
    print("\n[Start] 경로 안내 프로세스 시작")
    
    # 1. 출발지 녹음
    print("[Step 1] 출발지 입력")
    if os.path.exists("sounds/prompt_origin.mp3"):
        audio_handler.play_sound("sounds/prompt_origin.mp3") 
    else:
        print("안내 음성 파일 없음 (건너뜀)")
    
    # 4초간 녹음
    audio_handler.record_audio(ORIGIN_WAV, duration=4)
    
    # 2. 도착지 녹음
    print("[Step 2] 도착지 입력")
    if os.path.exists("sounds/prompt_destination.mp3"):
        audio_handler.play_sound("sounds/prompt_destination.mp3")
    
    audio_handler.record_audio(DEST_WAV, duration=4)
    
    # 3. GPS 수신
    print("[Step 3] GPS 탐색")
    if os.path.exists("sounds/prompt_wait.mp3"):
        audio_handler.play_sound("sounds/prompt_wait.mp3")
    
    # GPS 안테나가 실내라면 오래 걸릴 수 있음 (타임아웃 60초)
    gps_data = gps_handler.get_current_location(timeout=60)
    
    if not gps_data:
        print("[Error] GPS 수신 실패")
        tts_handler.speak_text("위성 신호를 잡을 수 없습니다. 실외로 이동해주세요.")
        return

    # 4. 서버 전송 및 안내 수신
    print("[Step 4] 서버 통신")
    # 녹음 파일과 GPS를 보내고, 안내 멘트(텍스트)를 받아옴
    guide_text = websocket_client.send_data_and_receive_guide(ORIGIN_WAV, DEST_WAV, gps_data)
    
    # 5. 결과 안내 (TTS)
    if guide_text:
        print(f"[Result] 안내: {guide_text}")
        # 받아온 텍스트를 음성으로 읽어줌
        tts_handler.speak_text(guide_text)
    else:
        print("[Error] 서버 응답 없음")
        tts_handler.speak_text("서버와 연결할 수 없습니다. 다시 시도해주세요.")

def on_button_press(channel):
    """버튼이 눌렸을 때 호출되는 함수"""
    # 중복 실행 방지를 위해 잠시 이벤트 감지 중지
    try:
        GPIO.remove_event_detect(config.BUTTON_PIN)
        main_process()
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        # 프로세스가 끝나면 다시 버튼 감지 시작
        setup_gpio()

def setup_gpio():
    """GPIO 초기화 및 이벤트 설정"""
    GPIO.add_event_detect(config.BUTTON_PIN, GPIO.FALLING, 
                          callback=on_button_press, bouncetime=1000)

def main():
    print("--- KindMap 디바이스 대기 중 ---")
    print(f"버튼(GPIO {config.BUTTON_PIN})을 눌러주세요.")
    
    # 시작음 재생
    if os.path.exists("sounds/prompt_start.mp3"):
        audio_handler.play_sound("sounds/prompt_start.mp3")
    
    # GPIO 설정
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    setup_gpio()
    
    try:
        # 프로그램이 종료되지 않도록 무한 대기
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n종료합니다.")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
