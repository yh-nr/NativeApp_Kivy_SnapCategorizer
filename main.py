#kivy関連import
from kivy.app import App            
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform
from kivy.config import Config
Config.set('kivy', 'log_level', 'debug')

import japanize_kivy

from src.Cam2annotate import CameraPreview, ATButton, PopupMenu
from src.func import show_toast

try:from android.permissions import request_permissions, Permission, check_permission
except:pass

# カメラへのアクセス許可を要求する
if platform == "android":
    if check_permission(Permission.CAMERA):pass
    else:request_permissions([Permission.CAMERA])
    if check_permission(Permission.WRITE_EXTERNAL_STORAGE):pass
    else:request_permissions([Permission.WRITE_EXTERNAL_STORAGE])
    if check_permission(Permission.READ_EXTERNAL_STORAGE):pass
    else:request_permissions([Permission.READ_EXTERNAL_STORAGE])
else:pass

class ATButton(ATButton):pass
class CameraPreview(CameraPreview):pass
class PopupMenu(PopupMenu):pass

class AppFrame(BoxLayout):pass


class SnapCategorizerApp(App):
    def __init__(self, **kwargs):
        super(SnapCategorizerApp, self).__init__(**kwargs)
        self.title = 'SnapCategorizer for ML Image Annotation'

    def build(self):
        show_toast(self.title)
        return AppFrame()

if __name__ == '__main__':                      #main.pyが直接実行されたら、、、という意味らしい
    SnapCategorizerApp().run()                         #
    



