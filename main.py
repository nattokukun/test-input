# -*- coding: utf-8 -*-

##----------------------------------------------------##
##          　　　　　ローカル定義
##----------------------------------------------------##
# ソースフォルダ
apps_dir = 'apps'

# ソースフォルダを設定
import sys
sys.path.append(apps_dir)

# kvファイルの明示的なロード
from kivy.lang import Builder
Builder.load_file(apps_dir+"/"+"main.kv")

# Appの定義
from kivy.app import App
class Apps(App):

    ##
    def image_path(self, p_file_name):
        ## return image_path(p_file_name)
        return apps_dir + "/_images/" + p_file_name
    ##

    def build(self):
        """ ##
        from mainxx import MainForm
        tp_mf = MainForm()
        return tp_mf
        ## """
        from mainxx import MainWidget
        return MainWidget()
##----------------------------------------------------##

def run_entrypoint(entrypoint):
    import runpy
    import sys
    import os
    entrypoint_path = os.path.dirname(entrypoint)
    sys.path.append(os.path.realpath(entrypoint_path))
    runpy.run_path(
        entrypoint,
        run_name="__main__")

##----------------------------------------------------##
##          　　　　　コメント
##----------------------------------------------------##
## def run_app(tb=None):
##     from apps.app import Apps
##     Apps().run()


def dispatch():
    ##----------------------------------------------------##
    ##          　　　　　コメント
    ##----------------------------------------------------##
    """
    import os

    # desktop launch
    print("dispathc!")
    entrypoint = os.environ.get("KIVYLAUNCHER_ENTRYPOINT")
    if entrypoint is not None:
        return run_entrypoint(entrypoint)
    """

    # try android
    try:
        from jnius import autoclass
        activity = autoclass("org.kivy.android.PythonActivity").mActivity
        intent = activity.getIntent()
        entrypoint = intent.getStringExtra("entrypoint")
        orientation = intent.getStringExtra("orientation")

        if orientation == "portrait":
            # SCREEN_ORIENTATION_PORTRAIT
            activity.setRequestedOrientation(0x1)
        elif orientation == "landscape":
            # SCREEN_ORIENTATION_LANDSCAPE
            activity.setRequestedOrientation(0x0)
        elif orientation == "sensor":
            # SCREEN_ORIENTATION_SENSOR
            activity.setRequestedOrientation(0x4)

        if entrypoint is not None:
            try:
                return run_entrypoint(entrypoint)
            except Exception:
                import traceback
                traceback.print_exc()
                return
    except Exception:
        import traceback
        traceback.print_exc()

    ##----------------------------------------------------##
    ##          　　　改修
    ##----------------------------------------------------##
    ## run_app()
    Apps().run()

if __name__ == "__main__":
    dispatch()
