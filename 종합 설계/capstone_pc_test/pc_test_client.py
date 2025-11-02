import api_client
import config
import time

# --- 하드웨어 모의(Mocking) 데이터 ---

# 1. GPS 모의: 실제 GPS 모듈 대신 고정된 좌표를 사용함
mock_gps_data = {
    "latitude": 37.5665,  # 서울시청 근처 위도
    "longitude": 126.9780 # 서울시청 근처 경도
}

# 2. 음성 파일 모의: 실제 녹음 대신, 미리 녹음해둔 파일을 사용함
mock_origin_file = "test_origin.wav"
mock_destination_file = "test_destination.wav"

# 3. 버튼 누르기 모의: GPIO 버튼 대신 키보드 'Enter' 키를 사용함
print("--- 서버 연동 모의 테스트 ---")
input("테스트를 시작하려면 Enter 키를 누르세요 (버튼을 누른 척)...")

# --- 메인 로직 실행 (main.py의 핵심 기능만 가져옴) ---

try:
    print(f"'{mock_origin_file}'과 '{mock_destination_file}' 파일을 서버로 전송합니다.")
    print(f"모의 GPS 위치: {mock_gps_data}")

    # 3. 서버로 데이터 전송 (api_client.py의 실제 함수 호출)
    response_data = api_client.send_navigation_request(
        mock_origin_file,
        mock_destination_file,
        mock_gps_data
    )

    # 4. 서버 응답 확인
    print("\n--- 서버로부터 응답 수신 성공! ---")
    print(response_data)

    if response_data.get('status') == 'success':
        print("\n[테스트 성공]")
        print("서버가 경로 탐색에 성공했으며, 아래의 음성 파일 목록을 보내왔습니다:")
        for step_url in response_data.get('steps', []):
            print(f" - {step_url}")
    else:
        print(f"\n[테스트 실패]")
        print(f"서버가 오류를 반환했습니다: {response_data.get('message')}")

except Exception as e:
    print(f"\n--- 서버 통신 중 오류 발생! ---")
    print(f"오류 내용: {e}")
    print("1. 서버 팀원에게 서버가 켜져 있는지 확인하세요.")
    print(f"2. config.py의 서버 주소({config.SERVER_API_URL})가 맞는지 확인하세요.")
