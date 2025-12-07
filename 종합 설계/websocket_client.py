# websocket_client.py
import websocket
import json
import base64
import config
import time
import uuid
import os
import threading
import ssl

# 전역 변수
ws_app = None
payload_to_send = None
final_result_text = None
device_uuid = None

def get_or_create_device_uuid():
    """디바이스 UUID 로드 또는 생성"""
    uuid_file = "device_uuid.txt"
    if os.path.exists(uuid_file):
        with open(uuid_file, 'r') as f:
            return f.read().strip()
    else:
        new_uuid = str(uuid.uuid4())
        with open(uuid_file, 'w') as f:
            f.write(new_uuid)
        return new_uuid

def send_data_and_receive_guide(origin_path, dest_path, gps_data): # dest_path는 사용하지 않음 (단일 파일 전송)
    global payload_to_send, final_result_text, device_uuid
    final_result_text = None
    
    # UUID 가져오기
    device_uuid = get_or_create_device_uuid()
    user_id = f"temp_{device_uuid}"

    # 1. 음성 파일 읽기
    try:
        with open(origin_path, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"[WS] 파일 읽기 실패: {e}")
        return None

    # 2. 전송할 데이터 패킷 준비 (API 문서 'voice_input' 참조)
    payload_to_send = {
        "type": "voice_input",
        "audio_data": audio_base64,
        "audio_format": "wav", 
        "sample_rate": 16000
    }

    # 3. 이벤트 핸들러
    def on_message(ws, message):
        global final_result_text
        print(f"[WS] 메시지 수신: {message[:200]}...") 
        
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "transcription_started":
                print(f"[WS] {data.get('message', '음성 인식 중...')}")

            elif msg_type == "transcription_complete":
                text = data.get('transcribed_text')
                conf = data.get('confidence')
                print(f"[WS] 인식 완료: '{text}' (신뢰도: {conf})")

            elif msg_type == "stations_recognized":
                origin = data.get('origin')
                dest = data.get('destination')
                print(f"[WS] 역 인식: 출발-{origin}, 도착-{dest}")

            elif msg_type == "route_calculated":
                # 경로 계산 완료!
                routes = data.get('routes', [])
                if routes:
                    # 첫 번째 경로의 주요 정보 추출 (예시)
                    best_route = routes[0]
                    total_time = best_route.get('total_time')
                    transfer_count = best_route.get('transfer_count')
                    
                    # 안내 멘트 구성
                    final_result_text = f"경로를 찾았습니다. 예상 소요 시간은 {total_time}분이며, 환승은 {transfer_count}회입니다."
                    print(f"[WS] 경로 안내 준비 완료: {final_result_text}")
                else:
                    final_result_text = "경로를 찾을 수 없습니다."
                
                ws.close() # 연결 종료

            elif msg_type == "error":
                print(f"[WS] 에러 발생: {data.get('message')}")
                final_result_text = f"오류가 발생했습니다. {data.get('message')}"
                ws.close()

        except Exception as e:
            print(f"[WS] 파싱 오류: {e}")

    def on_error(ws, error):
        print(f"[WS] 오류: {error}")

    def on_close(ws, close_status_code, close_msg):
        print("[WS] 연결 종료")

    def on_open(ws):
        print("[WS] 서버 접속 성공. 음성 데이터 전송...")
        ws.send(json.dumps(payload_to_send))
        
        # Ping 전송 스레드 시작 (연결 유지)
        def run_ping():
            while ws.sock and ws.sock.connected:
                time.sleep(30)
                try:
                    ws.send(json.dumps({"type": "ping"}))
                    print("[WS] Ping 전송")
                except:
                    break
        threading.Thread(target=run_ping, daemon=True).start()

    # 4. 실행
    # 주소 형식: ws://<host>:<port>/api/v1/ws/{user_id}
    ws_url = f"{config.SERVER_WS_BASE_URL}/{user_id}"
    
    ws_app = websocket.WebSocketApp(ws_url,
                                    on_open=on_open,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
    
    # SSL 인증서 문제 방지를 위해 옵션 추가
    ws_app.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    return final_result_text
