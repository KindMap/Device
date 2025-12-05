# tts_handler.py
from gtts import gTTS
import os
import audio_handler

def speak_text(text):
    """
    텍스트를 입력받아 구글 TTS로 음성 파일(mp3)을 만들고 재생함.
    """
    try:
        print(f"[TTS] 음성 변환 중: '{text}'")
        
        # 1. 텍스트를 mp3 파일로 변환 (한국어)
        tts = gTTS(text=text, lang='ko')
        filename = "guidance.mp3"
        tts.save(filename)
        
        # 2. 저장된 파일 재생 (기존 audio_handler의 재생 기능 활용)
        audio_handler.play_sound(filename)
        
        # 3. 재생 후 파일 삭제 (깔끔하게 정리)
        if os.path.exists(filename):
            os.remove(filename)
            
    except Exception as e:
        print(f"[TTS] 오류 발생: {e}")