# audio_handler.py

import pyaudio
import wave
from pydub import AudioSegment
from pydub.playback import play

# 녹음 설정 (16kHz, 모노, 16비트)
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # 음성 인식(STT)에 표준적으로 사용되는 샘플링 레이트임.
CHUNK = 1024

def play_sound(file_path):
    """
    MP3 또는 WAV 오디오 파일을 재생함.
    """
    try:
        print(f"[Audio] '{file_path}' 재생 시작...")
        sound = AudioSegment.from_file(file_path)
        play(sound)
        print(f"[Audio] '{file_path}' 재생 완료.")
    except Exception as e:
        print(f"[Audio] 오류: 오디오 파일 재생 실패 ({file_path})")
        print(f"    {e}")
        print("    (ffmpeg/ffprobe가 설치되었는지 확인)")

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
        # 스트림과 PyAudio 객체를 항상 닫아줌.
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

