# api_client.py
import requests
import config
import json # json 라이브러리 import

def send_navigation_request(origin_file, destination_file, gps_data):
    """
    서버에 음성 파일과 GPS 데이터를 전송하고 경로 응답을 받음.
    
    :param origin_file: 출발지 음성 파일 경로 (str)
    :param destination_file: 도착지 음성 파일 경로 (str)
    :param gps_data: GPS 좌표 (dict, e.g., {'latitude': 37.5, 'longitude': 126.9})
    :return: 서버 응답 (dict)
    """
    try:
        # 서버 URL
        url = config.SERVER_API_URL

        # 보낼 파일 준비 (멀티파트 폼 데이터)
        # 서버에서 받을 때의 키 값('origin_audio', 'destination_audio')은
        # 서버 개발자와 일치해야 함
        files = {
            # 'origin_audio'와 'destination_audio'는 서버 API 명세서와 일치해야 함
            'origin_audio': (origin_file, open(origin_file, 'rb'), 'audio/wav'),
            'destination_audio': (destination_file, open(destination_file, 'rb'), 'audio/wav')
        }

        # JSON으로 보낼 데이터 (GPS 등)
        # 서버 API 명세서에 따라 'data' 필드에 GPS 정보를 포함시킴
        # 'json.dumps'를 사용하여 파이썬 dict를 JSON 문자열로 변환
        data = {
            'gps_data': json.dumps(gps_data) 
            # 'user_id': 'test_user_01' # 필요시 사용자 ID도 추가
        }

        print(f"[API] 서버로 요청 전송: {url}")
        
        # requests 라이브러리를 사용해 POST 요청
        # files 매개변수로 음성 파일을, data 매개변수로 GPS 데이터를 전송
        response = requests.post(url, files=files, data=data)

        # HTTP 응답 코드 확인
        if response.status_code == 200 or response.status_code == 201:
            print("[API] 서버 응답 수신 성공")
            # 서버가 JSON을 반환한다고 가정함
            return response.json()
        else:
            print(f"[API] 서버 오류: HTTP {response.status_code}")
            print(f"[API] 응답 내용: {response.text}")
            return {"status": "error", "message": f"서버 오류: {response.status_code}"}

    except requests.exceptions.ConnectionError as e:
        print(f"[API] 서버 연결 실패: {e}")
        return {"status": "error", "message": "서버에 연결할 수 없음."}
    except Exception as e:
        print(f"[API] 요청 중 예외 발생: {e}")
        return {"status": "error", "message": f"알 수 없는 오류: {e}"}

