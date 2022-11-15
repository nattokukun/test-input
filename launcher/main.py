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
from _ast import Try
## import xxsubtype


import cssys
from cssys import debug_log

# OpenGLの調整
cssys.adjust_opengl(3)

########
if cssys.is_windows():
    import japanize_kivy
else:
    """
    import cssys
    if cssys.is_android():
        t_adr_ver = cssys.AndroidVersion()
        if t_adr_ver.is_10_11:
        # Android 10 以上
        # SDカードは許可されているが、Android/data 内が読めない
            t_access_ok = cssys.request_access_storage_10_11()
        else:
        # Android 10 未満
        # SDカードの許可が必要
            t_access_ok, t_sd_uri = cssys.request_access_storage_7_9()
        if not t_access_ok:
            raise Exception('Access Error!')
        else:
            print('******** ok')
    """

    """
    #######################
    import cssys
    t_ok, t_sd = cssys.request_access_storage()
    if not t_ok:
        raise Exception('cant access')
    #######################
    """

    """
    import cssys
    # 外部ストレージパス(実際は内部ストレージパス)を得る
    ## t_dir = cssys.adrd_get_external_storage_dir() + "/kivy/" + "ipaexg00401"
    t_dir = cssys.adrd_get_external_storage_dir() + \
            "/android/data/org.kivy.un_official_launcher/files/" + "ipaexg00401"
    t_fnt = 'ipaexg.ttf'
    t_fnt_path = t_dir + '/' + t_fnt
    ## t_dir = t_dir + 'xx'
    print('****************')
    print(t_fnt_path)
    print('****************')

    from jnius import autoclass
    Uri  = autoclass('android.net.Uri')
    File = autoclass('java.io.File')
    t_dir_uri = Uri.fromFile(File(t_fnt_path))
    import fmng
    # ファイルサイズを得る
    t_size = fmng.adr_get_file_size(t_dir_uri)
    print('*** File Size ')
    print(t_size)
    print('****************')
    """

    #######################
    from kivy.core.text import LabelBase, DEFAULT_FONT  # [パターン２] デフォルトの表示フォントを
    from kivy.resources import resource_add_path        #              Userが指定する
    ## LabelBase.register(DEFAULT_FONT, "ipaexg00401/ipaexg.ttf") apkでNG
    resource_add_path("/system/fonts")
    ## LabelBase.register(DEFAULT_FONT, "NotoSansBuhid-Regular.ttf") NG
    LabelBase.register(DEFAULT_FONT, "NotoSansCJK-Regular.ttc")
#########

##################################
import textinput4ja
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

class MainForm(Widget):
    def __init__(self, **kwargs):
        super(MainForm, self).__init__(**kwargs)
        # super().__init__(**kwargs)

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

###############

        """
###################
        if self.ids.input1.focus:
            print('on')
        else:
            print('off')
        if self.ids.input2.focus:
            print('on')
        else:
            print('off')
        print('---')
###################
        for key, val in self.ids.items():
            print(key)
            print(val)
            try:
                if val.focus:
                    print('on')
                else:
                    print('off')
            except:
                print('ng')
            print('**')
###################
        """
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
class TestApp(App):
    def __init__(self, **kwargs):
        super(TestApp, self).__init__(**kwargs)
        # super().__init__(**kwargs)
        self.title = "window"

    def build(self):    # Root Widget
        tp_mf = MainForm()
        """
        ## tp_mf.ids.label3.text = 'Oh My God'
        #######
        tp_mf.ids.input1.focus = True



        #######
        tp_mf.ids.input1.width = tp_mf.ids.input1.width / 2
        tp_mf.ids['input2'].width = tp_mf.ids['input2'].width / 2
        #######
        """
        tp_mf.form_init()
        return tp_mf

#---------------------------------------------------------------------------------
#                   Run
#---------------------------------------------------------------------------------
if __name__ == '__main__':
    TestApp().run()
