# -*- coding: utf-8 -*-

#######
from kivy.lang import Builder
#######

"""
from kivy import Config
Config.set('graphics', 'multisamples', '0')
"""

from kivy.app import App
### from kivy.uix.label import Label

#############
xxx_dir = 'apps'
#############

#############
import sys
sys.path.append(xxx_dir)
#############

#############
## kvファイルの明示的なロード
Builder.load_file(xxx_dir+"/"+"main.kv")
## self.root = Builder.load_file(xxx_dir+"/"+"test.kv")
##self.root = Builder.load_file("test.kv")
#############

class Apps(App):

    def build(self):

        from mainxx import MainForm
        tp_mf = MainForm()
        ## tp_mf.form_init()
        return tp_mf
        #############

