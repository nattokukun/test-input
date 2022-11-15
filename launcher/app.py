# -*- coding: utf-8 -*-

xxx_dir = 'launcher'

import sys
sys.path.append(xxx_dir)

"""
## kvファイルの明示的なロード
from kivy.lang import Builder
## self.root = Builder.load_file(xxx_dir+"/"+"test.kv")
Builder.load_file(xxx_dir+"/"+"test.kv")
"""



from kivy.app import App

class Launcher(App):
    def build(self):

        """
        xxx_dir = 'launcher'

        import sys
        sys.path.append(xxx_dir)
        """

        ## kvファイルの明示的なロード
        from kivy.lang import Builder
        self.root = Builder.load_file(xxx_dir+"/"+"test.kv")

        from mainxx import MainForm
        tp_mf = MainForm()
        tp_mf.form_init()
        return tp_mf
        #############

