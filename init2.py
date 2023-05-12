import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
from appium.webdriver.common.touch_action import TouchAction
from PIL import Image

import os
import io
import base64
import random
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

def scroll_down(element):
    x_start, y_start, x_end, y_end = extract_coordinates(str(element.get_attribute("bounds")))

    x = (x_start + x_end) // 2
    y = (y_start + y_end) // 2

    touch_action = TouchAction(driver)
    tab_element(element)
    touch_action.long_press(element).move_to(0, random.randint(1, 99)).release().perform()

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
        print("[Element 존재 검증] - FAIL ", dest, " -> 존재하지 않습니다.")
    else:
        print("[Element 존재 검증] - PASS ", dest, " -> 존재합니다")

    return element

def input_textbox(element: object, text: str):
    """
    Set the textbox with given text
    :param element: target, it must be text box element
    :param text: text box will be set from this given text
    """
    WebDriverWait(driver, 10).until(ec.element_to_be_clickable(element))
    element.send_keys(text)

    if not element.get_attribute("text") == str(text):
        print("   ㄴ[INPUT 검증] - FAIL \"", text, "\" -> 화면에 반영 되지 않았습니다.")
    else:
        print("   ㄴ[INPUT 검증] - PASS \"", text, "\" -> 화면에 정상 반영 되었습니다.")

    return text


def extract_rgb(element):
    size = element.size
    location = element.location

    screenshot = driver.get_screenshot_as_png()
    image = Image.open(io.BytesIO(screenshot))
    color = image.getpixel((location['x'] + size['width'] / 2, location['y'] + size['height'] / 2))

    return [color[0], color[1], color[2]]


def set_alarm(ampm: str, save_or_not: bool):
    """
    Set the alarm with given params. time is always 8:00 fixed
    :param ampm:
    :param save_or_not:
    :return:
    """
    button = find_element("ID", "reminderTimePicker", False)
    button.click()

    if ampm == "PM":
        find_element("XPATH", "//*[@resource-id='org.isoron.uhabits:id/ampm_hitspace']", False).click()
    if save_or_not:
        find_element("ID", "done_button", False).click()
    else:
        find_element("ID", "clear_button", False).click()

    WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, "reminderTimePicker")))
    set_time = button.get_attribute("text")

    return set_time


def set_frequency(fre: str, type: str, value: int):
    """
    1. Extract frequency list
    2. Click the Frequency button
    3. set Frequency, and set value
    4. Save
    :param fre: standard of frequency
    :param value: input value of element
    """
    button_diff = {"buttonYesNo": "boolean_frequency_picker", "buttonMeasurable": "numericalFrequencyPicker"}

    button = find_element("ID", button_diff.get(type), False)

    button.click()

    if type == "buttonMeasurable":
        if fre == "DAY":
            find_element("XPATH", "//*[@text='매일']", False).click()
        elif fre == "WEEK":
            find_element("XPATH", "//*[@text='매주']", False).click()
        elif fre == "MONTH":
            find_element("XPATH", "//*[@text='매월']", False).click()

    elif type == "buttonYesNo":
        frequency = {
            "DAY": ["everyXDaysRadioButton", "everyXDaysTextView", "일 마다"],
            "WEEK": ["xTimesPerWeekRadioButton", "xTimesPerWeekTextView", " times per week"],
            "MONTH": ["xTimesPerMonthRadioButton", "xTimesPerMonthTextView", " times per month"]
        }
        list = frequency.get(fre)

        find_element("ID", list[0], False).click()
        input_textbox(find_element("ID", list[1], False), value)
        find_element("ID", "android:id/button1", False).click()

    # 검증
    if value == 1 or type == "buttonMeasurable":
        if fre == "DAY":
            value = "매일"
        elif fre == "WEEK":
            value = "매주"
        elif fre == "MONTH":
            value = "매월"
    else:
        value = str(value) + list[2]

    WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, button_diff.get(type))))
    if not button.get_attribute("text") == value:
        print("   ㄴ[빈도 설정] - FAIL \"", value, "\" -> 설정 값으로 반영 되지 않았습니다.")
    else:
        print("   ㄴ[빈도 설정] - PASS \"", value, "\" -> 설정 값으로 반영 되었습니다.")

    return str(fre + " : " + str(value))


