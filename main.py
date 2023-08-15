import datetime
import timeit

#kivy関連import
from kivy.app import App   
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.utils import platform
from kivy.clock import Clock
from kivy.config import Config
Config.set('kivy', 'log_level', 'debug')
import japanize_kivy
from camera4kivy import Preview
try:from android.permissions import request_permissions, Permission, check_permission
except:pass

from src.func import show_toast
from src import config_manager

DOUBLE_TAP_TIME = 0.2   # Change time in seconds
LONG_PRESSED_TIME = 0.3  # Change time in seconds

# カメラへのアクセス許可を要求する
if platform == "android":
    if check_permission(Permission.CAMERA):pass
    else:request_permissions([Permission.CAMERA])
    if check_permission(Permission.WRITE_EXTERNAL_STORAGE):pass
    else:request_permissions([Permission.WRITE_EXTERNAL_STORAGE])
    if check_permission(Permission.READ_EXTERNAL_STORAGE):pass
    else:request_permissions([Permission.READ_EXTERNAL_STORAGE])
else:pass


class AppFrame(BoxLayout):pass


class ButtonGrid(GridLayout):
    camera_preview = ObjectProperty(None)
    buttongrid = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ButtonGrid, self).__init__(**kwargs)
    
    
    def on_parent(self, instance, value):
        self.refreshAndSwitchButtonSet()

    
    def refreshAndSwitchButtonSet(self, mode=None):
        offset=0
        current_buttons = [int(bc.custom_id.replace('btn','')) for bc in self.children]
        if len(current_buttons):offset += max(current_buttons)+1
        try:config_manager.settings[f'btn{max(current_buttons)+1}']
        except:offset=0
        if not mode:
            try:offset = min(current_buttons)
            except:offset=0
        self.clear_widgets()
        try:
            for i in range(12):
                n = i + offset
                btn = ATButton(custom_id=f'btn{n}',
                            text = '['+str(config_manager.settings[f'btn{n}']['num'])+']\n'+config_manager.settings[f'btn{n}']['name']
                            )
                btn.bind(on_single_press=lambda btn_instance=btn: self.camera_preview.capture_button(btn_instance))
                btn.bind(on_long_press=lambda btn_instance=btn: self.camera_preview.popup_open(btn_instance))
                self.add_widget(btn)
        except:pass

    def test_children(self):
        current_buttons = [int(bc.custom_id.replace('btn','')) for bc in self.children]
        print(current_buttons)

class CameraPreview(Preview):
    # image_texture = ObjectProperty(None)
    # image_capture = ObjectProperty(None)
    # camera = ObjectProperty(None)
    camerapreview = ObjectProperty(None)
    buttongrid = ObjectProperty(None)
    sound = SoundLoader.load(r'./res/shuttersound.mp3')

    def __init__(self, **kwargs):
        super(CameraPreview, self).__init__(**kwargs)
        self.play()
        pass

    def get_button_text(self, instance):
        settings = config_manager.settings
        return f"[{settings[instance.custom_id]['num']}]\n{settings[instance.custom_id]['name']}"
    
    def play(self):
        if self.camera_connected:
            self.disconnect_camera()
            # show_toast('カメラを切断します')
        else:
            self.try_connect_camera()

    def try_connect_camera(self):
        if platform == "android":
            self.connect_camera_if_permitted()
        else:
            self.connect_camera(enable_analyze_pixels=True, enable_video=False)
            # show_toast('カメラへの接続を試みます')

    def connect_camera_if_permitted(self):
        if check_permission(Permission.CAMERA):
            self.connect_camera(enable_analyze_pixels=True, enable_video=False)
        else:
            Clock.schedule_once(lambda dt: self.play(), 5)


    def capture_button(self,instance):
        if self.sound:self.sound.play()
        t_delta = datetime.timedelta(hours=9)
        JST = datetime.timezone(t_delta, 'JST')
        now = datetime.datetime.now(JST)

        #windowsの場合に、subdir1が存在するかチェックするコードをここに入れる      
         
        settings = config_manager.settings
        subdir1 = settings['theme']
        subdir2 = str(settings[instance.custom_id]['num'])
        subdir = subdir1 + '/' + subdir2
        name = f'img{now:%y%m%d%H%M%S%f}'[:-3]
        self.capture_photo(subdir=subdir ,name=name)
        pass


    def update_setting(self, btn, num, name):
        config_manager.update_setting(btn, num, name)
        self.buttongrid.refreshAndSwitchButtonSet()

    # デフォルトの設定ファイルを再読み込みする
    def load_default_settings(self):
        setting = config_manager.load_config_from_file(r'./assets/config.json')
        config_manager.save_config_to_file('config.json', setting)
        self.buttongrid.refreshAndSwitchButtonSet()

    def maxnum_from_settings(self):
        settings = config_manager.settings
        nums = [int(key.replace("btn", "")) for key in settings if key.startswith("btn")]
        return max(nums)

    def add_button(self):
        settings = config_manager.settings
        maxnum = max([int(key.replace("btn", "")) for key in settings if key.startswith("btn")])+1
        settings[f'btn{maxnum}'] = {
            "num": maxnum,
            "name": "＊＊＊"  # ここに適切な名前や値を設定してください
        }
        config_manager.save_config_to_file('config.json', settings)
        self.buttongrid.refreshAndSwitchButtonSet()

    # ボタンの設定変更ポップアップを表示する
    def popup_open(self, instance):
        settings = config_manager.settings
        btn = instance.custom_id
        num = str(settings[btn]['num'])
        name = settings[instance.custom_id]['name']
        popup_text = [btn, num, name]
        content = PopupMenu(popup_text=popup_text, popup_close=self.popup_close, update_setting=self.update_setting)
        self.popup = Popup(title=f'ボタン{btn.replace("btn","")}の割当を変更', content=content, size_hint=(0.5, 0.5), auto_dismiss=True)
        self.popup.open()

    def popup_close(self):
        self.popup.dismiss()

 

    


