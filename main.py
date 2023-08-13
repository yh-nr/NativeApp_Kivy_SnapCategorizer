import datetime

#kivy関連import
from kivy.app import App   
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
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
        

    def add_buttons(self, ):
        self.buttongrid.clear_widgets()

        for i in range(len(self.camera_preview.btn_name)):
            btn = ATButton(custom_id=f'btn{i}',
                           index=i,
                           camera_preview= self.camera_preview
                           )
            print(type(btn.text))
            btn.bind(on_press=lambda btn_instance=btn: self.camera_preview.capture_button(btn_instance))
            btn.bind(on_long_press=lambda btn_instance=btn: self.camera_preview.popup_open(btn_instance))
            self.add_widget(btn)

class CameraPreview(Preview):
    # image_texture = ObjectProperty(None)
    # image_capture = ObjectProperty(None)
    # camera = ObjectProperty(None)
    camerapreview = ObjectProperty(None)
    btn_name = ListProperty(['btn0','btn1','btn2','btn3','btn4','btn5','btn6','btn7','btn8','btn9','btn10','btn11'])
    

    def __init__(self, **kwargs):
        super(CameraPreview, self).__init__(**kwargs)
        for n in range(len(self.btn_name)):
            self.btn_name[n] = '['+str(config_manager.settings[f'btn{n}']['num'])+']\n'+config_manager.settings[f'btn{n}']['name']
        self.play()
        pass

    def get_button_text(self, instance):
        settings = config_manager.settings
        return f"[{settings[instance.custom_id]['num']}]\n{settings[instance.custom_id]['name']}"
 
    def play(self):
        if self.camera_connected == False:
            if platform == "android":
                if check_permission(Permission.CAMERA):
                    self.connect_camera(enable_analyze_pixels = True, enable_video = False)
                else:
                    Clock.schedule_once(lambda dt: self.play(), 5)
            else:
                # show_toast('カメラへの接続を試みます')
                self.connect_camera(enable_analyze_pixels = True, enable_video = False)
        else:
            # show_toast('カメラを切断します')
            self.disconnect_camera()

    def capture_button(self,instance):
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
        print('testA')
        self.update_button_name()
        print('testB')

    def load_button(self):
        setting = config_manager.load_config_from_file(r'./assets/config.json')
        config_manager.save_config_to_file('config.json', setting)
        self.update_button_name()
    
    def update_button_name(self):
            print(self)
            for n in range(len(self.btn_name)):
                print(n)
                self.btn_name[n] = '['+str(config_manager.settings[f'btn{n}']['num'])+']\n'+config_manager.settings[f'btn{n}']['name']

    def change_button_text(self, value):
        print('test')
        pass

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
    camerapreview = CameraPreview()
    print(type(camerapreview))
    camera_preview = ObjectProperty(camerapreview.camerapreview)
    
    print(type(camerapreview.camerapreview))


    def __init__(self,
                 index=0, 
                 font_size=35, 
                 background_color= (1,1,1,0),
                 color= (1,1,1,.8),
                 halign= 'center',
                 **kwargs):
        
        super(ATButton, self).__init__(**kwargs)

        # デフォルト値を読み込み
        self.font_size = font_size
        self.background_color= background_color
        self.color= color
        self.halign= halign

        # 
        self.index = index
        self.camera_preview.bind(btn_name=self.update_text)
        self.update_text()

        # 長押しを実装
        self.register_event_type('on_long_press')
        self.long_press_time = 0.5  # 長押しとして認識するまでの時間（秒）
        self._long_press_clock = None
    
    def update_text(self, *args):
        self.text = self.camerapreview.btn_name[self.index]

    def on_touch_down(self, touch):
        if super(ATButton, self).on_touch_down(touch):
            self._long_press_clock = Clock.schedule_once(self._do_long_press, self.long_press_time)
            return True
        return False

    def on_touch_up(self, touch):
        if self._long_press_clock:
            Clock.unschedule(self._long_press_clock)
            self._long_press_clock = None
        return super(ATButton, self).on_touch_up(touch)
    
    def _do_long_press(self, dt):
        self.dispatch('on_long_press')

    def on_long_press(self):
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