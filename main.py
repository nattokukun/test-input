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


import cussys
from cussys import debug_log

# OpenGLの調整
cussys.adjust_opengl(3)

########
if cussys.is_windows():
    import japanize_kivy
else:
    from kivy.core.text import LabelBase, DEFAULT_FONT  # [パターン２] デフォルトの表示フォントを
    from kivy.resources import resource_add_path        #              Userが指定する
    ## resource_add_path("/ipaexg00401")
    ## LabelBase.register(DEFAULT_FONT, "Noto Sans CJK.ttf")
    LabelBase.register(DEFAULT_FONT, "ipaexg00401/ipaexg.ttf")
    pass
    ## import japanize_kivy
    pass
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

        if cussys.is_windows():
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
