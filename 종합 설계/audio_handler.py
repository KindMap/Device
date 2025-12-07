# audio_handler.py

import pyaudio
import wave
import os
import subprocess

# 녹음 설정 (16kHz, 모노, 16비트) - 문서 권장 사항 반영
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

def play_sound(file_path):
    """
    MP3 또는 WAV 오디오 파일을 재생함.
    파이썬 3.13 호환성을 위해 pydub 대신 시스템의 ffplay를 직접 사용함.
    """
    if not os.path.exists(file_path):
        print(f"[Audio] 오류: 파일을 찾을 수 없음 ({file_path})")
        return

    try:
        print(f"[Audio] '{file_path}' 재생 중...")
        
        # ffmpeg의 재생 도구인 ffplay를 사용하여 재생
        # -nodisp: 화면 창 띄우지 않음
        # -autoexit: 재생 끝나면 자동 종료
        # -hide_banner: 불필요한 정보 출력 숨김
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", "-hide_banner", file_path],
            stdout=subprocess.DEVNULL,  # 출력 내용을 화면에 보이지 않게 함
            stderr=subprocess.DEVNULL
        )
        
        print(f"[Audio] 재생 완료.")
    except Exception as e:
        print(f"[Audio] 오류: 오디오 파일 재생 실패 ({file_path})")
        print(f"    {e}")
        print("    (sudo apt-get install ffmpeg 명령어로 설치 확인 필요)")

def record_audio(output_filename, duration):
    """
    지정된 시간(초) 동안 USB 마이크에서 오디오를 녹음하여 WAV 파일로 저장함.
    """
    audio = pyaudio.PyAudio()
    
    try:
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)
        
        print(f"[Audio] {duration}초간 녹음을 시작함...")
        frames = []
        for _ in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        print("[Audio] 녹음 완료.")
        
    except IOError as e:
        print(f"[Audio] 오류: 마이크를 찾을 수 없거나 열 수 없음.")
        print(f"    {e} (USB 마이크가 연결되어 있는지 확인)")
        return
    finally:
        if 'stream' in locals() and stream.is_active():
            stream.stop_stream()
            stream.close()
        audio.terminate()

    # 녹음된 데이터를 .wav 파일로 저장
    try:
        wf = wave.open(output_filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        print(f"[Audio] '{output_filename}'에 저장 완료.")
    except Exception as e:
        print(f"[Audio] 오류: WAV 파일 저장 실패 - {e}")
