import datetime
import timeit

#kivy関連import
from kivy.app import App   
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.audio import SoundLoader
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Rectangle

from kivy.graphics import Color, Line
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
                 font_size= '35sp', 
                 color= (1,1,1,1), 
                 outline_color= (1,0,0,.5), 
                 outline_weight= .8,
                 background_color= (1,1,1,0),
                 halign= 'center',
                 pos_hint={"center_x": 0.5, "center_y": 0.5},
                 **kwargs):
        
        super(ATButton, self).__init__(**kwargs)

        # デフォルト値を読み込み
        self.custom_id = custom_id
        self.text = text
        self.font_size = font_size
        self.background_color= background_color
        self.halign= halign

        # 白抜き文字の実装
        self.color = color
        self.outline_color = outline_color
        self.outline_weight = outline_weight
        self.pos_hint= pos_hint
        self.bind(size=self.update_text, pos=self.update_text)

        # 長押しを実装
        self.start = 0
        self.single_hit = 0
        self.press_state = False
        self.register_event_type('on_single_press')
        self.register_event_type('on_double_press')
        self.register_event_type('on_long_press')

    def update_text(self, *args):
        # 以前のアウトラインの描画をクリアする
        self.canvas.before.clear()
        
        # アウトラインの色を白に設定
        outline_color = self.outline_color
        outline_weight = self.outline_weight

        
        # テキストの情報を持つCoreLabelオブジェクトを生成
        text_label = CoreLabel(text=self.text, font_size=self.font_size, font_name=self.font_name, halign=self.halign)
        
        # CoreLabelオブジェクトを更新して、テキストのテクスチャを生成
        text_label.refresh()
        
        # テキストのテクスチャを取得
        texture = text_label.texture
        
        # テキストのテクスチャのサイズを取得
        texture_size = texture.size
        
        # アウトラインを描画するためのコンテキストに入る
        with self.canvas.before:
            # アウトラインの色を設定
            Color(*outline_color)
            
            # アウトラインを描画（縁取りの太さを調整するためのループ）
            for x in [-outline_weight, 0, outline_weight]:
                for y in [-outline_weight, 0, outline_weight]:
                    if x != 0 or y != 0:
                        # アウトラインの一部を描画
                        Rectangle(texture=texture, 
                                pos=(self.center_x + x - texture_size[0] / 2.0, 
                                    self.center_y + y - texture_size[1] / 2.0),
                                size=texture_size)

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