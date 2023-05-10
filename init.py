from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
from appium.webdriver.common.touch_action import TouchAction

import os
import base64
import configs.driver
import utility.lorem as lorem

def extract_coordinates(bounds: str) -> tuple:
    """
    extract
    :param bounds:
    :return:
    """
    coords = bounds.replace("][", ",").strip("[]").split(",")
    x_start, y_start, x_end, y_end = map(int, coords)

    return x_start, y_start, x_end, y_end


def tab_element(element):
    """
    Do 'DEVICE TAB' from Element's bounds
    :param element: Target of DEVICE TAB
    """
    x_start, y_start, x_end, y_end = extract_coordinates(str(element.get_attribute("bounds")))

    x = (x_start + x_end) // 2
    y = (y_start + y_end) // 2

    touch_action = TouchAction(driver)
    touch_action.tap(None, x, y).perform()


def find_element(by_val: str, dest: str, is_multiple: bool):
    """
    element will presence located, return this element
    :param by_val: By.ID, By.XPATH, By.CLASS ...more
    :param dest: destination of By
    :param is_multiple: for return object OR list
    :return: element
    """
    by = {"ID": By.ID, "XPATH": By.XPATH, "CLASS": By.CLASS_NAME}
    by_type = by.get(by_val)
    WebDriverWait(driver, 10).until(ec.presence_of_element_located((by_type, dest)))

    if is_multiple:
        element = driver.find_elements(by_type, dest)
    else:
        element = driver.find_element(by_type, dest)

    if element is None:
        print("FAIL [Element] " + dest + " : Does Not exists")
    else:
        print("PASS [Element] " + dest + " : Exists")

    return element


def input_textbox(element: object, text: str):
    """
    Set the textbox with given text
    :param element: target, it must be text box element
    :param text: text box will be set from this given text
    """
    WebDriverWait(driver, 10).until(ec.element_to_be_clickable(element))
    element.set_text(text)

    print(element.get_attribute("text"))
    if not element.get_attribute("text") == str(text):
        print("FAIL [Input] Not correct")
    else:
        print("PASS [Input] Correct")


def set_alarm(hour: str, min: str, ampm: str, save_or_not: bool):
    """
    Not developed yet.
    Set the alarm with given params
    :param hour:
    :param min:
    :param ampm:
    :param save_or_not:
    :return:
    """
    find_element("ID", "reminderTimePicker", False).click()
    find_element("ID", "hours", False)
    find_element("ID", "minutes", False)

    if ampm == "PM":
        find_element("XPATH", "//*[@resource-id='org.isoron.uhabits:id/ampm_hitspace']", False).click()
    if save_or_not:
        find_element("ID", "done_button", False).click()
    else:
        find_element("ID", "clear_button", False).click()

    return 0


def set_frequency(fre, value):
    """
    1. Extract frequency list
    2. Click the Frequency button
    3. set Frequency, and set value
    4. Save
    :param fre: standard of frequency
    :param value: input value of element
    """
    frequency = {
        "DAY": ["everyXDaysRadioButton", "everyXDaysTextView", "일 마다"],
        "WEEK": ["xTimesPerWeekRadioButton", "xTimesPerWeekTextView", " times per week"],
        "MONTH": ["xTimesPerMonthRadioButton", "xTimesPerMonthTextView", " times per month"]
    }
    list = frequency.get(fre)

    find_element("ID", "boolean_frequency_picker", False).click()
    find_element("ID", list[0], False).click()
    input_textbox(find_element("ID", list[1], False), value)
    find_element("ID", "android:id/button1", False).click()
    if value == 1:
        if fre == "DAY":
            value = "매일"
        elif fre == "WEEK":
            value = "매주"
        elif fre == "MONTH":
            value = "매월"
    else:
        value = str(value) + list[2]
    if not find_element("ID", "boolean_frequency_picker", False).get_attribute("text") == value:
        print("FAIL [빈도 설정] : Not saved as set")
    else:
        print("PASS [빈도 설정] : Saved as set")


