from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import glob

# ChromeDriver 경로 설정
chrome_driver_path = 'C:/Users/user/dataintelli/chromedriver-win64/chromedriver.exe'

# 다운로드 폴더 설정
download_dir = os.path.join(os.getcwd(), 'downloads')  # 현재 디렉토리의 downloads 폴더에 저장

# 폴더가 없으면 생성
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Chrome 옵션 설정
chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_dir,  # 다운로드 경로 설정
    "download.prompt_for_download": False,  # 다운로드 대화 상자 비활성화
    "directory_upgrade": True,  # 기존 경로가 있으면 덮어쓰기
    "safebrowsing.enabled": True  # 안전 브라우징 비활성화
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_experimental_option("detach", True)  # 브라우저가 닫히지 않도록 설정

# Chrome 드라이버 초기화
driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)

# 60개의 주소가 담긴 리스트
urls = [
    'https://www.data.go.kr/data/3082300/fileData.do',
    'https://www.data.go.kr/data/15015595/fileData.do',
    'https://www.data.go.kr/data/15021412/fileData.do',
    'https://www.data.go.kr/data/15089543/fileData.do',
    'https://www.data.go.kr/data/3074190/fileData.do',
    'https://www.data.go.kr/data/15006904/fileData.do',
    'https://www.data.go.kr/data/15055413/fileData.do',
    'https://www.data.go.kr/data/15047802/fileData.do',
    'https://www.data.go.kr/data/15026534/fileData.do',
    'https://www.data.go.kr/data/15089521/fileData.do',
    'https://www.data.go.kr/data/15047803/fileData.do',
    'https://www.data.go.kr/data/15028162/fileData.do',
    'https://www.data.go.kr/data/15051484/fileData.do',
    'https://www.data.go.kr/data/15076268/fileData.do',
    'https://www.data.go.kr/data/15039524/fileData.do',
    'https://www.data.go.kr/data/15069435/fileData.do',
    'https://www.data.go.kr/data/3039563/fileData.do',
    'https://www.data.go.kr/data/15108233/fileData.do',
    'https://www.data.go.kr/data/15044214/fileData.do',
    'https://www.data.go.kr/data/15033677/fileData.do',
    'https://www.data.go.kr/data/3077891/fileData.do',
    'https://www.data.go.kr/data/3072529/fileData.do',
    'https://www.data.go.kr/data/15009644/fileData.do',
    'https://www.data.go.kr/data/15054566/fileData.do',
    'https://www.data.go.kr/data/15048937/fileData.do',
    'https://www.data.go.kr/data/15051523/fileData.do',
    'https://www.data.go.kr/data/3048703/fileData.do',
    'https://www.data.go.kr/data/15009664/fileData.do',
    'https://www.data.go.kr/data/15045342/fileData.do',
    'https://www.data.go.kr/data/15078092/fileData.do',
    'https://www.data.go.kr/data/15018868/fileData.do',
    'https://www.data.go.kr/data/3049716/fileData.do',
    'https://www.data.go.kr/data/15051522/fileData.do',
    'https://www.data.go.kr/data/15055561/fileData.do',
    'https://www.data.go.kr/data/3034282/fileData.do',
    'https://www.data.go.kr/data/15089654/fileData.do',
    'https://www.data.go.kr/data/3051416/fileData.do',
    'https://www.data.go.kr/data/15051054/fileData.do',
    'https://www.data.go.kr/data/15055565/fileData.do',
    'https://www.data.go.kr/data/15055564/fileData.do',
    'https://www.data.go.kr/data/15064610/fileData.do',
    'https://www.data.go.kr/data/15064607/fileData.do',
    'https://www.data.go.kr/data/3051418/fileData.do',
    'https://www.data.go.kr/data/15118821/fileData.do',
    'https://www.data.go.kr/data/15105030/fileData.do',
    'https://www.data.go.kr/data/3044320/fileData.do',
    'https://www.data.go.kr/data/15095101/fileData.do',
    'https://www.data.go.kr/data/15123153/fileData.do',
    'https://www.data.go.kr/data/15095104/fileData.do',
    'https://www.data.go.kr/data/3033670/fileData.do'
]

# 다운로드된 파일 앞머리에 번호를 부여하기 위한 카운터
file_counter = 79

for url in urls:
    driver.get(url)

    # 버튼이 렌더링될 때까지 약간 대기
    time.sleep(3)

    # '다운로드' 버튼 찾기
    try:
        download_button = driver.find_element(By.XPATH, '//a[contains(@onclick, "fn_fileDataDown")]')

        # 버튼 클릭
        ActionChains(driver).move_to_element(download_button).click(download_button).perform()

        # Alert 창 처리 (있을 경우)
        try:
            alert = driver.switch_to.alert  # Alert 창으로 전환
            print(f"Alert text: {alert.text}")  # 필요시 알림창 텍스트 확인
            alert.accept()  # Alert의 확인(OK) 버튼을 자동으로 클릭
            print("Alert accepted")
        except:
            print("No alert found")  # Alert이 없으면 넘어감

        # 다운로드가 완료될 시간을 대기
        time.sleep(3)

        # 최근 다운로드된 파일을 찾고 이름 앞에 번호 붙이기
        list_of_files = glob.glob(os.path.join(download_dir, '*'))  # 다운로드 폴더 내 모든 파일 리스트
        latest_file = max(list_of_files, key=os.path.getctime)  # 가장 최근에 다운로드된 파일 찾기
        new_file_name = os.path.join(download_dir, f'{file_counter}_{os.path.basename(latest_file)}')  # 번호 부여한 새 파일명
        os.rename(latest_file, new_file_name)  # 파일 이름 변경
        print(f"File renamed to: {new_file_name}")

        file_counter += 1  # 다음 파일에 붙일 번호 증가

    except Exception as e:
        print(f"Error on {url}: {e}")

# 모든 작업이 완료되면 브라우저 종료
driver.quit()
