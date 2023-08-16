import datetime, timeit, os

#kivy関連import
from kivy.app import App   
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.core.audio import SoundLoader
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Rectangle

from kivy.graphics import Color, Line
from kivy.properties import ObjectProperty, StringProperty, ListProperty, NumericProperty
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
class MenuButtons(BoxLayout):pass

class ButtonGrid(GridLayout):
    camera_preview = ObjectProperty(None)
    buttongrid = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ButtonGrid, self).__init__(**kwargs)
    
    
    def on_parent(self, instance, value):
        self.refreshAndSwitchButtonSet()

    
    def refreshAndSwitchButtonSet(self, mode=None):
        '''シャッターボタンを更新する。もしくは次のページ（次の12個のボタン）を表示する関数
        '''
        settings = config_manager.settings
        limit = max([int(key.replace("btn", "")) for key in settings if key.startswith("btn")])
        offset=0
        current_buttons = [int(bc.custom_id.replace('btn','')) for bc in self.children]
        if len(current_buttons):offset += max(current_buttons)+1
        # try:settings[f'btn{max(current_buttons)+1}']
        # except:offset=0
        if not mode:
            try:offset = min(current_buttons)
            except:offset=0
        self.clear_widgets()

        i = 0
        while i < 12:
            n = i + offset
            if n > limit:break
            try:
                btn = ATButton(custom_id=f'btn{n}',
                            text='[' + str(config_manager.settings[f'btn{n}']['num']) + ']\n' + config_manager.settings[f'btn{n}']['name']
                            )
                btn.bind(on_single_press=lambda btn_instance=btn: self.camera_preview.capture_button(btn_instance))
                btn.bind(on_long_press=lambda btn_instance=btn: self.camera_preview.button_change_popup_open(btn_instance))
                btn.bind(on_double_press=lambda btn_instance=btn: self.camera_preview.confirmdelete_popup_open(btn_instance))
                self.add_widget(btn)
                i += 1  # エラーが発生しなかった場合にのみカウンタをインクリメントします
            except:
                offset += 1
                

    # # ウィジェットツリーを取得する
    # def test_children(self):
    #     current_buttons = [int(bc.custom_id.replace('btn','')) for bc in self.children]
    #     print(current_buttons)

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

        settings = config_manager.settings
        subdir1 = settings['root_dir']
        subdir2_num = str(settings[instance.custom_id]["num"])
        subdir2_name = '_' +settings[instance.custom_id]["name"]
        subdir2 = subdir2_num + subdir2_name
        name = f'img{now:%y%m%d%H%M%S%f}'[:-3]
        
        # Windowsで実行する場合に、subdir1が存在しないとcaputure_photoがエラーになるため、ここで作成する。
        if platform == "win":
            subdir = os.path.join(subdir1, subdir2_num)
            if not os.path.exists(subdir):
                os.makedirs(subdir)
                self.capture_photo(subdir=subdir ,name=name)
        else:
            subdir = os.path.join(subdir1, subdir2)
            self.capture_photo(subdir=subdir ,name=name)
        print(subdir)
        
        pass


    # ボタンの設定変更ポップアップを表示する
    def button_change_popup_open(self, instance):
        settings = config_manager.settings
        btn = instance.custom_id
        num = str(settings[btn]['num'])
        name = settings[instance.custom_id]['name']
        popup_text = [btn, num, name]
        content = ButtonAddFixMenu(popup_text=popup_text, popup_close=self.popup_close, update_setting=self.update_setting)
        self.popup = Popup(title=f'ボタン{num}の割当を変更', content=content, size_hint=(0.5, 0.5), auto_dismiss=True)
        self.popup.open()

    def add_newbutton_popup_open(self):
        settings = config_manager.settings
        new_button = max([int(key.replace("btn", "")) for key in settings if key.startswith("btn")])+1
        settings = config_manager.settings
        btn = f'btn{new_button}'
        num = new_button
        name = '新規ラベル'
        popup_text = [btn, num, name]
        content = ButtonAddFixMenu(popup_text=popup_text, popup_close=self.popup_close, update_setting=self.add_newbutton)
        self.popup = Popup(title=f'ボタン{new_button}を追加', content=content, size_hint=(0.5, 0.5), auto_dismiss=True)
        self.popup.open()

    def confirmdelete_popup_open(self, instance):
        settings = config_manager.settings
        num = str(settings[instance.custom_id]['num'])
        content = ConfirmDeleteMenu(btn_num=num, popup_close=self.popup_close, delete_setting=self.delete_setting)
        self.popup = Popup(title=f'確認：ボタン{num}', content=content, size_hint=(0.5, 0.5), auto_dismiss=True)
        self.popup.open()

    def load_json_popup_open(self):
        content = LoadJsonMenu(popup_close=self.popup_close, load=self.load_external_json)
        self.popup = Popup(title=f'JSONファイル読込', content=content, size_hint=(0.5, 0.5), auto_dismiss=True)
        self.popup.open()

    def popup_close(self):
        self.popup.dismiss()
    
    def update_setting(self, btn, num, name):
        config_manager.update_setting(btn, num, name)
        self.buttongrid.refreshAndSwitchButtonSet()
    
    def delete_setting(self, num):
        config_manager.delete_setting(num)
        print('動いてる？')
        self.buttongrid.refreshAndSwitchButtonSet()
    
    def load_external_json(self,path,selected):
        if selected:config_manager.load_config_from_file(selected[0])
        self.buttongrid.refreshAndSwitchButtonSet()

    def add_newbutton(self, btn, num, name):
        settings = config_manager.settings
        settings[btn] = {
            "num": num,
            "name": name  # ここに適切な名前や値を設定してください
        }
        config_manager.save_config_to_file('config.json', settings)
        self.buttongrid.refreshAndSwitchButtonSet()

class ATButton(Button):
    def __init__(self,
                 custom_id='btn0', 
                 text='ボタン', 
                 font_size= '35', 
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
        # self.bind(on_long_press=lambda self:self.button_change_popup_open(self))

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


class ButtonAddFixMenu(BoxLayout):
    popup_text = ListProperty()
    update_setting = ObjectProperty(None)
    popup_close = ObjectProperty(None)

class ConfirmDeleteMenu(BoxLayout):
    btn_num = StringProperty()
    delete_setting = ObjectProperty(None)
    popup_close = ObjectProperty(None)

class LoadJsonMenu(BoxLayout):
    # btn_num = StringProperty()
    load = ObjectProperty(None)
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