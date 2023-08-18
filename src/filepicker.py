from jnius import autoclass, PythonJavaClass, java_method
import json
from . import config_manager
from .func import show_toast
from android.config import ACTIVITY_CLASS_NAME, ACTIVITY_CLASS_NAMESPACE
from android import activity


# Request code for selecting a JSON document.
PICK_JSON_FILE = 42
RESULT_OK = -1  # Define a constant for RESULT_OK

# Java classes for Python
Uri = autoclass('android.net.Uri')
Intent = autoclass('android.content.Intent')
PythonActivity = autoclass(ACTIVITY_CLASS_NAME)

def read_json_file(uri):
    show_toast('read_json_fileが呼び出されたか確認')
    print(uri)
    content_resolver = PythonActivity.mActivity.getContentResolver()
    stream = content_resolver.openInputStream(uri)  
    json_text = ''
    buffer = bytearray(1024)
    try:
        while True:
            length = stream.read(buffer)
            if length == -1:
                break
            json_text += buffer[:length].decode('utf-8')
    finally:
        stream.close()
    return json_text


def process_json_data_callback(requestCode, resultCode, intent):
    print('process_json_data_callbackが呼び出されたか確認')
    if requestCode == PICK_JSON_FILE:
        if resultCode == RESULT_OK:
            uri = intent.getData()
            json_text = read_json_file(uri)
            json_data = json.loads(json_text)
            config_manager.save_config_to_file(config_manager.SETTINGS_FILE, json_data)
            print(json_data)
    

def load_json_4android():
    intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
    intent.addCategory(Intent.CATEGORY_OPENABLE)
    intent.setType("application/json")
    current_activity = PythonActivity.mActivity
    current_activity.startActivityForResult(intent, PICK_JSON_FILE)
