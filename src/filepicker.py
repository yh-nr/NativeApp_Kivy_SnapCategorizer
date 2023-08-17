from jnius import autoclass, PythonJavaClass, java_method
import json
from . import config_manager


# Request code for selecting a JSON document.
PICK_JSON_FILE = 42  # JSONファイルを選択するためのリクエストコードを定義します。

# JavaクラスをPythonで利用できるようにする
try:
    Uri = autoclass('android.net.Uri')
    Intent = autoclass('android.content.Intent')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
except:
    print('autoclassでエラーでたよ！！！！！！')
    print('autoclassでエラーでたよ！！！！！！')
    print('autoclassでエラーでたよ！！！！！！')



class ActivityResultEvent(PythonJavaClass):
    __javainterfaces__ = [ACTIVITY_CLASS_NAMESPACE + '$ActivityResultListener']
    __javacontext__ = 'app'

    def __init__(self, callback):
        super(ActivityResultEvent, self).__init__()
        self.callback = callback

    @java_method('(IILandroid/content/Intent;)V')
    def onActivityResult(self, requestCode, resultCode, intent):
        # ファイルピッカーからの結果を処理するメソッド
        if requestCode == PICK_JSON_FILE:
            if resultCode == -1:  # RESULT_OK
                uri = intent.getData()  # 選択されたファイルのURIを取得します。
                json_text = read_json_file(uri)
                json_data = json.loads(json_text)
                self.callback(json_data)  # コールバック関数を呼び出します

def open_file(picker_initial_uri):
    # ファイルピッカーを開くための関数
    intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
    intent.addCategory(Intent.CATEGORY_OPENABLE)
    intent.setType("application/json")  # JSONファイルのみを選択できるように設定します。
    current_activity = PythonActivity.mActivity
    current_activity.startActivityForResult(intent, PICK_JSON_FILE)

def read_json_file(uri):
    # URIからJSONファイルの内容を読み取る関数
    content_resolver = PythonActivity.mActivity.getContentResolver()
    stream = content_resolver.openInputStream(uri)
    
    json_text = ''
    buffer = bytearray(1024)
    while True:
        length = stream.read(buffer)
        if length == -1:
            break
        json_text += buffer[:length].decode('utf-8')
    
    stream.close()
    
    json_data = json.loads(json_text)  # JSONテキストをPythonのデータ構造に変換します。
    process_json_data(json_data)  # Pythonのデータ構造を別の関数に渡します。




# from jnius import autoclass  # Pyjniusのautoclass関数をインポートします。これを使用してJavaのクラスをPythonからアクセスできるようにします。

# # JavaクラスをPythonで利用できるようにする
# Uri = autoclass('android.net.Uri')  # AndroidのUriクラスをPythonで利用できるようにします。
# Intent = autoclass('android.content.Intent')  # AndroidのIntentクラスをPythonで利用できるようにします。
# DocumentsContract = autoclass('android.provider.DocumentsContract')  # AndroidのDocumentsContractクラスをPythonで利用できるようにします。

# # Request code for selecting a PDF document.
# PICK_PDF_FILE = 2  # PDFファイルを選択するためのリクエストコードを定義します。このコードは後で結果を受け取る際に使用します。

# def open_file(picker_initial_uri):  # open_fileという関数を定義します。この関数は、ファイルピッカーを開くために使用されます。
#     intent = Intent(Intent.ACTION_OPEN_DOCUMENT)  # OPEN_DOCUMENTアクションを持つ新しいIntentオブジェクトを作成します。これにより、ファイルピッカーが開きます。
#     intent.addCategory(Intent.CATEGORY_OPENABLE)  # カテゴリとしてOPENABLEを追加します。これにより、選択可能なファイルのみが表示されます。
#     intent.setType("application/pdf")  # ファイルピッカーで表示されるファイルのタイプをPDFに設定します。

#     # Optionally, specify a URI for the file that should appear in the
#     # system file picker when it loads.
#     intent.putExtra(DocumentsContract.EXTRA_INITIAL_URI, picker_initial_uri)  # オプションとして、ファイルピッカーが開いたときに表示される初期のURIを設定します。

#     # PythonActivityはKivyのアプリケーションで現在実行中のActivityを参照するためのクラスです
#     PythonActivity = autoclass('org.kivy.android.PythonActivity')  # Kivyアプリケーションで現在実行中のAndroidのActivityを参照するためのPythonActivityクラスを取得します。
#     current_activity = PythonActivity.mActivity  # 現在実行中のActivityのインスタンスを取得します。

#     current_activity.startActivityForResult(intent, PICK_PDF_FILE)  # startActivityForResultメソッドを使用して、ファイルピッカーを開き、後で結果を受け取ることができるようにします。

# # Example usage
# picker_initial_uri = Uri.parse("content://downloads/public_downloads")  # ファイルピッカーが開いたときに表示される初期のURIを設定します。ここではダウンロードフォルダを指定しています。
# open_file(picker_initial_uri)  # 上で定義したopen_file関数を呼び出して、ファイルピッカーを開きます。


# この関数を外部から呼び出す
def load_json_4android():    
    picker_initial_uri = Uri.parse("file:///sdcard/")
    open_file(picker_initial_uri)  # ファイルピッカーを開く関数を呼び出します。

    pass


def process_json_data(data):
    # JSONデータを処理する関数
    config_manager.save_config_to_file(config_manager.SETTINGS_FILE, data)
    print(data)  # ここではJSONデータを単に出力していますが、実際にはこのデータを使用して何らかの処理を行います。

    
# # KivyのPythonActivityにActivityResultListenerを追加します。
PythonActivity.mActivity.addActivityResultListener(process_json_data())