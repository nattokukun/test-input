# -*- coding: utf-8 -*-
## https://torimakujoukyou.com/python-kivy-label-update/

#---------------------------------------------------------------------------------
#
#---------------------------------------------------------------------------------
from kivy.app import App
# import kivy
# kivy.require('1.11.0')

## from kivy.config import Config
from kivy.uix.widget import Widget
## from kivy.properties import ObjectProperty
## from kivy.lang import Builder
## import otherlib
## import xxsubtype

######################
from _userlib import cssys
from _userlib.cssys import debug_log
######################

# OpenGLの調整
cssys.adjust_opengl(3)

######## 日本語
if cssys.is_windows():
    import japanize_kivy
else:
    from kivy.core.text import LabelBase, DEFAULT_FONT  # [パターン２] デフォルトの表示フォントを
    from kivy.resources import resource_add_path        #              Userが指定する
    ## LabelBase.register(DEFAULT_FONT, "ipaexg00401/ipaexg.ttf") apkでNG
    resource_add_path("/system/fonts")
    ## LabelBase.register(DEFAULT_FONT, "NotoSansBuhid-Regular.ttf") NG
    LabelBase.register(DEFAULT_FONT, "NotoSansCJK-Regular.ttc")

##################################
## import textinput4ja
from _userlib import textinput4ja
##################################

#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------

################################
# アクティブ コントロールを得る
def get_active(p_widget):
                            # アクティブ id
                            # アクティブ インスタンス
    tp_id       = ''
    tp_item_act = None
    for tp_key, tp_item in p_widget.ids.items():
        try:
            if tp_item.focus:
                tp_id       = tp_key
                tp_item_act = tp_item
                break
            else:
                pass
        except:
            pass
    return tp_id, tp_item_act
################################

class XMainForm(Widget):
    def __init__(self, **kwargs):
        super(XMainForm, self).__init__(**kwargs)
        # super().__init__(**kwargs)
        self.form_init()
        print('* form_init exec')
    #----------------------------------------------
    #----------------------------------------------

    def on_focus(self, p_id_inst, p_on):
        """
        # アクティブを得る
        tp_id_name, tp_item = get_active(self)
        if tp_item == None:
            return
        """
########################
        if p_on:
            t_sw = 'on'
        else:
            t_sw = 'off'
        tp_text = p_id_inst.text
        print('focus '+ ' '+ t_sw + ':' + tp_text)
########################

    def InputEnter(self):
        # アクティブを得る
        tp_id, tp_item = get_active(self)
        if tp_item == None:
            return
        """
        print(tp_id)
        print(tp_item.text)
        """
########################
        tp_text = tp_item.text
        print('enter:' + tp_text)
########################

        # 結果表示
        tp_text = tp_item.text
        self.ids.button_under.text = f"Enter : {tp_text}"
        self.ids.total_1_1.text =  f"{tp_text}"

        # フォーカス移動
        if tp_id == 'input_1_1_1':
            self.ids.input_1_1_2.focus = True
        if tp_id == 'input_1_1_2':
            self.ids.input_1_1_3.focus = True
        if tp_id == 'input_1_1_3':
            self.ids.input_1_1_1.focus = True
        return

    def form_init_input(self, p_id):
        debug_log('is form_init_input exec')
        self.ids[p_id].width  = self.ids[p_id].width  / 2
        self.ids[p_id].height = self.ids[p_id].height / 2

    def form_init(self):
#############
##         return
#############
        # 先頭セット
        self.ids.input_1_1_1.focus = True

        debug_log('test.001')

        if cssys.is_windows():
            self.form_init_input('input_1_1_1')
            self.form_init_input('input_1_1_2')
            self.form_init_input('input_1_1_3')
            """
            #######
            self.ids.input1.width = self.ids.input1.width / 2
            self.ids['input2'].width = self.ids['input2'].width / 2
            #######
            """

    #----------------------------------------------
    #----------------------------------------------
    def ButtonTestPress(self):
        # print(os.path.getsize('D:\Jmap'))
        sz = otherlib.get_dir_size('D:\Jmap')
        self.ids.label3.text = f"{sz}"

    def ButtonPress(self):
        name = self.ids.input1.text
        self.ids.label2.text = f"Hello {name}!!"
        # self.ids.input1.text = ""


#---------------------------------------------------------------------------------
#                   App
#---------------------------------------------------------------------------------
def MainWidget():
                    # Root Widget
    tp_mf = XMainForm()
    """
    ## tp_mf.ids.label3.text = 'Oh My God'
    #######
    tp_mf.ids.input1.focus = True
    #######
    tp_mf.ids.input1.width = tp_mf.ids.input1.width / 2
    tp_mf.ids['input2'].width = tp_mf.ids['input2'].width / 2
    #######
    """
    debug_log('MainWidget')
    return tp_mf

###############################
def adapted_image_path(p_image_file_name):  # ファイル名
                                    # パス・フィル名
    IMAGE_DIR = '_images'
    """
    if cssys.is_android():
    # android launcher
        # 相対位置が分からないので、絶対パスにする

        import os
        from jnius   import autoclass
        from android import mActivity, activity
        from _userlib import fmng
        from _userlib.cssys import debug_log
        Uri  = autoclass('android.net.Uri')
        File = autoclass('java.io.File')

        t_dir_file_name = os.path.realpath(
                os.path.join( os.path.dirname(__file__), IMAGE_DIR, p_image_file_name )
        )

        ""
        debug_log('%%%%%%%%%%% ttt')
        debug_log(ttt)
        debug_log('%%%%%%%%%%% ttt')
        t_path = ttt
        ""

        # ファイルサイズを得る
        t_file = File(t_dir_file_name)
        t_uri =  Uri.fromFile(t_file)
        t_size = fmng.adr_get_file_size(t_uri)
        if t_size > 0:
            t_msg = f'exist file.. {t_dir_file_name}'
        else:
            t_msg = f'* not exist file! .. {t_dir_file_name}'


        debug_log(t_msg)
    else:
    # windows
        # 相対パス
        t_dir_file_name = IMAGE_DIR + '\\' + p_image_file_name
    """

    ############
    t_dir_file_name = IMAGE_DIR + '/' + p_image_file_name
    ############

    return t_dir_file_name
###############################


class MainApp(App):
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)
        # super().__init__(**kwargs)
        self.title = "Test Input"

###########################
    def image_path(self, p_file_name):
        return adapted_image_path(p_file_name)
###########################

    def build(self):    # Root Widget
        """
        tp_mf = XMainForm()
        ## tp_mf.ids.label3.text = 'Oh My God'
        #######
        ## tp_mf.ids.input1.focus = True
        #######
        ## tp_mf.ids.input1.width = tp_mf.ids.input1.width / 2
        ## tp_mf.ids['input2'].width = tp_mf.ids['input2'].width / 2
        #######
        return tp_mf
        """
        return MainWidget()

#---------------------------------------------------------------------------------
#                   Run
#---------------------------------------------------------------------------------
if __name__ == '__main__':
    MainApp().run()
