import subprocess
import time
import os
from datetime import datetime
from ppadb.client import Client as AdbClient

RECORDING_PATH = '%s/' % os.getcwd() + 'record/'
record_file = RECORDING_PATH + '/' + datetime.now().strftime("%Y%m%d%H%M%S") + '.mp4'

try :
  client = AdbClient(host='0.0.0.0', port=5037)
  device = client.devices()[0]
except Exception as e :
  print(e)
  exit(1)

# 녹화할 화면 크기와 파일 경로를 지정합니다.
width, height = 720, 1280
file_path = "/sdcard/Recordings/test.mp4"

# screenrecord 명령어를 실행합니다.
cmd = f"adb shell screenrecord " + file_path
process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)

# 10초 동안 녹화합니다.
time.sleep(10)

# 녹화를 중지합니다.
process.send_signal(subprocess.signal.SIGINT)
