# config.py

# API 문서에서 확인한 실제 서버 주소로 변경함
SERVER_API_URL = "http://35.92.117.143:8001/api/v1/routes"

# 라즈베리파이 GPIO 핀 번호 (BCM 모드 기준)
BUTTON_PIN = 17

# GPS 모듈 시리얼 포트
# 라즈베리파이 4B 기준, /dev/ttyS0 또는 /dev/ttyAMA0 일 수 있음
# 또는 USB GPS 모듈인 경우 /dev/ttyUSB0
SERIAL_PORT = "/dev/ttyS0"
BAUD_RATE = 9600

# 안내 음성 파일 경로
SOUNDS_DIR = "sounds/"
SOUND_START = SOUNDS_DIR + "prompt_start.mp3"
SOUND_ORIGIN = SOUNDS_DIR + "prompt_origin.mp3"
SOUND_DESTINATION = SOUNDS_DIR + "prompt_destination.mp3"
SOUND_WAIT = SOUNDS_DIR + "prompt_wait.mp3"
SOUND_ERROR = SOUNDS_DIR + "prompt_error.mp3"
