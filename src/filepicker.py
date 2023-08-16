from jnius import autoclass

# JavaクラスをPythonで利用できるようにする
Uri = autoclass('android.net.Uri')
Intent = autoclass('android.content.Intent')
DocumentsContract = autoclass('android.provider.DocumentsContract')

# Request code for selecting a PDF document.
PICK_PDF_FILE = 2

def open_file(picker_initial_uri):
    intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
    intent.addCategory(Intent.CATEGORY_OPENABLE)
    intent.setType("application/pdf")

    # Optionally, specify a URI for the file that should appear in the
    # system file picker when it loads.
    intent.putExtra(DocumentsContract.EXTRA_INITIAL_URI, picker_initial_uri)

    # PythonActivityはKivyのアプリケーションで現在実行中のActivityを参照するためのクラスです
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    current_activity = PythonActivity.mActivity

    current_activity.startActivityForResult(intent, PICK_PDF_FILE)

