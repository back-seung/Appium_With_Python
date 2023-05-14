from typing import Optional
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


def find_element(by_val: str, dest: str, is_multiple: bool):
    """
    find element by given parameters.
    :param by_val: value of By
    :param dest: destination
    :param is_multiple: find element is single or multiple
    :return:
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
    send keys into textbox.
    :return: text
    """
    WebDriverWait(driver, 10).until(ec.element_to_be_clickable(element))
    element.clear()
    element.send_keys(text)

    if not element.get_attribute("text") == str(text):
        print("   ㄴ[INPUT 검증] - FAIL \"", text, "\" -> 화면에 반영 되지 않았습니다.")
    else:
        print("   ㄴ[INPUT 검증] - PASS \"", text, "\" -> 화면에 정상 반영 되었습니다.")

    return text


def extract_rgb(element):
    """
    extract R,G,B from given element
    :return: list of RGB
    """
    size = element.size
    location = element.location

    screenshot = driver.get_screenshot_as_png()
    image = Image.open(io.BytesIO(screenshot))
    color = image.getpixel((location['x'] + size['width'] / 2, location['y'] + size['height'] / 2))

    return [color[0], color[1], color[2]]


def tab_device_with_bounds(bounds: str) -> tuple:
    """
    tab the device using with given bounds
    :param bounds: e.g [123,123][12,345]
    """
    coords = bounds.replace("][", ",").strip("[]").split(",")
    x_start, y_start, x_end, y_end = map(int, coords)

    x = (x_start + x_end) // 2
    y = (y_start + y_end) // 2

    touch_action = TouchAction(driver)
    touch_action.tap(None, x, y).perform()


def set_alarm(ampm: str, save_or_not: bool):
    """
    set the alarm. time is fixed at (8:00) because cant handle this.
    :param ampm: save time is AM or PM
    :return: get text attribute from elemenmt
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

    :param fre: "DAY", "WEEK", "MONTH" only
    :param type: yesNo Type or Measurable Type
    :param value: frequency value
    :return: str(fre + " : " + str(value))  -> e.g. "WEEK : 4 times per week"
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


def save_or_modify_habit(save_or_modify: str, title_name: Optional[str], save_type: Optional[str]) -> None:
    """
    saving habit or modifying habbit.
    :param save_or_modify: is INSERT or MODIFY
    :param title_name: MODIFY only -> title of element
    :param save_type: is yesNo Type or Measurable Type
    :return: list of saving element's value
    """
    # 입력값 저장 용도 list
    list = []
    fre_arr = ["DAY", "WEEK", "MONTH"]
    am_or_pm = ["AM", "PM"]
    set_or_not = [True, False]

    # 등록 또는 수정 구분
    if save_or_modify == "INSERT":
        print("#####  습관 추가 시작  #####")
        find_element("ID", "actionCreateHabit", False).click()
        find_element("ID", save_type, False).click()
        # 빈도 설정
        list.append(set_frequency(fre_arr[random.randint(0, (len(fre_arr) - 1))], save_type, random.randint(1, 10)))
    elif save_or_modify == "MODIFY":
        print("#####  습관 수정 시작  #####")
        find_element("XPATH", "//*[@text='" + title_name + "']", False).click()
        find_element("ID", "action_edit_habit", False).click()
        # 빈도 설정
        list.append(set_frequency(fre_arr[random.randint(0, (len(fre_arr) - 1))], save_type, random.randint(1, 10)))

    # 제목 입력 및 저장
    list.append(input_textbox(find_element("ID", "nameInput", False), lorem.words(3)))

    # 컬러 선택 및 RGB 저장
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
            print("   ㄴ[컬러 설정] - FAIL \"", str(random_idx), "\" -> 설정 값으로 반영 되지 않았습니다.")
        else:
            print("   ㄴ[컬러 설정] - PASS \"", str(random_idx), "\" -> 설정 값으로 반영 되었습니다.")

    # 반영된 색 저장
    list.append(color2)
    # 질문 입력 및 저장
    list.append(input_textbox(find_element("ID", "questionInput", False), lorem.words(3)))

    # 알림 설정 및 결과 저장
    list.append(set_alarm(am_or_pm[random.randint(0, (len(am_or_pm) - 1))],
                          set_or_not[random.randint(0, (len(set_or_not) - 1))]))

    if save_type == "buttonMeasurable":
        list.append(input_textbox(find_element("ID", "unitInput", False), lorem.words(1)))
        list.append(input_textbox(find_element("ID", "targetInput", False), random.randint(1, 15)))

    # 메모 입력 및 저장
    list.append(input_textbox(find_element("ID", "notesInput", False), lorem.words(3)))
    # 정의한 습관 저장
    find_element("ID", "buttonSave", False).click()

    # 수정시 사용
    if save_type is not None:
        list.append(save_type)

    if save_or_modify == "MODIFY":
        find_element("XPATH", '//android.widget.ImageButton[@content-desc="위로 이동"]', False).click()
        print("#####  습관 수정 종료  #####")
    else:
        print("#####  습관 추가 종료  #####")

    return list


def del_habit(title_name: str):
    """
    deleting habit.
    :param title_name: title name of habit
    """
    print("## 습관 삭제 시작")

    find_element("XPATH", "//*[@text='" + title_name + "']", False).click()
    tab_device_with_bounds("[649,75][720,159]")
    find_element("XPATH", "//*[@text='삭제']", False).click()
    find_element("XPATH", "//*[@text='네']", False).click()

    print("## 습관 삭제 완료")


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

saved_arr = []
# 습관 추가 - 예 아니오 기준
saved_arr.append(save_or_modify_habit("INSERT", None, "buttonYesNo"))
# 습관 추가 - 측정 가능 기준
saved_arr.append(save_or_modify_habit("INSERT", None, "buttonMeasurable"))

# 습관 기록 확인
habits = saved_arr
for habit in habits:
    for i in range(5):
        box = find_element("XPATH",
                           "(//*[@class='android.widget.LinearLayout' and (./preceding-sibling::* | ./following-sibling::*)[@text='" +
                           habit[
                               1] + "'] and ./parent::*[@class='android.widget.LinearLayout'] and (./preceding-sibling::* | ./following-sibling::*)[@class='android.view.View']]/*[@class='android.view.View'])[" + str(
                               i + 1) + "]",
                           False)
        action = TouchAction(driver)
        WebDriverWait(driver, 10).until(ec.element_to_be_clickable(box))
        action.long_press(box).perform()

        if len(habit) > 8:
            scrolls = find_element("XPATH", "//*[@resource-id='android:id/numberpicker_input']", True)
            for scroll in scrolls:
                WebDriverWait(driver, 10).until(ec.element_to_be_clickable(scroll))
                scroll.clear()
                scroll.send_keys(str(random.randint(0, 100)))
            find_element("XPATH", "//*[@text='확인']", False).click()

# 습관 수정
modified_arr = []
for saved in habits:
    print(saved)
    modified_arr.append(save_or_modify_habit("MODIFY", saved[1], saved[len(saved) - 1]))

# 습관 삭제
for saved in modified_arr:
    del_habit(saved[1])

# 녹화 종료 -> Base64로 디코딩
recording_data = driver.stop_recording_screen()
decoded_data = base64.b64decode(recording_data)

# 비디오 파일로 저장
with open(RECORD_FILE, "wb") as video_file:
    video_file.write(decoded_data)

# Driver Remote 종료
driver.quit()
