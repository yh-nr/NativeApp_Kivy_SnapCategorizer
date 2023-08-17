from jnius import autoclass, PythonJavaClass, java_method
import json

from . import config_manager

try:from android.config import ACTIVITY_CLASS_NAME, ACTIVITY_CLASS_NAMESPACE
except:pass

# Request code for selecting a JSON document.
PICK_JSON_FILE = 42
RESULT_OK = -1  # Define a constant for RESULT_OK

# Java classes for Python
try:
    Uri = autoclass('android.net.Uri')
    Intent = autoclass('android.content.Intent')
    PythonActivity = autoclass(ACTIVITY_CLASS_NAME)
    _activity = autoclass(ACTIVITY_CLASS_NAME).mActivity
except Exception as e:
    print("Failed to import Java classes:", e)

class ActivityResultEvent(PythonJavaClass):
    __javainterfaces__ = ['org/kivy/android/ActivityResultListener']
    __javacontext__ = 'app'

    def __init__(self, callback):
        super(ActivityResultEvent, self).__init__()
        self.callback = callback

    @java_method('(IILandroid/content/Intent;)V')
    def onActivityResult(self, requestCode, resultCode, intent):
        if requestCode == PICK_JSON_FILE:
            if resultCode == RESULT_OK:
                uri = intent.getData()
                json_text = read_json_file(uri)
                json_data = json.loads(json_text)
                self.callback(json_data)

def open_file(picker_initial_uri):
    intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
    intent.addCategory(Intent.CATEGORY_OPENABLE)
    intent.setType("application/json")
    current_activity = PythonActivity.mActivity
    current_activity.startActivityForResult(intent, PICK_JSON_FILE)

def read_json_file(uri):
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

# def load_json_4android():    
#     event = ActivityResultEvent(callback_function)
#     picker_initial_uri = Uri.parse("file:///sdcard/")
#     open_file(picker_initial_uri)

def process_json_data(data):
    try:
        config_manager.save_config_to_file(config_manager.SETTINGS_FILE, data)
        print(data)
    except Exception as e:
        print("Failed to process JSON data:", e)

# def callback_function(json_data):
#     try:
#         process_json_data(json_data)
#     except json.JSONDecodeError as e:
#         print("Failed to decode JSON:", e)

def load_json_4android():    
    def callback_function(json_data):
        try:
            process_json_data(json_data)
        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", e)
    
    event = ActivityResultEvent(callback_function)
    
    picker_initial_uri = Uri.parse("file:///sdcard/")
    open_file(picker_initial_uri)
