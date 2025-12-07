# main.py
import time
import os
import audio_handler
import gps_handler
import websocket_client
import tts_handler
import config
import RPi.GPIO as GPIO 

# 파일 경로 (하나만 사용)
VOICE_INPUT_WAV = "voice_input.wav"

def main_process():
    """버튼이 눌렸을 때 실행되는 전체 시나리오"""
    print("\n[Start] 경로 안내 프로세스 시작")
    
    # 1. 안내 멘트 & 녹음 (한 번에!)
    print("[Step 1] 음성 명령 입력")
    
    # 안내 멘트: "어디서 어디로 가시나요?"
    if os.path.exists("sounds/prompt_voice_input.mp3"):
        audio_handler.play_sound("sounds/prompt_voice_input.mp3") 
    else:
        # 없으면 기본 멘트 사용 (TTS)
        tts_handler.speak_text("어디서 어디로 가시나요? 말씀해주세요.")

    # 5초간 녹음
    print("녹음 시작 (5초)...")
    audio_handler.record_audio(VOICE_INPUT_WAV, duration=5)
    
    # 2. GPS 수신 (옵션 - 문서상 필수는 아니지만 보내면 좋음)
    print("[Step 2] GPS 탐색")
    if os.path.exists("sounds/prompt_wait.mp3"):
        audio_handler.play_sound("sounds/prompt_wait.mp3")
    
    # GPS 안테나가 실내라면 여기서 오래 걸릴 수 있음 (타임아웃 60초)
    gps_data = gps_handler.get_current_location(timeout=60)
    
    if not gps_data:
        print("[Warning] GPS 수신 실패 (기본값 전송 또는 NULL)")
        gps_data = None

    # 3. 서버 전송
    print("[Step 3] 서버 통신")
    # 녹음 파일 하나만 전송 (두 번째 인자는 None)
    guide_text = websocket_client.send_data_and_receive_guide(VOICE_INPUT_WAV, None, gps_data)
    
    # 4. 결과 안내
    if guide_text:
        print(f"[Result] 안내: {guide_text}")
        tts_handler.speak_text(guide_text)
    else:
        print("[Error] 서버 응답 없음")
        tts_handler.speak_text("죄송합니다. 경로를 찾을 수 없습니다.")

def on_button_press(channel):
    """버튼 콜백"""
    # 중복 실행 방지
    try:
        GPIO.remove_event_detect(config.BUTTON_PIN) # 이벤트 잠시 끄기
        main_process()
    except Exception as e:
        print(f"오류: {e}")
    finally:
        # 프로세스 끝나면 다시 버튼 감지 켜기 (재설정)
        try:
            GPIO.add_event_detect(config.BUTTON_PIN, GPIO.FALLING, 
                                  callback=on_button_press, bouncetime=1000)
        except:
            pass

def main():
    print("--- KindMap 디바이스 대기 중 ---")
    print(f"버튼(GPIO {config.BUTTON_PIN})을 눌러주세요.")
    
    # 시작음 재생
    if os.path.exists("sounds/prompt_start.mp3"):
        audio_handler.play_sound("sounds/prompt_start.mp3")
    
    # GPIO 설정
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # 초기 이벤트 설정
    GPIO.add_event_detect(config.BUTTON_PIN, GPIO.FALLING, 
                          callback=on_button_press, bouncetime=1000)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n종료합니다.")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