def save_habit(type: str):
    """

    :param type: "buttonYesNo", "buttonMeasurable"
    :return:
    """
    # 입력값 저장
    list = []

    # 타입에 따라 습관 등록 버튼 클릭
    find_element("ID", "actionCreateHabit", False).click()
    find_element("ID", type, False).click()

    # 각 타입의 공통된 Parameter
    # 제목 입력 및 저장
    list.append(input_textbox(find_element("ID", "nameInput", False), lorem.words(3)))

    # 컬러 선택 및 RGB 비교 검증
    color_btn = find_element("ID", "colorButton", False)
    color_btn.click()
    random_idx = random.randint(1, 20)
    find_element("XPATH", '//android.widget.FrameLayout[@content-desc="Color ' + str(random_idx) + '"]', False).click()
    color1 = extract_rgb(color_btn)
    color_btn.click()
    picked_color = find_element("XPATH",
                                '//android.widget.FrameLayout[@content-desc="Color ' + str(random_idx) + ' selected"]',
                                False)

    if picked_color is not None:
        picked_color.click()
        color2 = extract_rgb(find_element("ID", "colorButton", False))
        if not color1 == color2:
            print("   ㄴ[컬러 설정] - FAIL ", str(random_idx), " -> 설정 값으로 반영 되지 않았습니다.")
        else:
            print("   ㄴ[컬러 설정] - PASS ", str(random_idx), " -> 설정 값으로 반영 되었습니다.")

    # 반영된 색 저장
    list.append(color2)

    # 질문 입력 및 저장
    list.append(input_textbox(find_element("ID", "questionInput", False), lorem.words(3)))

    # 빈도 설정
    list.append(set_frequency("DAY", type, random.randint(1, 10)))

    # 알림 설정 및 결과 저장
    am_or_pm = ["AM", "PM"]
    list.append(set_alarm(am_or_pm[random.randint(0, 1)], True))

    # 메모 입력 및 저장
    list.append(input_textbox(find_element("ID", "notesInput", False), lorem.words(3)))

    if type == "buttonMeasurable":
        list.append(input_textbox(find_element("ID", "unitInput", False), lorem.words(1)))
        list.append(input_textbox(find_element("ID", "targetInput", False), random.randint(1, 15)))

    # 정의한 습관 저장
    find_element("ID", "buttonSave", False).click()

    return list


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

# 습관 추가 - 예 아니오 기준
saved_habit_yes_or_no = save_habit("buttonYesNo")
print(saved_habit_yes_or_no)
# 습관 추가 - 측정 가능 기준
saved_habit_measurable = save_habit("buttonMeasurable")
print(saved_habit_measurable)

# 습관 수정 - 임의의 습관
habits = [saved_habit_yes_or_no, saved_habit_measurable]
for habit in habits:
    for i in range(5):
        box = find_element("XPATH",
                           "(//*[@class='android.widget.LinearLayout' and (./preceding-sibling::* | ./following-sibling::*)[@text='" +
                           habit[
                               0] + "'] and ./parent::*[@class='android.widget.LinearLayout'] and (./preceding-sibling::* | ./following-sibling::*)[@class='android.view.View']]/*[@class='android.view.View'])[" + str(
                               i + 1) + "]",
                           False)
        action = TouchAction(driver)
        WebDriverWait(driver, 10).until(ec.element_to_be_clickable(box))
        action.long_press(box).wait(2000).perform()

        if len(habit) > 6:
            scrolls = find_element("XPATH", "//*[@resource-id='android:id/numberpicker_input']", True)
            print(len(scrolls))
            for scroll in scrolls:
                WebDriverWait(driver, 10).until(ec.element_to_be_clickable(scroll))
                scroll.clear()
                scroll.send_keys(str(random.randint(0, 100)))
            find_element("XPATH", "//*[@text='확인']", False).click()
    # 측정 가능값 체크

# 녹화 종료 -> Base64로 디코딩
recording_data = driver.stop_recording_screen()
decoded_data = base64.b64decode(recording_data)

# 비디오 파일로 저장
with open(RECORD_FILE, "wb") as video_file:
    video_file.write(decoded_data)

# Driver Remote 종료
driver.quit()
