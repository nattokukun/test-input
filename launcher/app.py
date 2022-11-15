# -*- coding: utf-8 -*-

#######
from kivy.lang import Builder
#######

from kivy import Config
Config.set('graphics', 'multisamples', '0')

from kivy.app import App
from kivy.uix.label import Label

class Launcher(App):

    def build(self):


        #############
        import sys
        sys.path.append('launcher')
        #############


        #############
        ## kvファイルの明示的なロード
        self.root = Builder.load_file("launcher/test.kv")
        ##self.root = Builder.load_file("test.kv")
        #############


        ## print('[1]')
        ## return Label(text="Hello World")

        #############
        # from launcher.app import Launcher

        from mainxx import MainForm
        tp_mf = MainForm()
        tp_mf.form_init()
        return tp_mf
        #############

