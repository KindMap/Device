# websocket_client.py
import websocket
import json
import base64
import config
import time

# 전역 변수
ws_app = None
payload_to_send = None
final_result_text = None

def send_data_and_receive_guide(origin_path, dest_path, gps_data):
    global payload_to_send, final_result_text
    final_result_text = None
    
    # 1. 음성 파일 읽기
    try:
        with open(origin_path, "rb") as f:
            origin_b64 = base64.b64encode(f.read()).decode('utf-8')
        with open(dest_path, "rb") as f:
            dest_b64 = base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"[WS] 파일 읽기 실패: {e}")
        return None

    # 2. 전송할 데이터 패킷 준비
    # [수정] 서버가 인식하는 'start_navigation' 타입으로 변경
    payload_to_send = {
        "type": "start_navigation", 
        "gps": gps_data,
        "origin": origin_b64, # audio_origin -> origin으로 변경
        "destination": dest_b64, # audio_destination -> destination으로 변경
        "disability_type": "PHY"
    }

    # 3. 이벤트 핸들러
    def on_message(ws, message):
        global final_result_text
        print(f"[WS] 메시지 수신: {message[:200]}...") # 로그 확인용
        
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            # [Case 1] 연결 성공 메시지 확인
            if msg_type == "connected":
                user_id = data.get("user_id") or data.get("device_id")
                print(f"[WS] 서버 연결 확립! (ID: {user_id})")
                print("[WS] 데이터(음성/GPS) 전송 시작...")
                ws.send(json.dumps(payload_to_send)) # 데이터 전송
                return

            # [Case 2] 경로 안내 수신
            # (서버가 보내주는 타입이 'guidance'인지 'path'인지 확인 필요. 일단 guidance 유지)
            if msg_type == "guidance":
                 text = data.get('text') or data.get('message')
                 print(f"[WS] 안내 수신 완료: {text}")
                 final_result_text = text
                 ws.close()
            
            # [Case 3] 단순 메시지 또는 에러
            elif "message" in data and msg_type != "connected":
                 print(f"[WS] 서버 메시지: {data['message']}")
                 if data.get('status') == 'error':
                     ws.close()
                 # 안내 문구일 수도 있으므로 저장 시도
                 elif not final_result_text:
                     final_result_text = data['message']

        except Exception as e:
            print(f"[WS] 파싱 오류: {e}")

    def on_error(ws, error):
        print(f"[WS] 오류: {error}")

    def on_close(ws, close_status_code, close_msg):
        print("[WS] 연결 종료")

    def on_open(ws):
        print("[WS] 서버 접속 시도...")

    # 4. 실행
    ws_url = config.SERVER_WS_URL 
    ws_app = websocket.WebSocketApp(ws_url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws_app.run_forever()
    return final_result_text