class ATButton(Button):
    def __init__(self,
                 custom_id='btn0', 
                 text='ボタン', 
                 font_size=35, 
                 background_color= (1,1,1,0),
                 halign= 'center',
                 **kwargs):
        
        super(ATButton, self).__init__(**kwargs)

        # デフォルト値を読み込み
        self.custom_id = custom_id
        self.text = text
        self.font_size = font_size
        self.background_color= background_color
        self.halign= halign

        # 文字色変更用
        self.color_index = 0
        self.colors = [(0, 0, 0, .7), (1, 0, 0, .7), (1, 1, 1, .7), (1, 1, 1, 0)]  # 黒, 赤, 白
        self.color = self.colors[self.color_index]
        Clock.schedule_interval(self.update_color, 1/4)  # 1秒ご

        # 長押しを実装
        self.start = 0
        self.single_hit = 0
        self.press_state = False
        self.register_event_type('on_single_press')
        self.register_event_type('on_double_press')
        self.register_event_type('on_long_press')

    
    def update_color(self, *args):
        self.color_index = (self.color_index + 1) % 4
        self.color = self.colors[self.color_index]

    # def on_touch_down(self, touch):
    #     print('タッチダウン！')
    #     if super(ATButton, self).on_touch_down(touch):
    #         if self._current_touch_id is None or self._current_touch_id != touch.uid:
    #             # 新たなタッチが発生した場合のみ、フラグをリセットし、タイマーを設定
    #             self._is_long_press = False
    #             self._long_press_clock = Clock.schedule_once(self._do_long_press, self.long_press_time)
    #             self._current_touch_id = touch.uid  # タッチのIDを保存
    #         return True
    #     return False

    #     # print('タッチダウン！')
    #     # self._is_long_press = False  # タッチが始まるたびにフラグをリセット
    #     # if super(ATButton, self).on_touch_down(touch):
    #     #     self._long_press_clock = Clock.schedule_once(self._do_long_press, self.long_press_time)
    #     #     return True
    #     # return False

    # def on_touch_up(self, touch):
    #     print('タッチアップ！')
    #     if self._long_press_clock:
    #         Clock.unschedule(self._long_press_clock)
    #         self._long_press_clock = None

    #     if touch.grab_current is self and not self._is_long_press:
    #         # 長押しでなければ、on_release イベントを発火
    #         self.dispatch('on_release')

    #     # タッチが終了したので、タッチのIDをリセット
    #     if self._current_touch_id == touch.uid:
    #         self._current_touch_id = None

    # #     return super(ATButton, self).on_touch_up(touch)

    # def _on_state(self, instance, value):
    #     print(value)
    #     if value == 'down':
    #         # ボタンが押されたとき、長押しフラグをリセットし、タイマーを設定
    #         self._is_long_press = False
    #         self._long_press_clock = Clock.schedule_once(self._do_long_press, self._long_press_time)
    #     else:
    #         # ボタンが離されたとき、タイマーをキャンセル
    #         if self._long_press_clock:
    #             Clock.unschedule(self._long_press_clock)
    #             self._long_press_clock = None

    #         if not self._is_long_press:
    #             # 長押しでなければ、on_release イベントを発火
    #             self.dispatch('on_release')

    #         # タッチが終了したので、長押しフラグをリセット
    #         self._is_long_press = False

    # def _do_long_press(self, dt):
    #     self._is_long_press = True  # 長押しを検出
    #     self.dispatch('on_long_press')

    # def on_long_press(self):
    #     print("Long press detected")

    # def on_release(self):
    #     print("Button released")

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.start = timeit.default_timer()
            if touch.is_double_tap:
                self.press_state = True
                self.single_hit.cancel()
                self.dispatch('on_double_press')
        else:
            return super(ATButton, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.press_state is False:
            if self.collide_point(touch.x, touch.y):
                stop = timeit.default_timer()
                awaited = stop - self.start

                def not_double(time):
                    nonlocal awaited
                    if awaited > LONG_PRESSED_TIME:
                        self.dispatch('on_long_press')
                    else:
                        self.dispatch('on_single_press')

                self.single_hit = Clock.schedule_once(not_double, DOUBLE_TAP_TIME)
            else:
                return super(ATButton, self).on_touch_down(touch)
        else:
            self.press_state = False

    def on_single_press(self):
        print('single')
        pass

    def on_double_press(self):
        print('double')
        pass

    def on_long_press(self):
        print('long')
        pass

class PopupMenu(BoxLayout):
    popup_text = ListProperty()
    update_setting = ObjectProperty(None)
    popup_close = ObjectProperty(None)




class SnapCategorizerApp(App):
    def __init__(self, **kwargs):
        super(SnapCategorizerApp, self).__init__(**kwargs)
        self.title = 'SnapCategorizer for ML Image Annotation'

    def build(self):
        show_toast(self.title)
        return AppFrame()
    

if __name__ == '__main__':                      #main.pyが直接実行されたら、、、という意味らしい
    SnapCategorizerApp().run()                         #