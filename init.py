from configures.driver import get_driver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
from ppadb.client import Client as AdbClient
from selenium.webdriver.common.keys import Keys

import os
import subprocess

FILE_NAME = datetime.now().strftime("%Y%m%d%H%M%S") + '.mp4'
DEVICE_RECORD_FILE = '/sdcard/Recordings/' + FILE_NAME
SUFFIX = "org.isoron.uhabits"  # element
PULL_LOCAL_PATH = '%s/' % os.getcwd() + 'record/'
PULL_LOCAL_FILE = PULL_LOCAL_PATH + FILE_NAME
# 녹화 파일 디렉토리 존재하지 않으면 디렉토리 생성
if not os.path.exists(PULL_LOCAL_PATH):
    os.mkdir(PULL_LOCAL_PATH)
    print(PULL_LOCAL_PATH)


def find_by(by_val, dest, need_suffixs):
    by = {"ID": By.ID, "XPATH": By.XPATH, "CLASS": By.CLASS_NAME}
    by_type = by.get(by_val)

    # if need_suffixs is True:
        # dest = SUFFIX + dest

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((by_type, dest)))
    element = driver.find_element(by_type, dest)
    return element


def input_textbox(element, text):
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(element))
    element.set_text(text)
    return 0

def set_alarm(hour, min, ampm, save_or_not):
    find_by("ID", "reminderTimePicker", True).click()
    print(driver.find_elements(MobileBy.ANDROID_UIAUTOMATOR, value='new UiSelector().xPath("//android.widget.FrameLayout[@content-desc="Hours circular slider: 8"]/android.view.View[4]")'))
    find_by("ID", "hours", True).send_keys(Keys.NUMPAD1)

    print(find_by("ID", "minutes", True).get_attribute("text"))

    if ampm == "PM":
        find_by("XPATH", "//*[@resource-id='org.isoron.uhabits:id/ampm_hitspace']", True).click()
    if save_or_not == True:
        find_by("ID", "done_button", True).click()
    else:
        find_by("ID", "clear_button", True).click()

    return 0


def set_frequency(fre, value):
    """
      1. fre 기준 리스트 추출
      2. 빈도 버튼 클릭
      3. 주기, 값 설정
      4. 저장
    """
    frequency = {
        "DAY": ["everyXDaysRadioButton", "everyXDaysTextView"],
        "WEEK": ["xTimesPerWeekRadioButton", "xTimesPerWeekTextView"],
        "MONTH": ["xTimesPerMonthRadioButton", "xTimesPerMonthTextView"]
    }
    # 구분 별 ID 가져오고, 선택 및 입력 후 저장 버튼 클릭
    list_of_fqcy = frequency.get(fre)
    print(list_of_fqcy[0], list_of_fqcy[1])

    find_by("ID", "boolean_frequency_picker", True).click()
    find_by("ID", list_of_fqcy[0], True).click()
    input_textbox(find_by("ID", list_of_fqcy[1], True), value)
    find_by("ID", "button1", False).click()


# Device Remote 시작
driver = get_driver()

# 디바이스 녹화 준비 - record.py move 예정
try:
    client = AdbClient(host='0.0.0.0', port=5037)
    device = client.devices()[0]
except Exception as e:
    print(e)
    exit(1)

# 다바이스 녹화 명령 실행
cmd = f"adb shell screenrecord --bit-rate 8000000 " + DEVICE_RECORD_FILE
process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)

# 최초 앱 실행시 가이드 팝업을 닫음
for i in range(2):
    find_by("ID", "next", True).click()
find_by("ID", "done", True).click()

# + 버튼 클릭
find_by("ID", "actionCreateHabit", True).click()
find_by("ID", "buttonYesNo", True).click()
#
# # 제목 입력
# input_textbox(find_by("ID", "nameInput", True), "테스트 진행 여부 확인")
#
# # 색상 설정 클릭
# for i in range(20):
#     find_by("ID", "colorButton", True).click()
#     find_by("XPATH", '//android.widget.FrameLayout[@content-desc="Color ' + str(i + 1) + '"]', False).click()
#
# # 질문 입력
# input_textbox(find_by("ID", "questionInput", True), "오늘 할당된 테스트를 모두 완료했나요?")
#
# # 프리퀀시 설정
# frequency_arr = ["DAY", "WEEK", "MONTH"]
# for val in frequency_arr:
#     set_frequency(val, 1)

# 알람 설정
set_alarm(12, 50, "PM", True)
# 메모 입력
input_textbox(find_by("ID", "notesInput", True), "테스트 메모")

# 정의한 습관 저장
save_all_btn = find_by("ID", "buttonSave", True).click()

# 녹화 종료 및 mp4 파일 추출
process.send_signal(subprocess.signal.SIGINT)
cmd = f"adb pull {DEVICE_RECORD_FILE} {PULL_LOCAL_FILE}"
subprocess.call(cmd.split())

# mp4로 변환
FFMPEG_CMD = f"ffmpeg -y -i {PULL_LOCAL_FILE} -c copy {PULL_LOCAL_FILE}"
subprocess.call(FFMPEG_CMD.split())
