"""func.pyには共通の関数を格納しています。"""

import json
import os
from os.path import join, abspath

from kivy.utils import platform
from kivy.resources import resource_find, resource_add_path
from kivy.app import App
from plyer import notification

try: from jnius import autoclass
except:pass


def SavePic(camera, timestr):
    """SavePicは"""
    if platform == 'android':
        from jnius import autoclass     
        # AndroidのJavaクラスにアクセス
        Environment = autoclass('android.os.Environment')
        # Build_VERSION = autoclass('android.os.Build$VERSION')
        # Context = autoclass('android.content.Context')
        # MediaStore = autoclass('android.provider.MediaStore')
        # ContentValues = autoclass('android.content.ContentValues')
        # PythonActivity = autoclass('org.kivy.android.PythonActivity')

        # print('###### SDK VERSION ######'), print(int(Build_VERSION.SDK_INT))
        app_storage_path = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DCIM).getAbsolutePath()


        # # Scoped Storageが使用可能なAndroidバージョンかをチェック
        # if int(Build_VERSION.SDK_INT) >= 29:
        #     # アプリの外部ファイルディレクトリへのパスを取得
        #     # app_storage_path = PythonActivity.mActivity.getExternalFilesDir(None).getAbsolutePath()
        #     content_resolver = PythonActivity.mActivity.getContentResolver()
        #     values = ContentValues()
        #     image_uri = content_resolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values)
        #     app_storage_path = image_uri.getPath()

        # else:
        #     # Android 9以前の場合、従来のストレージアクセスを利用
        #     app_storage_path = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DCIM).getAbsolutePath()

    elif platform == 'win': 
        CSIDL_MYPICTURES = 39           # CSIDL_MYPICTURES の値は 39
        MAX_PATH = 260                  # 最大パス長

        # SHGetFolderPath 関数を呼び出すためのセットアップ        
        import ctypes
        shell32 = ctypes.windll.shell32
        buf = ctypes.create_unicode_buffer(MAX_PATH)
        shell32.SHGetFolderPathW(0, CSIDL_MYPICTURES, 0, 0, buf)

        app_storage_path = buf.value    # パスを取得

    filename = f"IMG_{timestr}.png"
    filepath = join(app_storage_path, filename)
    camera.export_to_png(filepath)
    try:
        camera.export_to_png(filename)
    except:
        pass

    return filepath


def show_toast(message):
    """show_toastは、受け取った文字列messageをtoast表示します。"""
    notification.notify(
        message=message,
        timeout=1,
        toast=True
    )

#内部の保存フォルダ
def internal_savefile_location():
    """内部ディレクトリの絶対パスを返す"""
    if platform == 'android':
        from android.storage import app_storage_path
        return app_storage_path()

    elif platform == 'win':
        return abspath('.')


def external_savefile_location():
    """外部ディレクトリの絶対パスを返す"""
    if platform == 'android':
        return 'この機能は準備中'

    elif platform == 'win': 
        CSIDL_MYPICTURES = 39           # CSIDL_MYPICTURES の値は 39
        MAX_PATH = 260                  # 最大パス長

        # SHGetFolderPath 関数を呼び出すためのセットアップ
        import ctypes
        shell32 = ctypes.windll.shell32
        buf = ctypes.create_unicode_buffer(MAX_PATH)
        shell32.SHGetFolderPathW(0, CSIDL_MYPICTURES, 0, 0, buf)

        return buf.value    # パスを取得
