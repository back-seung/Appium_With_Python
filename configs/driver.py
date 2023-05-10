from appium import webdriver

def get_driver():
    """
    Get driver using with URL, DESIRED_CAPABILITIES
    :return: Remote driver
    """
    print("Web Driver Initialized")
    return webdriver.Remote(URL, DESIRED_CAPABILITIES)


URL = "0.0.0.0:4724/wd/hub"
DESIRED_CAPABILITIES = {
    "platformName": "Android",
    "appium:platformVersion": "12.0",
    "appium:app": "/Users/mac/Desktop/Appium/apk/uhabits.apk",
    "appium:automationName": "UiAutomator2",
    "appium:newCommandTimeout": "10",
    "appium:appPackage": "org.isoron.uhabits",
    "appium:appActivity": "org.isoron.uhabits.MainActivity"
}
