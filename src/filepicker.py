from jnius import autoclass, PythonJavaClass, java_method
import json
from . import config_manager
from .func import show_toast
from android.config import ACTIVITY_CLASS_NAME, ACTIVITY_CLASS_NAMESPACE


# Request code for selecting a JSON document.
PICK_JSON_FILE = 42
RESULT_OK = -1  # Define a constant for RESULT_OK

# Java classes for Python
Uri = autoclass('android.net.Uri')
Intent = autoclass('android.content.Intent')
PythonActivity = autoclass(ACTIVITY_CLASS_NAME)

class ActivityResultEvent(PythonJavaClass):
    __javainterfaces__ = [ACTIVITY_CLASS_NAMESPACE + '$ActivityResultListener']
    # __javacontext__ = 'app'

    def __init__(self, callback):
        super(ActivityResultEvent, self).__init__()
        self.callback = callback

    @java_method('(IILandroid/content/Intent;)V')
    def onActivityResult(self, requestCode, resultCode, intent):
        show_toast('onActivityResultが呼び出されたか確認')
        if requestCode == PICK_JSON_FILE:
            if resultCode == RESULT_OK:
                uri = intent.getData()
                json_text = read_json_file(uri)
                json_data = json.loads(json_text)
                self.callback(json_data)

# def open_file(picker_initial_uri):
#     show_toast('open_fileが呼び出されたか確認')
#     intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
#     intent.addCategory(Intent.CATEGORY_OPENABLE)
#     intent.setType("application/json")
#     current_activity = PythonActivity.mActivity
#     current_activity.startActivityForResult(intent, PICK_JSON_FILE)

def read_json_file(uri):
    show_toast('read_json_fileが呼び出されたか確認')
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

def process_json_data(data):
    show_toast('process_json_dataが呼び出されたか確認')
    config_manager.save_config_to_file(config_manager.SETTINGS_FILE, data)

def callback_function(json_data):
    show_toast('callback_functionが呼び出されたか確認')
    process_json_data(json_data)

def load_json_4android():
    show_toast('load_json_4androidが呼び出されたか確認')
    event = ActivityResultEvent(callback_function)
    picker_initial_uri = Uri.parse("file:///sdcard/")
    # open_file(picker_initial_uri)
    show_toast('open_fileが呼び出されたか確認')
    intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
    intent.addCategory(Intent.CATEGORY_OPENABLE)
    intent.setType("application/json")
    intent.putExtra(Intent.EXTRA_INITIAL_URI, picker_initial_uri)
    current_activity = PythonActivity.mActivity
    current_activity.addActivityResultListener(event)
    current_activity.startActivityForResult(intent, PICK_JSON_FILE)
