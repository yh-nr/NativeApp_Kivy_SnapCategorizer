import json
from kivy.app import App
from .filepicker import load_json_4android


SETTINGS_FILE = r'config.json'
DEFAULT_SETTINGS_FILE = r'./assets/config.json'

def load_config_from_file(filename=SETTINGS_FILE):
    global settings
    with open(filename, 'r', encoding='utf-8') as f:
        settings = json.load(f)
        save_config_to_file(SETTINGS_FILE, settings)
    return settings

def save_config_to_file(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    try:button_refresh()
    except:pass



def load_json_with_android_filepicker():
    load_json_4android()

def button_refresh():
    app = App.get_running_app()
    app.root.buttongrid.refreshAndSwitchButtonSet()


def delete_setting(num):
    global settings
    print(settings)
    print(f'btn{num}')
    _ = settings.pop(f'btn{num}', None)
    print(settings)
    save_config_to_file(SETTINGS_FILE, settings)
    return settings

def update_setting(btn, num, name):
    global settings
    # settings[btn]['num'] = num
    # settings[btn]['name'] = name
    
    settings[btn] = {
        "num": num,
        "name": name  # ここに適切な名前や値を設定してください
    }
    save_config_to_file(SETTINGS_FILE, settings)
    return settings

def initialize_settings():
    global settings
    try:
        settings = load_config_from_file()
    except:
        save_config_to_file(SETTINGS_FILE, load_config_from_file(DEFAULT_SETTINGS_FILE))
        settings = load_config_from_file()
        print('config.jsonを作成したよ！')

# 最初に設定を初期化する
initialize_settings()