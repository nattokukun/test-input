# -*- coding: utf-8 -*-

from kivy import Config
Config.set('graphics', 'multisamples', '0')

"""
"""

from kivy.app import App
### from kivy.uix.label import Label

class Launcher(App):
    def build(self):

	xxx_dir = 'launcher'

        import sys
        ## sys.path.append('launcher')
        sys.path.append(xxx_dir)

        ## kvファイルの明示的なロード
        from kivy.lang import Builder
        self.root = Builder.load_file(xxx_dir+"/"+"test.kv")


        from mainxx import MainForm
        tp_mf = MainForm()
        tp_mf.form_init()
        return tp_mf
        #############

