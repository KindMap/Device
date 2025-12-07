# tts_handler.py
from gtts import gTTS
import os
import audio_handler

def speak_text(text):
    """
    서버로부터 받은 텍스트를 음성 파일(mp3)로 변환하고 재생함.
    """
    try:
        print(f"[TTS] 음성 변환 중: '{text}'")
        
        # 1. 구글 TTS로 텍스트를 음성 파일로 저장 (한국어)
        tts = gTTS(text=text, lang='ko')
        filename = "guidance.mp3"
        tts.save(filename)
        
        # 2. 저장된 파일 재생 (기존 audio_handler 활용)
        audio_handler.play_sound(filename)
        
        # 3. 재생 후 파일 삭제 (선택 사항)
        if os.path.exists(filename):
            os.remove(filename)
            
    except Exception as e:
        print(f"[TTS] 오류 발생: {e}")