# Device Remote 시작
driver = configs.driver.get_driver()

# 녹화 시작
RECORD_PATH = '%s/' % os.getcwd() + 'record/'
RECORD_FILE = RECORD_PATH + datetime.now().strftime("%Y_%m_%d_%H%M%S") + '.mp4'
driver.start_recording_screen()

# 녹화 파일 Directory 존재 하지 않으면 생성
if not os.path.exists(RECORD_PATH):
    os.mkdir(RECORD_PATH)
    print(RECORD_PATH)

# 최초 앱 실행시 가이드 팝업을 닫음
for i in range(2):
    find_element("ID", "next", False).click()
find_element("ID", "done", False).click()

# 필터 클릭 테스트
for i in range(2):
    find_element("ID", "action_filter", False).click()
    find_element("ID", "checkbox", True)[0].click()
    find_element("ID", "action_filter", False).click()
    find_element("ID", "checkbox", True)[1].click()

# 정렬 오름/내림차순 클릭 테스트
for i in range(5):
    for j in range(2):
        find_element("ID", "action_filter", False).click()
        find_element("ID", "submenuarrow", False).click()
        find_element("ID", "content", True)[i].click()

# 주간 적용
tab_element(find_element("CLASS", "android.widget.ImageView", False))
find_element("ID", "content", True)[0].click()
# 야간 적용
tab_element(find_element("CLASS", "android.widget.ImageView", False))
find_element("ID", "content", True)[0].click()

# 각 설정 화면 클릭 테스트
for i in range(3):
    tab_element(find_element("CLASS", "android.widget.ImageView", False))
    orderby_arr = find_element("ID", "content", True)[i + 1].click()
    driver.press_keycode(4)

# 습관 등록 테스트 - 예/아니오 기준
find_element("ID", "actionCreateHabit", False).click()
find_element("ID", "buttonYesNo", False).click()

# 제목 입력
input_textbox(find_element("ID", "nameInput", False), lorem.words(3))

# 컬러 적용 검증 테스트
# 기본 컬러 설정 값 index
pre = 12
find_element("ID", "colorButton", False).click()
picked_color = find_element("XPATH", '//android.widget.FrameLayout[@content-desc="Color ' + str(pre) + ' selected"]',
                            False)
if picked_color is not None:
    picked_color.click()
    print("PASS, (* Default)" + str(pre) + "번째 color 선택됨")

# 총 컬러 수 20
for i in range(20):
    pre = i
    if pre != 12:
        find_element("ID", "colorButton", False).click()
        color_element = find_element("XPATH",
                                     '//android.widget.FrameLayout[@content-desc="Color ' + str(i + 1) + '"]',
                                     False).click()
        find_element("ID", "colorButton", False).click()
        picked_color = find_element("XPATH",
                                    '//android.widget.FrameLayout[@content-desc="Color ' + str(pre + 1) + ' selected"]',
                                    False)
        if picked_color is not None:
            picked_color.click()
            print("PASS, " + str(pre + 1) + "번째 color 선택됨")

# 질문 입력
input_textbox(find_element("ID", "questionInput", False), lorem.words(3))

# 빈도 설정
frequency_arr = ["DAY", "WEEK", "MONTH"]
for val in frequency_arr:
    set_frequency(val, 1)

# 알람 설정
# set_alarm(12, 50, "PM", True)
# 메모 입력
input_textbox(find_element("ID", "notesInput", False), lorem.words(3))

# 정의한 습관 저장
find_element("ID", "buttonSave", False).click()

# 녹화 종료 -> Base64로 디코딩
recording_data = driver.stop_recording_screen()
decoded_data = base64.b64decode(recording_data)

# 비디오 파일로 저장
with open(RECORD_FILE, "wb") as video_file:
    video_file.write(decoded_data)

# Driver Remote 종료
driver.quit()