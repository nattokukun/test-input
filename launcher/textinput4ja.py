# -*- coding: utf-8 -*-

'''
textinput4ja.py
TextInput class for Japanese
Tested on macOS Monterey 12.6 and Android emulator api=33 using Kivy 2.1.0
MIT License
Copyright ©︎ 2022 bu
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
from kivy.utils import platform
from kivy.uix.textinput import TextInput, FL_IS_LINEBREAK, FL_IS_WORDBREAK
from kivy.properties import StringProperty, ListProperty, BooleanProperty, NumericProperty
from kivy.core.window import Window
from kivy.base import EventLoop
import copy
import re
from kivy.clock import Clock

##$#$##
ti4jp_prnt_on = False
def ti4jp_prnt(*args, **kwargs):
    if ti4jp_prnt_on:
        print("&&&&& ", end="")
        print(*args,**kwargs)
##$#$##

# Androidでの言語設定を取得
if platform == 'android':
    from jnius import autoclass
    Locale = autoclass('java.util.Locale')
    ti4jp_prnt('言語設定は...; ', Locale.getDefault().getLanguage())
#override TextInput
class TextInput_JA(TextInput):
    __events__ = ('on_text_validate', 'on_double_tap', 'on_triple_tap',
                  'on_quad_touch')
    _resolved_base_dir = None #よくわからん
    is_JP_ime_on = BooleanProperty() #日本語IMEの起動状態のフラグ
    is_lang_en = BooleanProperty()   #言語設定がEnglishかどうかのフラグ
    is_lang_ja = BooleanProperty()   #言語設定が日本語かどうかのフラグ
    is_android_ime_on = BooleanProperty() #androidでのIMEの起動状態のフラグ
    lines = ListProperty() #TextInputに入力されているテキストの行ごとのリスト
    alltext= StringProperty() #TextInputに入力済みの全テキスト
    add_to_end = BooleanProperty() #テキストの追加が入力済みテキストの末端への追加かどうかのフラグ
    del_by_bkspc = BooleanProperty()  #backspaceを押してテキストを消去したかどうかのフラグ
    _text_confirmed = BooleanProperty() #テキスト入力を確定したかどうかのフラグ
    _justbreaklined = BooleanProperty()  #テキスト入力して直後に改行されたかどうかのフラグ
    _row_start_of_typing = NumericProperty() #テキスト入力を始めた行を格納
    _ci_start_of_typing = NumericProperty() #テキスト入力を始めたときのcursor indexを格納
    def __init__(self, **kwargs):
        super(TextInput_JA, self).__init__(**kwargs)
        self.is_JP_ime_on = False #初期設定はFalseとする
        if platform == 'android':
            #言語設定を取得してフラグを立てておく
            if Locale.getDefault().getLanguage() == 'en':
                self.is_lang_en = True
                self.is_lang_ja = False
                ti4jp_prnt('self.is_lang_enは。。。。[', self.is_lang_en, '] です')
                ti4jp_prnt('self.is_lang_jaは。。。。[', self.is_lang_ja, '] です')
            elif Locale.getDefault().getLanguage() == 'ja':
                self.is_lang_en = False
                self.is_lang_ja = True
                ti4jp_prnt('self.is_lang_enは。。。。[', self.is_lang_en, '] です')
                ti4jp_prnt('self.is_lang_jaは。。。。[', self.is_lang_ja, '] です')
            else:
                self.is_lang_en = False
                self.is_lang_ja = False
                ti4jp_prnt('self.is_lang_enは。。。。[', self.is_lang_en, '] です')
                ti4jp_prnt('self.is_lang_jaは。。。。[', self.is_lang_ja, '] です')
        self.is_android_ime_on = False
        self.gcursor_index = self.cursor_index()
        self.lines = ['','']
        self.alltext = ''
        self.add_to_end = True
        self.del_by_bkspc = False
        self._text_confirmed = False
        self._justbreaklined = False
        self._row_start_of_typing = 0
        self._ci_start_of_typing = 0
    def do_backspace(self, from_undo=False, mode='bkspc'):
        '''Do backspace operation from the current cursor position.
        This action might do several things:
            - removing the current selection if available.
            - removing the previous char and move the cursor back.
            - do nothing, if we are at the start.
        '''
        ti4jp_prnt('')
        ti4jp_prnt('*****************************************************************')
        ti4jp_prnt('            ------ do_backspace() の実行中 ------                ')
        ti4jp_prnt('*****************************************************************')
        ti4jp_prnt('')
        ti4jp_prnt('self.del_by_bkspcは。。。; [',self.del_by_bkspc, '] です')
        ti4jp_prnt('self._text_confirmedは。。。; [',self._text_confirmed, '] です')
        ti4jp_prnt('self.is_lang_enは。。。。[', self.is_lang_en, '] です')
        ti4jp_prnt('self.is_android_ime_onは...; ', self.is_android_ime_on)
        ti4jp_prnt('self.is_JP_ime_onは........; ', self.is_JP_ime_on)
        # IME system handles its own backspaces
        #元のコードは if self._ime_composition:  となっていたが、これだとbackspaceが効かなくなってしまっていたので改良。
        #androidの場合はreadonlyの時だけreturn, android以外の時はis_JP_ime_onのときもreturn
        if platform == 'android':
            if self.readonly:
                ti4jp_prnt('android でreadonlyの設定なのでreturnします')
                ti4jp_prnt('*****************************************************************')
                ti4jp_prnt('        -- return によってdo_backspace を終了します --         ')
                ti4jp_prnt('*****************************************************************')
                return
        else:
            if self.readonly or self.is_JP_ime_on:
                ti4jp_prnt('readonlyもしくはis_JP_ime_onがTrueなのでreturnします')
                ti4jp_prnt('*****************************************************************')
                ti4jp_prnt('        -- return によってdo_backspace を終了します --         ')
                ti4jp_prnt('*****************************************************************')
                return
        ti4jp_prnt('::::   self.del_by_bkspc　を Trueにします   ::::')
        self.del_by_bkspc = True
        #以下、print文以外はオリジナルのコードのまま
        col, row = self.cursor
        _lines = self._lines
        _lines_flags = self._lines_flags
        text = _lines[row]
        cursor_index = self.cursor_index()
        if col == 0 and row == 0:
            return
        start = row
        if col == 0:
            if _lines_flags[row] == FL_IS_LINEBREAK:
                substring = u'\n'
                new_text = _lines[row - 1] + text
            else:
                substring = _lines[row - 1][-1] if len(_lines[row - 1]) > 0 \
                    else u''
                new_text = _lines[row - 1][:-1] + text
            self._set_line_text(row - 1, new_text)
            self._delete_line(row)
            start = row - 1
        else:
            # ch = text[col-1]
            substring = text[col - 1]
            new_text = text[:col - 1] + text[col:]
            self._set_line_text(row, new_text)
        # refresh just the current line instead of the whole text
        start, finish, lines, lineflags, len_lines = (
            self._get_line_from_cursor(start, new_text)
        )
        self._refresh_text_from_property(
            'insert' if col == 0 else 'del', start, finish,
            lines, lineflags, len_lines
        )
        self.cursor = self.get_cursor_from_index(cursor_index - 1)
        # handle undo and redo
        self._set_unredo_bkspc(
            cursor_index,
            cursor_index - 1,
            substring, from_undo, mode)
        ti4jp_prnt('')
        ti4jp_prnt('*****************************************************************')
        ti4jp_prnt('              -- do_backspace を終了しました --                  ')
        ti4jp_prnt('*****************************************************************')
        ti4jp_prnt('')
    # current IME composition in progress by the IME system, or '' if nothing
    _ime_composition = StringProperty('')
    # cursor position of last IME event
    _ime_cursor = ListProperty(None, allownone=True)
    def window_on_textedit(self, window, ime_input):
        #android用
        if platform == 'android':
            ti4jp_prnt('')
            ti4jp_prnt('******************************************************')
            ti4jp_prnt('--------- < window_on_textedit for android > ---------')
            ti4jp_prnt('******************************************************')
            ti4jp_prnt('')
            ti4jp_prnt('self._ime_composition;       ', self._ime_composition)
            ti4jp_prnt('ime_input;                   ', ime_input)
            ti4jp_prnt('self.cursor_index();         ', self.cursor_index())
            ti4jp_prnt('self.del_by_bkspc;           ', self.del_by_bkspc)
            ti4jp_prnt('self._ime_cursor;            ', self._ime_cursor)
            ti4jp_prnt('self._text_confirmed;        ', self._text_confirmed)
            ti4jp_prnt('self._justbreaklined;        ', self._justbreaklined)
            ti4jp_prnt('self.is_JP_ime_onは........; ', self.is_JP_ime_on)
            ti4jp_prnt('self.is_android_ime_onは...; ', self.is_android_ime_on, ' (直前でTrueに切り替えています) ')
            text_lines = self._lines or ['']        #text入力済み内容を保持
            self.is_android_ime_on = True           #window_on_textedit実行中のときはTrueになるように設定
            gcc, gcr = copy.deepcopy(self.cursor)   #カーソル位置を保持
            ci = self.cursor_index()                #カーソルインデックスを保持
            #新たに入力を始めたときの行とカーソルインデックスを保持
            if self._text_confirmed:
                self._row_start_of_typing = self.cursor[1]
                self._ci_start_of_typing = self.cursor_index()
            ti4jp_prnt('')
            ti4jp_prnt('text_lines; ', text_lines)
            ti4jp_prnt('gcc, gcr; ', gcc, gcr)
            ti4jp_prnt('ci; ', ci)
            ti4jp_prnt('self.is_lang_en; ', self.is_lang_en)
            #_ime_compositionを保持しているときとそうでないときで処理を分ける
            if self._ime_composition:
                ti4jp_prnt('')
                ti4jp_prnt('*********** < self._ime_compositionが存在するケースの処理 > **********')
                ti4jp_prnt('')
                pcc, pcr = self._ime_cursor     #入力中のテキストのカーソル位置を保持
                cc,cr = self.cursor             #カーソル位置を保持
                ti4jp_prnt('self._ime_cursor; ', self._ime_cursor)
                ti4jp_prnt('pcc, pcr; ', pcc,',',pcr)
                ti4jp_prnt('cc, cr; ', cc,',',cr)
                #改行がなかった場合はcr == pcrとなる。その場合はtext_linesで現在の行のpcrを指定する
                ti4jp_prnt('cr, pcr; ', cr, ',', pcr)
                ti4jp_prnt('self._justbreaklined; ', self._justbreaklined)
                if cr == pcr:
                    ti4jp_prnt('cr == pcrです')
                    text = text_lines[pcr]
                #改行があった場合はcr != pcrとなる。その場合はtext_linesで元の行pcrの1つ前の行を指定する
                #ただし、enterキーを押して改行された場合はpcrの行を指定する
                elif cr != pcr and self._justbreaklined:
                    ti4jp_prnt('cr != pcrですが直前に改行コードが入力されています')
                    text = text_lines[pcr]
                else:
                    ti4jp_prnt('cr != pcrです')
                    text = text_lines[pcr-1]
                ti4jp_prnt('text; ', text)
                len_ime = len(self._ime_composition) #_ime_compositionの長さを格納
                ti4jp_prnt('len_ime(_ime_compositionの長さ); ', len_ime)
                ti4jp_prnt('text[pcc - len_ime:pcc]; ', text[pcc - len_ime:pcc])
                ti4jp_prnt('self._ime_composition;   ', self._ime_composition)
                ti4jp_prnt('cr; ', cr)
                ti4jp_prnt('self.cursor[1]; ', self.cursor[1])
                #text入力中の未確定部分において改行が含まれているか否かによって処理を分ける
                #改行なし(たぶん)
                if text[pcc - len_ime:pcc] == self._ime_composition:  # always?
                    ti4jp_prnt('text[pcc - len_ime:pcc] == self._ime_compositionである=>改行なし（たぶん）')
                    ti4jp_prnt('text[cc:], ',text[cc:] )
                    ti4jp_prnt('len(text), ', len(text))
                    ti4jp_prnt('len(text[cc:]), ', len(text[cc:]))
                    ti4jp_prnt('text_lines[cr:], ',text_lines[cr:] )
                    ti4jp_prnt('len(text_lines[cr:]), ',len(text_lines[cr:]))
                    ti4jp_prnt('len(ime_input); ', len(ime_input))
                    #さらに、途中挿入か末端への追加かで条件分岐する
                    #textがime_inputより長く、text[cc:]が存在する、または以降の行が存在する => 途中挿入中ということ
                    if len(text) > len(ime_input) and len(text[cc:]) != 0 or len(text_lines[cr:]) > 1:
                        self.add_to_end = False #末端への追加では無い。
                        ti4jp_prnt('途中挿入中です')
                    else:
                        self.add_to_end = True #末端への追加なのでフラグを立てる
                        ti4jp_prnt('末端追加中です')
                    ci = self.cursor_index() #カーソルインデックスを格納しておく
                    ti4jp_prnt('ci', ci)
                    #textをrefreshする。ここのrefreshでは行にpcr, テキストにtextを使う
                    self._refresh_text_from_property(
                        "insert",
                        *self._get_line_from_cursor(pcr, text)
                    )
                    #カーソル位置をrefreshする
                    self.cursor = self.get_cursor_from_index(ci)
                    ti4jp_prnt('self.cursor = self.get_cursor_from_index(ci)')
                    ti4jp_prnt('self.cursor, ',self.cursor, ', ci',ci, ', len_ime', len_ime)
                    ti4jp_prnt('text_lines after refresh; ', text_lines)
                #改行あり（たぶん）
                else:
                    ti4jp_prnt('text[pcc - len_ime:pcc] == self._ime_compositionではない=>改行あり（たぶん）')
                    ci = self.cursor_index() #カーソルインデックスを格納しておく
                    ti4jp_prnt('ci', ci)
                    #途中挿入か末端への追加かで条件分岐させる。len(text)とlen(ime_input)との比較を基準にする。
                    if len(text) > len(ime_input):
                        ti4jp_prnt('ime_compositionあり、改行ありで途中挿入しています')
                        self.add_to_end = False #末端への追加では無い
                        ti4jp_prnt('')
                        alltext = copy.deepcopy(self.text) #sel.text全部を格納しておく
                        diff_ime_input = ime_input[len(alltext[ci:]):] #ime_inputとの差分を取得
                        diff_alltext = alltext[ci:] #alltextの差分を取得
                        ti4jp_prnt('diff_ime_input; ', diff_ime_input)
                        ti4jp_prnt('diff_alltext_post; ', diff_alltext)
                        self.add_to_end = False #末端への追加では無いのでFalseにしておく
                        #ただし、backspaceによって len(text) > len(ime_input)になった時とそうでないときで処理を分ける必要がある
                        if self.del_by_bkspc == False:
                            #テキストを挿入中
                            ti4jp_prnt('テキストを入れています')
                            #text全体を更新する
                            self.text = alltext[:ci - len(self._ime_composition)] + ime_input + alltext[ci:]
                            #カーソル位置を更新する
                            self.cursor = self.get_cursor_from_index(ci - len(self._ime_composition))
                            ti4jp_prnt('self.text =', alltext[:ci - len(self._ime_composition)],'+', ime_input,'+', alltext[ci:])
                            ti4jp_prnt('self.cursor; ', self.cursor)
                        else:
                            #backspaceでテキストを削除中
                            ti4jp_prnt('テキストを削除しています')
                            #text全体を更新する
                            self.text = self.text[:ci - 1] + self.text[ci:]
                            #カーソル位置を更新する
                            self.cursor = self.get_cursor_from_index(ci - len(self._ime_composition))
                            ti4jp_prnt('self.text =', self.text[:ci - 1],'+', self.text[ci:])
                            ti4jp_prnt('self.cursor', self.cursor)
                    else:
                        ti4jp_prnt('ime_compositionあり、改行ありで末端追加しています')
                        ti4jp_prnt('')
                        self.add_to_end = True #末端追加なのでフラグを立てる
                        #テキストをリフレッシュする
                        self._refresh_text_from_property(
                            "insert",
                            *self._get_line_from_cursor(self.cursor[1], text)
                        )
                        #カーソル位置をリフレッシュする
                        self.cursor = self.get_cursor_from_index(ci - len_ime)
                        ti4jp_prnt('self.text; ', self.text)
                        ti4jp_prnt('self.cursor; ', self.cursor)
                    #refreshをここでも実施。行はpcr, テキストはtextを使う
                    self._refresh_text_from_property(
                        "insert",
                        *self._get_line_from_cursor(pcr, text)
                    )
                    #カーソル位置をリフレッシュ
                    self.cursor = self.get_cursor_from_index(ci)
                    ti4jp_prnt('self.cursor = self.get_cursor_from_index(ci)')
                    ti4jp_prnt('self.cursor, ',self.cursor, ', ci',ci, ', len_ime', len_ime)
                    ti4jp_prnt('text_lines after refresh; ', text_lines)
            else:
                ti4jp_prnt('')
                ti4jp_prnt('*********** < self._ime_compositionがないケース > **********')
                ti4jp_prnt('')
                #何もしない
            if ime_input:
                ti4jp_prnt('')
                ti4jp_prnt('******** < ime_inputがあります > ********')
                ti4jp_prnt('')
                ti4jp_prnt('ime_input; ', ime_input)
                ti4jp_prnt('self._lines_flags', self._lines_flags)
                #_selectionがある時は削除
                if self._selection:
                    self.delete_selection()
                cc, cr = self.cursor #カーソル位置を格納
                ti4jp_prnt('cc, cr; ', cc, ',', cr)
                ti4jp_prnt('gcc, gcr; ', gcc, ',',gcr)
                #_ime_compositionがあるときとない時で処理を分ける
                if self._ime_composition:
                    ti4jp_prnt('')
                    ti4jp_prnt('self._ime_compositionあります。それは...; ', self._ime_composition)
                    #改行がなかった場合はcr == pcrとなる。text_linesにおけるcrを指定する
                    ti4jp_prnt('テキスト入力現時点での行とテキスト入力開始時の行の比較 cr, pcr; ', cr, ',', pcr)
                    if cr == pcr:
                        ti4jp_prnt('')
                        ti4jp_prnt('cr == pcrです') #改行なし
                        text = text_lines[cr]
                        ti4jp_prnt('text; ', text)
                        #テキスト入力が確定前かどうかで切り分ける必要性があるので確認しておく
                        ti4jp_prnt('self._text_confirmed; ', self._text_confirmed)
                        ti4jp_prnt('self._ime_cursor', self._ime_cursor)
                        #日本語入力の場合 、子音が入力されたときに改行され、母音が入力されたら改行なしの状態になるケースがあり、
                        #その場合はcr == pcr かつ text[pcc - len_ime:pcc] != self._ime_compositionの状態になっている。
                        #そのためここで分岐を入れて処理を分ける
                        if text[pcc - len_ime:pcc] != self._ime_composition:
                            ti4jp_prnt('')
                            ti4jp_prnt('text[pcc - len_ime:pcc] == self._ime_composition で は な い ですね')
                            #カーソル以降にテキストがないときとあるときで途中挿入か末端追加かを分けてフラグを立て直す
                            if len(text[cc:]) != 0:
                                self.add_to_end = False #末端への追加では無い
                                ti4jp_prnt('途中挿入中ってことですな')
                            else:
                                self.add_to_end = True #末端への追加である
                                ti4jp_prnt('末端追加中ってことですな')
                            #子音1つ分を削除する。で、ime_inputの最後の文字を入れる
                            new_text = text[:cc-1] + ime_input[len_ime-1:] + text[cc:]
                            ti4jp_prnt('new_text = text[:cc-1] + ime_input[len_ime-1:] + text[cc:]')
                            ti4jp_prnt(new_text,'=', text[:cc-1] ,'+', ime_input[len_ime-1:], '+', text[cc:])
                        #英数字入力の場合、text[pcc - len_ime:pcc] == self._ime_compositionである
                        #日本語入力でも途中挿入はtext[pcc - len_ime:pcc] == self._ime_compositionになる
                        else:
                            ti4jp_prnt('')
                            ti4jp_prnt('text[pcc - len_ime:pcc] == self._ime_composition で す ね')
                            #ここで、カーソルが最右端の場合はlen(text[cc:])が0になってしまうので条件分岐する
                            ti4jp_prnt('self._lines; ', self._lines)
                            ti4jp_prnt('self._lines[cr]; ', self._lines[cr])
                            ti4jp_prnt('self._lines[cr:]; ', self._lines[cr:])
                            ti4jp_prnt('len(self._lines[cr]); ', len(self._lines[cr]))
                            ti4jp_prnt('len(self._lines[cr:]); ', len(self._lines[cr:]))
                            ti4jp_prnt('cc; ', cc)
                            ti4jp_prnt('text[cc:]; ', text[cc:])
                            #末端にカーソルがあるときでは無い
                            if len(text[cc:]) != 0:
                                self.add_to_end = False #末端への追加では無い
                                ti4jp_prnt('')
                                ti4jp_prnt('途中挿入中ってことです')
                            #text[cc:]が存在しないかつ挿入位置が一番右側。かつ以降の行が存在する場合
                            elif len(text[cc:]) == 0 and cc == len(self._lines[cr]) and len(text_lines[cr:]) > 1:
                                self.add_to_end = False #末端への追加では無い
                                ti4jp_prnt('')
                                ti4jp_prnt('途中挿入中ってことです。 その2')
                                self.add_to_end = False #末端への追加では無い
                            #それ以外
                            else:
                                self.add_to_end = True #末端への追加である
                                ti4jp_prnt('')
                                ti4jp_prnt('末端追加中ってことです')
                            #入力中テキストの確定前と確定した後で処理を分ける
                            if self._text_confirmed == False:
                                ti4jp_prnt('')
                                ti4jp_prnt('変換確定前のnew_text')
                                new_text = text[:cc - len(self._ime_composition)] + ime_input + text[cc:]
                                ti4jp_prnt(new_text,'=', text[:cc-len(self._ime_composition)] ,'+', ime_input, '+', text[cc:])
                            else:
                                #確定後用は
                                ti4jp_prnt('')
                                ti4jp_prnt('変換確定後のnew_text')
                                new_text = text[:cc] + ime_input + text[cc:]
                                ti4jp_prnt('new_text = text[:cc] + ime_input + text[cc:]')
                                ti4jp_prnt(new_text,'=', text[:cc] ,'+', ime_input, '+', text[cc:])
                        #テキストをnew_textを使ってリフレッシュする
                        self._refresh_text_from_property(
                            "insert", *self._get_line_from_cursor(cr, new_text)
                        )
                        ti4jp_prnt('テキストのリフレッシュ done')
                    #改行があった場合はcr != pcrとなる。text_linesで元の行のpcr、およびpccを指定するしてtextとする
                    #ただし、enterキーを押して直前に改行されている場合は現在の行のcrおよびccを指定する
                    elif cr != pcr and self._justbreaklined:
                        ti4jp_prnt('')
                        ti4jp_prnt('cr != pcrですが直前に改行コードが入力されています')
                        text = text_lines[cr]
                        ti4jp_prnt('text; ', text)
                        new_text = text[:cc] + ime_input + text[cc:]
                        ti4jp_prnt('new_text = text[:cc] + ime_input + text[cc:]')
                        ti4jp_prnt(new_text,'=', text[:cc] ,'+', ime_input, '+', text[cc:])
                        #テキストをリフレッシュ
                        self._refresh_text_from_property(
                            "insert", *self._get_line_from_cursor(cr, new_text)
                        )
                        ti4jp_prnt('テキストのリフレッシュ done')
                    #enterキーを押しての直前の改行がない場合
                    else:
                        ti4jp_prnt('')
                        ti4jp_prnt('cr != pcrです')
                        text = text_lines[pcr]
                        ti4jp_prnt('text; ', text)
                        new_text = text[:pcc] + ime_input + text[pcc:]
                        ti4jp_prnt('new_text = text[:pcc] + ime_input + text[pcc:]')
                        ti4jp_prnt(new_text,'=', text[:pcc] ,'+', ime_input, '+', text[pcc:])
                        #テキストをリフレッシュ
                        self._refresh_text_from_property(
                            "insert", *self._get_line_from_cursor(pcr, new_text)
                        )
                        ti4jp_prnt('テキストのリフレッシュ done')
                    #カーソル位置のリフレッシュ
                    ti4jp_prnt('')
                    ti4jp_prnt('*** ime_compositionがある場合における、最後のカーソルのリフレッシュ段階 ***')
                    ti4jp_prnt('')
                    ti4jp_prnt('cc, cr; ', cc,',', cr)
                    ti4jp_prnt('self.cursor; ', self.cursor)
                    ti4jp_prnt('gcc, gcr; ', gcc,',', gcr)
                    ti4jp_prnt('self.cursor_index(); ',self.cursor_index())
                    ti4jp_prnt('len_ime; ', len_ime)
                    ti4jp_prnt('ci; ', ci)
                    ti4jp_prnt('self._justbreaklined; ', self._justbreaklined)
                    ti4jp_prnt('')
                    #末端への追加の場合とそうでない場合で処理を分ける
                    if self.add_to_end == True:
                        ti4jp_prnt('')
                        ti4jp_prnt('self.add_to_end == Trueなので、末端への追加の場合です')
                        #入力中の改行の有無で条件分岐。保持しているカーソル行crと現在のカーソル行の比較で検出
                        if cr == self.cursor[1]:
                            ti4jp_prnt('cr==self.cursor[1]なので入力中の改行はありません')
                            #カーソル位置は素直に新規に入力した分移動したものに更新する
                            self.cursor = self.get_cursor_from_index(
                                self.cursor_index() + len(ime_input)
                                )
                        else:
                            ti4jp_prnt('cr==self.cursor[1] で は な い ので入力中の改行が あ り ま す')
                            #カーソル位置はカーソルインデックスを元に更新する
                            self.cursor = self.get_cursor_from_index(
                                ci
                                )
                    else:
                        #backspaceで消している場合はself._ime_composition[:-1] == ime_inputとなる
                        #これを考慮してカーソル位置を更新する
                        ti4jp_prnt('self.add_to_end == Falseなので、途中挿入です')
                        ti4jp_prnt('ime_input; ', ime_input)
                        ti4jp_prnt('self._ime_composition; ', self._ime_composition)
                        self.cursor = self.get_cursor_from_index(
                            self.cursor_index() + len(ime_input) - len(self._ime_composition)
                            )
                    ti4jp_prnt('self.cursor_index()',self.cursor_index() )
                    ti4jp_prnt('len(ime_input)',len(ime_input) )
                    ti4jp_prnt('len(self._ime_composition); ', len(self._ime_composition))
                    ti4jp_prnt('カーソル位置のリフレッシュ done@self._ime_compositionがある場合の最後')
                    ti4jp_prnt('self.cursor; ', self.cursor)
                #########################################
                ###   self._ime_compositionがない場合 ###
                #########################################
                #現在のカーソル位置の行の文字列をrefresh
                else:
                    ti4jp_prnt('')
                    ti4jp_prnt('----- self._ime_compositionがない場合です -----')
                    ti4jp_prnt('ime_input; ', ime_input)
                    ti4jp_prnt('self.del_by_bkspc; ', self.del_by_bkspc)
                    text = text_lines[cr]
                    ti4jp_prnt('text; ', text)
                    #行の文字数と入力中テキストの文字数によって途中挿入か末端への追加かのフラグを更新
                    if len(text) > len(ime_input):
                        self.add_to_end = False #末端への追加では無い
                        ti4jp_prnt('')
                        ti4jp_prnt('途中挿入です')
                    else:
                        self.add_to_end = True #末端への追加である
                        ti4jp_prnt('')
                        ti4jp_prnt('末端追加です')
                    #言語が英語の時は。
                    #IME on/offの切り替えが起こるときの処理。必要ない?
                    if self.is_lang_en:
                        new_text = text[:cc] + ime_input[len(text[:cc]):] + text[cc:]
                        ti4jp_prnt('new_text = text[:cc] + ime_input[len(text[:cc]):] + text[cc:]')
                        ti4jp_prnt(new_text,'=', text[:cc] ,'+', ime_input[len(text[:cc]):], '+', text[cc:])
                    else:
                        new_text = text[:cc] + ime_input + text[cc:]
                        ti4jp_prnt('new_text = text[:cc] + ime_input + text[cc:]')
                        ti4jp_prnt(new_text,'=', text[:cc] ,'+', ime_input, '+', text[cc:])
                    ti4jp_prnt('self.cursor_index(); ', self.cursor_index())
                    #テキストをリフレッシュ
                    self._refresh_text_from_property(
                        "insert", *self._get_line_from_cursor(cr, new_text)
                    )
                    ti4jp_prnt('テキストのリフレッシュ done')
                    #カーソル位置を更新
                    self.cursor = self.get_cursor_from_index(
                    self.cursor_index() + len(ime_input)
                    )
                    ti4jp_prnt('カーソル位置の更新 done')
                    ti4jp_prnt('self.cursor; ', self.cursor)
            #ime_inputが無い時#back spaceが押されてime_inputが無い場合の処理
            #途中挿入の入力中に、backspaceでime_inputの文字数以上に削除した場合が該当する
            else:
                ti4jp_prnt('')
                ti4jp_prnt('----- ime_inputがありません, ime_input; [ ', ime_input,' ] -----')
                cc, cr = self.cursor
                ci = self.cursor_index()
                ti4jp_prnt('text; ', text)
                ti4jp_prnt('text_lines; ', text_lines)
                ti4jp_prnt('self.cursor; ', self.cursor)
                ti4jp_prnt('cc, cr, ci; ', cc,',', cr, ',', ci)
                #del_by_bkspcであることを確認
                if self.del_by_bkspc == True:
                    ti4jp_prnt('back spaceが押されてime_inputが無いのです')
                new_text = text[:cc-1] + ime_input + text[cc:]
                ti4jp_prnt('new_text = text[:cc -1] + ime_input + text[cc:]')
                ti4jp_prnt(new_text,'=', text[:cc - 1] ,'+', ime_input, '+', text[cc:])
                #テキストをリフレッシュ
                self._refresh_text_from_property(
                    "insert", *self._get_line_from_cursor(cr, new_text)
                )
                ti4jp_prnt('テキストのリフレッシュ done')
                ti4jp_prnt('self.cursor_index(); ', self.cursor_index())
                ti4jp_prnt('self.cursor; ', self.cursor)
                ti4jp_prnt('cc, cr, ci; ', cc,',', cr, ',', ci)
                #ime_input文字数を超えてbackspace押した時のカーソル位置を、
                #途中挿入か末端追加かで切り分けて処理
                #末端追加のとき
                if self.add_to_end == True:
                    ti4jp_prnt('self.add_to_endがTrue?; ', self.add_to_end)
                    if new_text == '':
                        ti4jp_prnt('new_textがありません')
                        ti4jp_prnt('最後列から入力を開始しその入力中に改行したケースです。')
                        ti4jp_prnt('行の最後列になるよう、textの最後の位置にカーソルを移します')
                        #この場合はcr-1行の最後の位置をindexとして使用する
                        self.cursor = self.get_cursor_from_index(
                            len(self.text)
                        )
                    else:
                        ti4jp_prnt('new_textが存在する場合は、現在のカーソルインデックスをそのまま採用します')
                        self.cursor = self.get_cursor_from_index(
                            self.cursor_index()
                        )
                #途中入力のとき
                else:
                    ti4jp_prnt('self.add_to_endがFalse?; ', self.add_to_end)
                    self.cursor = self.get_cursor_from_index(
                        self.cursor_index() - 1
                    )
                ti4jp_prnt('カーソル位置のリフレッシュ done')
                ti4jp_prnt('self.cursor; ', self.cursor)
                #このケースの時はself.is_android_ime_onをFalseに戻す。不要かもしれない。
                self.is_android_ime_on = False
                ti4jp_prnt('self.is_android_ime_onを...', self.is_android_ime_on, '...に戻しました')
            ti4jp_prnt('')
            ti4jp_prnt('---- window_on_texteditの最終処理ブロック ----')
            #_ime_compositionをime_inputで更新
            self._ime_composition = ime_input
            #_ime_cursorをself.cursorで更新
            self._ime_cursor = self.cursor
            ti4jp_prnt('self._ime_composition',self._ime_composition)
            ti4jp_prnt('self._ime_cursor; ', self._ime_cursor)
            #self._text_confirmed等ををFalseに戻す
            self._text_confirmed = False
            self._justbreaklined = False
            self.del_by_bkspc = False
            self.add_to_end = False
            ti4jp_prnt('self._text_confirmedを... ', self._text_confirmed, '...に戻しました')
            ti4jp_prnt('self._justbreaklinedを... ', self._justbreaklined, '...に戻しました')
            ti4jp_prnt('self.del_by_bkspcを... ', self.del_by_bkspc, '...に戻しました')
            ti4jp_prnt('self.add_to_endを... ', self.add_to_end, '...に戻しました')
            ti4jp_prnt('')
            ti4jp_prnt('***********************************************************')
            ti4jp_prnt('********* end of window_on_textedit for android ***********')
            ti4jp_prnt('***********************************************************')
            ti4jp_prnt('')
    ########################
    ####  android以外用  ###
    ########################
        else:
            ti4jp_prnt('')
            ti4jp_prnt('******************************************************')
            ti4jp_prnt('-------- < window_on_textedit for non-android> -------')
            ti4jp_prnt('******************************************************')
            self.gcursor_index = self.cursor_index()
            self.gcursor = self.cursor
            col, row = self.cursor
            _lines = self._lines
            text_lines = self._lines or ['']
            ti4jp_prnt('text@begining on window_on_textedit', self.text)
            ti4jp_prnt('self.text_validate_unfocus;', self.text_validate_unfocus)
            ti4jp_prnt('self.is_android_ime_onは...; ', self.is_android_ime_on)
            ti4jp_prnt('self.is_JP_ime_onは........; ', self.is_JP_ime_on)
            #if self._ime_composition and not ime_input:
            if self._ime_composition:
                ti4jp_prnt('')
                ti4jp_prnt('*********** < self._ime_compositionが存在するケースの処理 > **********')
                ti4jp_prnt('')
                pcc, pcr = self._ime_cursor
                ti4jp_prnt('更新前pcc, pcr', pcc,',', pcr)
                ti4jp_prnt('col, row', col,',', row)
                ti4jp_prnt('text_lines', text_lines)
                ti4jp_prnt('len(text_lines)', len(text_lines))
                #入力開始した行よりも下に行があるかないかでtextに採用する行を分ける
                if len(text_lines) >  pcr:
                    ti4jp_prnt('len(text_lines) > pcrです')
                    text = text_lines[pcr]
                else:
                    ti4jp_prnt('len(text_lines) > pcrではありません')
                    text = text_lines[pcr-1]
                ti4jp_prnt('text', text)
                #_ime_compositionの文字数を取得しておく
                len_ime = len(self._ime_composition)
                #改行がない時
                if text[pcc - len_ime:pcc] == self._ime_composition:  # always?
                    ti4jp_prnt('')
                    ti4jp_prnt('***** ime_compositionありで改行なし *****')
                    ti4jp_prnt('')
                    #入力行のテキストを更新する
                    remove_old_ime_text = text[:pcc - len_ime] + text[pcc:]
                    ci = self.cursor_index()
                    ti4jp_prnt('remove_old_ime_text = text[:pcc - len_ime] + text[pcc:]')
                    ti4jp_prnt(remove_old_ime_text,'=', text[:pcc - len_ime],'+',text[pcc:])
                    ti4jp_prnt('len_ime; ', len_ime)
                    ti4jp_prnt('ci; ', ci)
                    ti4jp_prnt('pcc; ', pcc)
                    ti4jp_prnt('text@if_ime_composition', self.text)
                    #ここ検討してスッキリさせる余地あり
                    #入力開始した行が現在のカーソルがある行と一致しているかどうかで処理を分ける
                    if pcr == self.cursor[1]:
                        ti4jp_prnt('pcr == self.cursor[1]です')
                        self._refresh_text_from_property(
                            "insert",
                            *self._get_line_from_cursor(pcr, remove_old_ime_text)
                        )
                    else:
                        ti4jp_prnt('pcr != self.cursor[1]です')
                        self._refresh_text_from_property(
                            "insert",
                            *self._get_line_from_cursor(self.cursor[1], remove_old_ime_text)
                        )
                    #カーソル位置は入力文字数分を戻して更新
                    self.cursor = self.get_cursor_from_index(ci - len_ime)
                    #IME開始直後はself.is_JP_ime_onがFalseなのでその時に入力されているテキストを取得し反映する
                    #保持しているカーソル位置はime_inputで取得しているccだとここでは定義されてないので使えないため、self. gcursorから取ってくる
                    if self.is_JP_ime_on == False:
                        gcc, gcr = self.gcursor
                        new_text = text[:gcc] + text[gcc:]
                        #テキストをリフレッシュ
                        self._refresh_text_from_property(
                            "insert", *self._get_line_from_cursor(gcr, new_text)
                        )
                        #new_textの長さを加味して修正したカーソル位置を更新
                        self.cursor = self.get_cursor_from_index(
                        self.cursor_index() + len(new_text)
                        )
                #改行があるとき
                else:
                    ti4jp_prnt('ime_compositionあり, else, 改行あり')
                    if len(text_lines) >  pcr:
                        text = text_lines[pcr]
                    else:
                        text = text_lines[pcr-1]
                    ti4jp_prnt('text = text_lines[pcr]; ', text)
                    ti4jp_prnt('self._lines_flags; ', self._lines_flags)
                    ti4jp_prnt('')
                    ti4jp_prnt('')
                    cc, cr = self.cursor
                    #remove_old_ime_text = ''としたら改行時に余計な文字が付かなくなって正常に動く。なぜかよくわからん。
                    remove_old_ime_text = ''
                    ci = self.cursor_index()
                    if len(text) > len(ime_input):
                        ti4jp_prnt('ime_compositionあり、改行ありでの。。。。途中挿入です')
                        ti4jp_prnt('')
                        ti4jp_prnt('ime_input', ime_input)
                        ti4jp_prnt('self._ime_composition',self._ime_composition)
                        ti4jp_prnt('len(ime_input)', len(ime_input))
                        ti4jp_prnt('len(self._ime_composition)', len(self._ime_composition))
                        #テキスト全体の取得と差分の取得
                        alltext = copy.deepcopy(self.text)
                        diff_ime_input = ime_input[len(alltext[ci:]):]
                        diff_alltext = alltext[ci:]
                        ti4jp_prnt('diff_ime_input; ', diff_ime_input)
                        ti4jp_prnt('diff_alltext_post; ', diff_alltext)
                        ti4jp_prnt('self.text[:ci]', self.text[:ci])
                        ti4jp_prnt('self.text[ci:]', self.text[ci:])
                        self.add_to_end = False
                        #テキストの挿入の時はime_input >= self._ime_compositionかつself.del_by_bkspc==Falseになる。
                        #そうでなければ削除操作中。それぞれで処理を分ける
                        if self.del_by_bkspc == False:
                            ti4jp_prnt('テキストを入れています')
                            self.text = alltext[:ci - len(self._ime_composition)] + ime_input + alltext[ci:]
                            self.cursor = self.get_cursor_from_index(ci - len(self._ime_composition))
                            ti4jp_prnt('self.text', self.text)
                            ti4jp_prnt('self.text =', alltext[:ci - len(self._ime_composition)],'+', ime_input,'+', alltext[ci:])
                            ti4jp_prnt('self.cursor', self.cursor)
                        else:
                            ti4jp_prnt('テキストを削除しています')
                            self.text = self.text[:ci - 1] + self.text[ci:]
                            self.cursor = self.get_cursor_from_index(ci - len(self._ime_composition))
                            ti4jp_prnt('self.text', self.text)
                            ti4jp_prnt('self.text =', self.text[:ci - 1],'+', self.text[ci:])
                            ti4jp_prnt('self.cursor', self.cursor)
                    else:
                        ti4jp_prnt('ime_compositionあり、改行ありでの末端挿入です')
                        ti4jp_prnt('')
                        self.add_to_end = True #フラグを更新
                        #改行があるかどうかを入力開始行と現在の行の比較で検出し、改行の有無で処理を分ける
                        if pcr == self.cursor[1]:
                            ti4jp_prnt('gcr == self.cursor[1]です')
                            self._refresh_text_from_property(
                                "insert",
                                *self._get_line_from_cursor(pcr, remove_old_ime_text)
                            )
                        else:
                            ti4jp_prnt('pcr != self.cursor[1]です')
                            self._refresh_text_from_property(
                                "insert",
                                *self._get_line_from_cursor(self.cursor[1], remove_old_ime_text)
                            )
                        self.cursor = self.get_cursor_from_index(ci - len_ime)
                        ti4jp_prnt('self.text', self.text)
                        ti4jp_prnt('self.cursor', self.cursor)
                    #IME開始直後はself.is_JP_ime_onがFalseなのでその時に入力されているテキストを取得し反映する
                    #カーソル位置はime_inputで取得しているccは定義されてないので使えないためself. gcursorを使う
                    if self.is_JP_ime_on == False:
                        gcc, gcr = self.gcursor
                        ti4jp_prnt('self.cursor', self.cursor)
                        ti4jp_prnt('gcc, gcr', gcc, ',', gcr)
                        new_text = text[:gcc] + text[gcc:] #これでうまくいった。
                        ti4jp_prnt(new_text)
                        ti4jp_prnt('new_text = text[:gcc] + text[gcc:]')
                        ti4jp_prnt(new_text,'=', text[:gcc],'+', text[gcc:])
                        ti4jp_prnt('@else; new_text@is_JP_ime_onがFalseのとき', new_text)
                        if gcr == self.cursor[1]:
                            ti4jp_prnt('gcr == self.cursor[1]です')
                            self._refresh_text_from_property(
                                "insert", *self._get_line_from_cursor(gcr, new_text)
                            )
                        else:
                            ti4jp_prnt('gcr != self.cursor[1]です')
                            self._refresh_text_from_property(
                                "insert", *self._get_line_from_cursor(self.cursor[1], new_text)
                            )
                        #new_textの長さを加味してカーソル位置を更新
                        self.cursor = self.get_cursor_from_index(
                        self.cursor_index() + len(new_text)
                        )
            if ime_input:
                ti4jp_prnt('')
                ti4jp_prnt('******** < ime_inputがあります > ********')
                ti4jp_prnt('')
                ti4jp_prnt('text@else_ime_input', self.text)
                if self._selection:
                    self.delete_selection()
                #_ime_compositionがあるかどうかで処理を分ける
                if self._ime_composition:
                    ti4jp_prnt('text@if_ime_input+ime_composition', self.text)
                    #改行しないとき
                    if text[pcc - len_ime:pcc] == self._ime_composition:  # always?
                        ti4jp_prnt('***** ime_inputありで改行なし *****')
                        cc, cr = self.cursor
                        ti4jp_prnt('最初のcc, cr', cc, cr)
                        text = text_lines[cr]
                        ti4jp_prnt('text@テキスト変数後ifif_ime_input+ime_composition', self.text)
                        ti4jp_prnt('text', text)
                        #original
                        new_text = text[:cc] + ime_input + text[cc:]
                        ti4jp_prnt('new_text = text[:cc] + ime_input + text[cc:] ;', new_text, '=', text[:cc],'+', ime_input,'+', text[cc:])
                        ti4jp_prnt('self.cursor_index(); ', self.cursor_index())
                    #改行するとき new_textをtext(カーソルより前),ime_input, text(カーソルより後ろ)を元にして生成
                    else:
                        ti4jp_prnt('***** ime_inputありで改行あり *****')
                        #いろいろ取得しておく
                        cc, cr = self.cursor
                        pcc, pcr = self._ime_cursor
                        text = text_lines[cr]
                        alltext = copy.deepcopy(self.text)
                        ci = self.cursor_index()
                        diff_ime_input = ime_input[len(alltext[ci:]):]
                        diff_alltext = alltext[ci:]
                        ti4jp_prnt('self.text', self.text)
                        ti4jp_prnt('text(text_lines[cr])', text)
                        ti4jp_prnt('最初のcc, cr (',cc,',',cr,')')
                        ti4jp_prnt('最初のpcc, pcr','(', pcc, ',',pcr,')')
                        ti4jp_prnt('ci', ci)
                        ti4jp_prnt('alltext', alltext)
                        ti4jp_prnt('ime_input', ime_input)
                        ti4jp_prnt('self._ime_composition; ', self._ime_composition)
                        ti4jp_prnt('diff_ime_input; ', diff_ime_input)
                        ti4jp_prnt('diff_alltext_post; ', diff_alltext)
                        ti4jp_prnt('alltext[:ci] , alltext[ci:] ;', alltext[:ci],',', alltext[ci:])
                        ti4jp_prnt('text[:cc] , text[cc:] ;', text[:cc],',', text[cc:])
                        #末尾への挿入か途中挿入かで切り分け
                        if self.add_to_end == True:
                            #テキストの挿入の時はlen(ime_input) >= len(self._ime_composition)になる。
                            #そうでなければ削除操作中
                            if len(ime_input) >= len(self._ime_composition):
                                ti4jp_prnt('***** ime_inputあり改行あり での末端への挿入です *****')
                                ti4jp_prnt('new_text = text[:cc] + ime_input + alltext[ci:][len(ime_input)-1:]')
                                ti4jp_prnt('new_text', '=', text[:cc], '+', ime_input, '+', alltext[ci:][len(ime_input)-1:])
                                new_text = text[:cc] + ime_input + alltext[ci:][len(ime_input)-1:]
                            else:
                                ti4jp_prnt('***** ime_inputあり, else, 改行あり での末端でのBackspaceによる行削除、または変換に伴う行削除です *****')
                                ti4jp_prnt('new_text = text[:cc] + ime_input + alltext[ci:][len(ime_input)-1:]')
                                ti4jp_prnt('new_text', '=', text[:cc], '+', ime_input)
                                new_text = text[:cc] + ime_input
                        #途中挿入の時
                        else:
                            #テキストの挿入の時はself.del_by_bkspc==Falseになる。
                            #そうでなければ削除操作中
                            if self.del_by_bkspc == False:
                                ti4jp_prnt('***** ime_inputありで改行あり での途中への挿入です *****')
                                ti4jp_prnt('new_text = text[:cc] + text[cc:]')
                                ti4jp_prnt('new_text', '=', text[:cc], '+', text[cc:])
                                new_text = text[:cc] + text[cc:]
                            else:
                                ti4jp_prnt('***** ime_inputあり, else, 改行あり での途中でのBackspaceによる行削除です *****')
                                ti4jp_prnt('new_text = text[:cc] + text[cc:]')
                                ti4jp_prnt('new_text', '=', text[:cc], '+', text[cc:])
                                new_text = text[:cc] + text[cc:]
                else:
                    ti4jp_prnt("window_on_textでの最初の処理")
                    cc, cr = self.cursor
                    text = text_lines[cr]
                    ti4jp_prnt('text@一番最初テキスト更新', self.text)
                    #new_textを作成する
                    new_text = text[:cc] + ime_input + text[cc:]
                #リフレッシュする
                ti4jp_prnt('テキストのリフレッシュを実施')
                self._refresh_text_from_property(
                    "insert", *self._get_line_from_cursor(cr, new_text)
                )
                #カーソル位置の更新
                self.cursor = self.get_cursor_from_index(
                    self.cursor_index() + len(ime_input)
                )
            #_ime_compositionをime_inputで更新
            self._ime_composition = ime_input
            #_ime_cursorを現在のカーソル位置で更新
            self._ime_cursor = self.cursor
            #is_JP_ime_onをTrueに戻す
            self.is_JP_ime_on = True
            #del_by_bkspcをFalseに戻す
            self.del_by_bkspc = False
            ti4jp_prnt('ime_input; ', ime_input)
            ti4jp_prnt('ime_input_isalnum(); ', ime_input.isalnum())
            ti4jp_prnt('ime_input_isascii(); ', ime_input.isascii())
            ti4jp_prnt('ime_input_isalpha(); ', ime_input.isalpha())
            ti4jp_prnt('')
            ti4jp_prnt('***********************************************************')
            ti4jp_prnt('******* end of window_on_textedit for non-android *********')
            ti4jp_prnt('***********************************************************')
            ti4jp_prnt('')
    def insert_text(self, substring, from_undo=False):
        '''Insert new text at the current cursor position. Override this
        function in order to pre-process text for input validation.
        '''
        ti4jp_prnt('')
        ti4jp_prnt('')
        ti4jp_prnt('*************************************************')
        ti4jp_prnt('************* start of insert_text **************')
        ti4jp_prnt('*************************************************')
        ti4jp_prnt('')
        ti4jp_prnt('self.is_android_ime_onは...; ', self.is_android_ime_on)
        ti4jp_prnt('self.is_JP_ime_onは........; ', self.is_JP_ime_on)
        ti4jp_prnt('')
        _lines = self._lines
        _lines_flags = self._lines_flags
        self.gcursor = self.cursor
        ti4jp_prnt('@insert_text  substring; ', substring)
        #ここ必要ないかもしれない
        if platform == 'android':
            if substring.isascii() == False:
                ti4jp_prnt('isasii()が [False] なので self.is_JP_ime_onを [True] にします')
                self.is_JP_ime_on = True
            else:
                ti4jp_prnt('isasii()が [True] なので self.is_JP_ime_onを [False] にします')
                self.is_JP_ime_on = False
        if self.readonly or not substring or not self._lines:
            ti4jp_prnt('')
            ti4jp_prnt('self.readonly; ', self.readonly)
            ti4jp_prnt('substring;,    ', substring)
            ti4jp_prnt('self._lines;,  ', self._lines)
            ti4jp_prnt('self.readonly or not substring or not self._linesなのでreturnします')
            ti4jp_prnt('')
            return
        if isinstance(substring, bytes):
            substring = substring.decode('utf8')
        if self.replace_crlf:
            substring = substring.replace(u'\r\n', u'\n')
        self._hide_handles(EventLoop.window)
        if not from_undo and self.multiline and self.auto_indent \
                and substring == u'\n':
            substring = self._auto_indent(substring)
        mode = self.input_filter
        if mode not in (None, 'int', 'float'):
            substring = mode(substring, from_undo)
            if not substring:
                return
        col, row = self.cursor
        cindex = self.cursor_index()
        text = _lines[row]
        len_str = len(substring)
        ti4jp_prnt('col, row; ',col, ',', row)
        ti4jp_prnt('cindex;   ', cindex, ' (self.ccursor_index()) ')
        ti4jp_prnt('text;     ',text, ' (_lines[row])')
        ti4jp_prnt('len_str;  ', len_str)
        ti4jp_prnt("substring が改行コードだけ?      ", substring == u'\n' )
        ti4jp_prnt("substring に改行コードが含まれる?", u'\n' in substring )
        ti4jp_prnt('text = text[:col] + text[col:]')
        ti4jp_prnt(text, '=', text[:col], '+', text[col:])
        ti4jp_prnt('len(text[col:]); ', len(text[col:]))
        #改変ここから
        #ここで末端追加か途中挿入かのフラグを立てておく 必要ないかも
        ti4jp_prnt('')
        ti4jp_prnt('len(text[col:]) == 0 かどうかで末端追加か途中挿入かのフラグを立てる')
        if len(text[col:]) == 0:
            self.add_to_end = True
            ti4jp_prnt('self.add_to_endをTrueにしました')
        else:
            self.add_to_end = False
            ti4jp_prnt('self.add_to_endをFalseにしました')
        #androidかそうでないかで分ける
        #androidでないとき
        if platform != 'android':
            ti4jp_prnt('')
            ti4jp_prnt('*********************')
            ti4jp_prnt('* android以外の場合 *')
            ti4jp_prnt('*********************')
            ti4jp_prnt('')
            #改行コードの入力の有無により条件分岐
            if substring == u'\n':
                #IMEがONの時は改行コードを入れずに改行しないようにする。IMEがOFFの時は改行コードを入れて改行する。
                if self.is_JP_ime_on == True:
                    #is_JP_ime_onをFalseに設定
                    self.is_JP_ime_on = False
                    new_text = text[:col] + text[col:]
                else:
                    new_text = text[:col] + u'\n' + text[col:]
                    ##カーソルの表示が一行下になるように更新する
                    Clock.schedule_once(lambda x: self.cursor_update(self.cursor), 0.1)
            else:
                if self.is_JP_ime_on == True:
                    #is_JP_ime_onをFalseに設定
                    self.is_JP_ime_on = False
                    new_text = text[:col] + text[col:]
                else:
                    #ime_compositionとsubstringが同じだったらIMEがOFF(？)に切り替わった直後なので、
                    #生成テキストの重複を避けるためsubstringを使わずにnew_textを生成し、substringと_ime_compositionの内容を消去
                    if self._ime_composition==substring:
                        substring = ''
                        self._ime_composition = ''
                        new_text = text[:col] + text[col:]
                    else:
                        new_text = text[:col] + substring + text[col:]
            if mode is not None:
                if mode == 'int':
                    if not re.match(self._insert_int_pat, new_text):
                        return
                elif mode == 'float':
                    if not re.match(self._insert_float_pat, new_text):
                        return
            self._set_line_text(row, new_text)
            # len_strはsubstringの長さ
            if len_str > 1 or substring == u'\n' or\
                (substring == u' ' and _lines_flags[row] != FL_IS_LINEBREAK) or\
                (row + 1 < len(_lines) and
                 _lines_flags[row + 1] != FL_IS_LINEBREAK) or\
                (self._get_text_width(
                    new_text,
                    self.tab_width,
                    self._label_cached) > (self.width - self.padding[0] -
                                           self.padding[2])):
                # Avoid refreshing text on every keystroke.
                # Allows for faster typing of text when the amount of text in
                # TextInput gets large.
                (
                    start, finish, lines, lines_flags, len_lines
                ) = self._get_line_from_cursor(row, new_text)
                # calling trigger here could lead to wrong cursor positioning
                # and repeating of text when keys are added rapidly in a automated
                # fashion. From Android Keyboard for example.
                self._refresh_text_from_property(
                    'insert', start, finish, lines, lines_flags, len_lines
                )
            ti4jp_prnt('')
            ti4jp_prnt('self.is_JP_ime_on; ', self.is_JP_ime_on)
            ti4jp_prnt('self.add_to_end; ', self.add_to_end)
            ti4jp_prnt('cindex; ', cindex)
            ti4jp_prnt('self.text[cindex:]; ', self.text[cindex:])
            ti4jp_prnt('substring; ', substring)
            ti4jp_prnt('self.ime_composition; ', self._ime_composition)
            ti4jp_prnt('len_str; ', len_str)
            #IMEがONで入力した時は
            #cindexの位置(insert_textに入った時のself.cursor.index()の戻り値)よりも
            #後ろに何もついていなければ末尾追加なので、len_str分カーソル位置を移動
            #後ろに文字がついていれば挿入追加なので、カーソル位置はそのまま
            # isalnum()を使って、
            #substringが半角英数字のみ、またはlen(self.text[ciindex:])==0のときはlen_strを追加する。
            #それ以外（つまりIME ONで挿入追加を行った時）はカーソル位置はそのまま
            ti4jp_prnt('substring.isascii(); ', substring.isascii())
            if substring.isalnum() or len(self.text[cindex:]) == 0:
                self.cursor = self.get_cursor_from_index(cindex + len_str)
            # handle undo and redo
            self._set_unredo_insert(cindex, cindex + len_str, substring, from_undo)
            #is_JP_ime_onをFalseに設定
            self.is_JP_ime_on = False
            ti4jp_prnt('self.is_JP_ime_onを; ', self.is_JP_ime_on, ' に更新しました')
            ti4jp_prnt('')
            ti4jp_prnt('*******************************************************************')
            ti4jp_prnt('*************** end of insert_text(android以外) *******************')
            ti4jp_prnt('*******************************************************************')
            ti4jp_prnt('')
        #################
        # androidの場合 #
        #################
        else:
            ti4jp_prnt('')
            ti4jp_prnt('********************')
            ti4jp_prnt('androidの場合')
            ti4jp_prnt('********************')
            ti4jp_prnt('')
            ti4jp_prnt('self.text;   ', self.text)
            ti4jp_prnt('self.cursor; ', self.cursor)
            ti4jp_prnt('col, row;    ', col, row)
            ti4jp_prnt('cindex;      ', cindex)
            ti4jp_prnt('text = _lines[row];     ', text)
            ti4jp_prnt('len_str=len(substring); ', len_str)
            ti4jp_prnt('substring;              ', substring)
            ti4jp_prnt('self._ime_composition;  ', self._ime_composition)
            '''Insert new text at the current cursor position. Override this
            function in order to pre-process text for input validation.
            '''
            text_lines = self._lines
            cc, cr = self.cursor
            ti4jp_prnt('text_lines;           ', text_lines)
            ti4jp_prnt('text_lines[cr];       ', text_lines[cr])
            ti4jp_prnt('text_lines[cr:];      ', text_lines[cr:])
            ti4jp_prnt('len(text_lines[cr]);  ', len(text_lines[cr]))
            ti4jp_prnt('len(text_lines[cr:]); ', len(text_lines[cr:]))
            ti4jp_prnt('cc, cr;               ', cc, ',', cr)
            ti4jp_prnt('text[cc:];            ', text[cc:])
            #末端追加か途中挿入かを判定して処理を分ける
            #textがime_inputより長くて、text[cc:]が存在する。または以降の行が存在する => ime_inputが無いので使えません
            ti4jp_prnt('')
            ti4jp_prnt('len(text[cc:] != 0 かどうかにより、末端追加か途中挿入かを判定します')
            if len(text[cc:]) != 0:
                self.add_to_end = False #末端への追加では無い
                ti4jp_prnt('')
                ti4jp_prnt('@insert_textで[途中挿入中]と判定されました(次以降の行が存在しない)')
            #text[cc:]が存在しないかつ挿入位置が一番右側だ。かつ以降の行が存在する
            elif len(text[cc:]) == 0 and cc == len(self._lines[cr]) and len(text_lines[cr:]) > 1:
                self.add_to_end = False #末端への追加では無い
                ti4jp_prnt('')
                ti4jp_prnt('@insert_textで[途中挿入中]と判定されました。その２(次以降の行が存在する)')
            else:
                self.add_to_end = True #末端への追加である
                ti4jp_prnt('')
                ti4jp_prnt('@insert_textで[末端追加中]と判定されました')
            #substringに改行コードが含まれていない => 変換が確定。この直後かそうでないかで処理を分ける。
            ti4jp_prnt('')
            ti4jp_prnt('substringに改行コードが含まれていない => 変換が確定')
            ti4jp_prnt('かつ変換確定直後かそうでないかを確認して処理を分ける')
            if u'\n' not in substring:
                ti4jp_prnt('')
                ti4jp_prnt("変換を確定しました。たぶん")
                self._text_confirmed = True
                ti4jp_prnt('self._text_confirmed を... ', self._text_confirmed, ' ...に更新しました')
            else:
                ti4jp_prnt('substringに改行コードが含まれていないので、改行だけです。たぶん')
                self._justbreaklined = True  #フラグを更新
                ti4jp_prnt('self._justbreaklined を... ', self._justbreaklined, ' ...に更新しました')
                ti4jp_prnt('self._text_confirmed は... ', self._text_confirmed, ' ...のままです')
            ti4jp_prnt('')
            ti4jp_prnt('改行コードが含まれている場合 => 改行コードのみが入力されたときとそれ以外で分ける')
            #改行コードが含まれている場合。改行コードのみが入力されたときとそれ以外で分ける
            if substring == u'\n':
                ti4jp_prnt('')
                ti4jp_prnt('改行コードのみが入力されています')
                ti4jp_prnt('')
                new_text = text[:col] + substring + text[col:]
                #下に設定している、[カーソル位置の最終的なリフレッシュ] での分岐2に相当するので、後でリフレッシュされないため、ここでリフレッシュ
                ti4jp_prnt('分岐2に相当するので、後でリフレッシュされないため、ここでリフレッシュ')
                (
                    start, finish, lines, lines_flags, len_lines
                ) = self._get_line_from_cursor(row, new_text)
                # calling trigger here could lead to wrong cursor positioning
                # and repeating of text when keys are added rapidly in a automated
                # fashion. From Android Keyboard for example.
                self._refresh_text_from_property(
                    'insert', start, finish, lines, lines_flags, len_lines
                )
                ti4jp_prnt('テキストのリフレッシュが終了しました')
            elif u'\n' in substring and substring != u'\n':
                ti4jp_prnt('-----')
                ti4jp_prnt('substring==改行コード ではないけど、改行コードがsubstringに入っています')
                ti4jp_prnt('-----')
                #この分岐の時も変換後の文字列にリフレッシュする機会がないようなので、ここで実施する。
                new_text = text[:col] + text[col:]
                ti4jp_prnt('new_text = text[:col] + text[col:]')
                ti4jp_prnt(new_text,'=', text[:col],'+', text[col:])
                #このケースの時はself.is_android_ime_onをFalseに戻す
                ti4jp_prnt('このケースの時はself.is_android_ime_onをFalseに戻す')
                self.is_android_ime_on = False
                ti4jp_prnt('self.is_android_ime_onを...', self.is_android_ime_on, '...に戻しました')
            else:
                ti4jp_prnt('')
                ti4jp_prnt('改行コードは入っていません')
                ti4jp_prnt('')
                ti4jp_prnt('substring == self._ime_composition のときは変換候補からの選択による変換なしで挿入')
                ti4jp_prnt(' => len(substring)を引いておく')
                ti4jp_prnt('substring == self._ime_composition ではないときは変換候補から選択しての挿入')
                ti4jp_prnt(' => len(self._ime_composition)を引いておく')
                ti4jp_prnt('')
                #substring == self._ime_compositionのときは変換候補からの変換なしで挿入
                # => len(substring)を引いておく
                #substring == self._ime_compositionではないときは変換候補から選択しての挿入
                # => len(self._ime_composition)を引いておく
                if substring == self._ime_composition:
                    ti4jp_prnt('----------')
                    ti4jp_prnt('substring == self._ime_composition が True です')
                    ti4jp_prnt('----------')
                    ti4jp_prnt('-------------------------------------------------')
                    ti4jp_prnt('substring == self._ime_composition が True です  ')
                    ti4jp_prnt(' 変換候補から選択せずに挿入 です                 ')
                    ti4jp_prnt('-------------------------------------------------')
                    #substringに改行コードが含まれていない => 変換が確定。変換直後かそうでないかで切り分ける。
                    ti4jp_prnt('substringに改行コードが含まれていない => 変換が確定。変換直後かそうでないかで切り分ける。')
                    if self._text_confirmed:
                        ti4jp_prnt('----------')
                        ti4jp_prnt('self._text_confirmedがTrue?; ', self._text_confirmed)
                        new_text = text[:col] + text[col:]
                        ti4jp_prnt('new_text = text[:col] + text[col:]')
                        ti4jp_prnt(new_text,'=', text[:col],'+', text[col:])
                        ti4jp_prnt('')
                        ti4jp_prnt('_ime_compositionをリセット')
                        #compositionをリセット
                        self._ime_composition = ''
                        #この分岐の時は変換後の文字にリフレッシュする機会がないようなので、ここで実施する。
                        ti4jp_prnt('この分岐の時は変換後の文字にリフレッシュする機会がないようなので、ここで実施する。')
                        self._refresh_text_from_property(
                            "insert", *self._get_line_from_cursor(row, new_text)
                        )
                        ti4jp_prnt('テキストのリフレッシュ 終了')
                    else:
                        ti4jp_prnt('')
                        ti4jp_prnt('self._text_confirmed が False?; ', self._text_confirmed)
                        new_text = text[:col - len(substring)] + substring + text[col:]
                        ti4jp_prnt('new_text = text[:col - len(substring)] + substring + text[col:]')
                        ti4jp_prnt(new_text,'=', text[:col - len(substring)],'+',  substring,'+', text[col:])
                        ti4jp_prnt('')
                else:
                    ti4jp_prnt('-------------------------------------------------')
                    ti4jp_prnt('substring == self._ime_composition が False です ')
                    ti4jp_prnt(' 変換候補から選択して挿入 です                   ')
                    ti4jp_prnt('-------------------------------------------------')
                    ti4jp_prnt('')
                    ti4jp_prnt('self.text;   ', self.text)
                    ti4jp_prnt('self.cursor; ', self.cursor)
                    ti4jp_prnt('col, row;    ', col, row)
                    ti4jp_prnt('cindex;      ', cindex)
                    ti4jp_prnt('text = _lines[row];     ', text)
                    ti4jp_prnt('len_str=len(substring); ', len_str)
                    ti4jp_prnt('substring;              ', substring)
                    ti4jp_prnt('self._ime_composition;      ', self._ime_composition)
                    ti4jp_prnt('len(self._ime_composition); ', len(self._ime_composition))
                    ti4jp_prnt('self._text_confirmedは。。;  [',self._text_confirmed, '] です')
                    ti4jp_prnt('self._row_start_of_typing;    ', self._row_start_of_typing)
                    ti4jp_prnt('self._ci_start_of_typing;    ', self._ci_start_of_typing)
                    ti4jp_prnt('--------')
                    ti4jp_prnt('入力開始行と完了行が異なる場合と同じ場合とで処理を分ける。')
                    if self._row_start_of_typing != row:
                        #入力開始行と完了行が異なる場合は、選択された変換候補と、変換前の該当テキスト部分を置換し、全textを取り直してからnew_textを作成
                        ti4jp_prnt('入力開始行と完了行が異なるので、選択された変換候補と、変換前の該当テキスト部分を置換し、全textを取り直してからnew_textを作成')
                        self.text = self.text[:cindex-len(self._ime_composition)] + substring + self.text[cindex:]
                        ti4jp_prnt('self.text = self.text[:cindex-len(self._ime_composition)] + substring + self.text[cindex:]')
                        ti4jp_prnt(self.text,'=', self.text[:cindex-len(self._ime_composition)],'+', substring,'+', self.text[cindex:])
                        #一連のパラメータも取り直す
                        _lines = self._lines
                        _lines_flags = self._lines_flags
                        self.gcursor = self.cursor
                        text_lines = self._lines
                        cc, cr = self.cursor
                        col, row = self.cursor
                        cindex = self.cursor_index()
                        text = _lines[row]
                        len_str = len(substring)
                        ti4jp_prnt('_lines;                ', _lines)
                        ti4jp_prnt('self.gcursor;          ', self.gcursor)
                        ti4jp_prnt('text_lines;            ', text_lines)
                        ti4jp_prnt('cc, cr;                ', cc, ' , ', cr)
                        ti4jp_prnt('col, row;              ', col, ' , ', row)
                        ti4jp_prnt('cindex;                ', cindex)
                        ti4jp_prnt('text;                  ', text)
                        ti4jp_prnt('len_str;               ', len_str)
                        ti4jp_prnt('self.add_to_end        ', self.add_to_end)
                        ti4jp_prnt('--------')
                        #現在の行のテキストをnew_textに入れる
                        new_text = _lines[row]
                        ti4jp_prnt('new_text = _lines[row]')
                        ti4jp_prnt(new_text,'=', _lines[row])
                    else:
                        #入力開始行と完了行が同じ場合は、その行のみにおいて、選択された変換候補と変換前の該当テキスト部分を置換してnew_textを作成
                        ti4jp_prnt('入力開始行と完了行が同じなので、その行のみにおいて、選択された変換候補と変換前の該当テキスト部分を置換してnew_textを作成')
                        new_text = text[:col - len(self._ime_composition)] + substring + text[col:]
                        ti4jp_prnt('new_text = text[:col - len(self._ime_composition)] + substring + text[col:]')
                        ti4jp_prnt(new_text,'=', text[:col - len(self._ime_composition)],'+',  substring,'+', text[col:])
                    ti4jp_prnt('--------')
                    ti4jp_prnt('------------------------------------------')
                    ti4jp_prnt('self.cursor ;           ', self.cursor)
                    ti4jp_prnt('self.add_to_end;        ', self.add_to_end)
                    ti4jp_prnt('self.is_android_ime_on; ', self.is_android_ime_on)
                    ti4jp_prnt('self._ime_cursor;       ', self._ime_cursor)
                    ti4jp_prnt('self.cursor;            ', self.cursor)
                    ti4jp_prnt('self.gcursor;           ', self.gcursor)
                    ti4jp_prnt('------------------------------------------')
                    ti4jp_prnt('self._ime_compositionはリセットしておく。')
                    ti4jp_prnt('リセット前に、最後のカーソル位置調整で使用するself._ime_compositionの文字数を取得しておく。')
                    #self._ime_compositionはリセットしておく。
                    #連続で変換候補からの入力になったときの場合にリセットが必要となるため。
                    #リセット前に、最後のカーソル位置調整の段階で使用するself._ime_compositionの文字数を取得しておく。
                    ti4jp_prnt('_len_ime_bevore_reset; ',len(self._ime_composition))
                    self._ime_composition = ''
                    ti4jp_prnt('この分岐の時は変換後の文字にリフレッシュする機会がないようなので、ここで実施する')
                    #この分岐の時は変換後の文字にリフレッシュする機会がないようなので、ここで実施する。
                    self._refresh_text_from_property(
                        "insert", *self._get_line_from_cursor(self.cursor[1], new_text)
                    )
                    ti4jp_prnt('テキストのリフレッシュが終了しました')
                    #このケースの時はself.is_android_ime_onをFalseに戻す
                    self.is_android_ime_on = False
                    ti4jp_prnt('self.is_android_ime_onを...', self.is_android_ime_on, '...に戻しました')
                ti4jp_prnt('')
                ti4jp_prnt(' [改行コードのみが入力されたときとそれ以外で分ける] での最後の確認')
                ti4jp_prnt('col; ', col, ', len(substring);  ', len(substring))
                ti4jp_prnt('self._lines', self._lines)
                ti4jp_prnt('')
                ti4jp_prnt(' [改行コードのみが入力されたときとそれ以外で分ける] が終了しました')
                ti4jp_prnt('')
            if mode is not None:
                if mode == 'int':
                    if not re.match(self._insert_int_pat, new_text):
                        return
                elif mode == 'float':
                    if not re.match(self._insert_float_pat, new_text):
                        return
            #下に記載しているカーソル位置の最終的なリフレッシュの、分岐2および分岐4のケースと改行のみの時は、ここの条件式の処理を回避するようにする
            ti4jp_prnt('------------------------------------------------------------')
            ti4jp_prnt('--       self._set_line_textのところを実行するどうか      --')
            ti4jp_prnt('------------------------------------------------------------')
            if substring == u'\n':
                ti4jp_prnt('')
                ti4jp_prnt('改行コードのみなので迂回します')
                pass
            elif self.add_to_end==True and self.is_android_ime_on==False:
                ti4jp_prnt('')
                ti4jp_prnt('分岐2に該当する、self.add_to_end==True and self.is_android_ime_on==Falseなので迂回します')
                pass
            elif self.add_to_end==False and self.is_android_ime_on==False:
                ti4jp_prnt('')
                ti4jp_prnt('分岐4に該当するself.add_to_end==False and self.is_android_ime_on==Falseなので迂回します')
                pass
            else:
                ti4jp_prnt('self._set_lineを実施します')
                self._set_line_text(row, new_text)
                ti4jp_prnt('self._lines; ', self._lines)
                if len_str > 1 or substring == u'\n' or\
                    (substring == u' ' and _lines_flags[row] != FL_IS_LINEBREAK) or\
                    (row + 1 < len(_lines) and
                     _lines_flags[row + 1] != FL_IS_LINEBREAK) or\
                    (self._get_text_width(
                        new_text,
                        self.tab_width,
                        self._label_cached) > (self.width - self.padding[0] -
                                               self.padding[2])):
                    # Avoid refreshing text on every keystroke.
                    # Allows for faster typing of text when the amount of text in
                    # TextInput gets large.
                    ti4jp_prnt('')
                    ti4jp_prnt('ifの条件式の中におりますのでリフレッシュをすることになります')
                    ti4jp_prnt('')
                    (
                        start, finish, lines, lines_flags, len_lines
                    ) = self._get_line_from_cursor(row, new_text)
                    # calling trigger here could lead to wrong cursor positioning
                    # and repeating of text when keys are added rapidly in a automated
                    # fashion. From Android Keyboard for example.
                    self._refresh_text_from_property(
                        'insert', start, finish, lines, lines_flags, len_lines
                    )
                    ti4jp_prnt('テキストのリフレッシュを終了しました')
            ti4jp_prnt('-------------------------------------------------------------')
            ti4jp_prnt('--ここまで [self._set_line_textのところを実行するかどうか] --')
            ti4jp_prnt('-------------------------------------------------------------')
            ################################################
            #                                              #
            # カーソル位置の最終的なリフレッシュ           #
            #  末尾追加の場合はlen_str分カーソル位置を移動 #
            #  挿入追加の場合は、カーソル位置はそのまま    #
            #                                              #
            ################################################
            ti4jp_prnt('**********************************')
            ti4jp_prnt('カーソル位置の最終的なリフレッシュ')
            ti4jp_prnt('**********************************')
            ti4jp_prnt('----------')
            ti4jp_prnt('----------')
            ti4jp_prnt('self.add_to_end;            ', self.add_to_end)
            ti4jp_prnt('self.is_android_ime_on;     ', self.is_android_ime_on)
            ti4jp_prnt('----------')
            ti4jp_prnt('----------')
            ti4jp_prnt('text;                       ', text)
            ti4jp_prnt('cindex;                     ', cindex)
            ti4jp_prnt('len_str(substringの文字数); ', len_str)
            ti4jp_prnt('len(text[:col - len(self._ime_composition)] + substring); ', len(text[:col - len(self._ime_composition)] + substring))
            ti4jp_prnt('len(self._ime_composition); ', len(self._ime_composition))
            ti4jp_prnt('text[:col - len(self._ime_composition)]',text[:col - len(self._ime_composition)],'+ ', 'substring', substring)
            ti4jp_prnt('self.cursor;                ', self.cursor)
            ti4jp_prnt('self._lines                 ', self._lines)
            ti4jp_prnt('-------------------------------------------------------------')
            #self.add_to_endとself.is_android_ime_onの組み合わせで条件分岐
            ti4jp_prnt('self.add_to_endとself.is_android_ime_onの組み合わせで条件分岐')
            if self.add_to_end:
                if self.is_android_ime_on:
                    ti4jp_prnt('')
                    ti4jp_prnt('-------------------------------------------------------------')
                    ti4jp_prnt('分岐1')
                    ti4jp_prnt('self.add_to_end が...       ; ', self.add_to_end, 'です（Trueであってる？）')
                    ti4jp_prnt('self.is_android_ime_on が...; ', self.is_android_ime_on, 'です(Trueで合ってる？)')
                    ti4jp_prnt('カーソル位置を更新します')
                    self.cursor = self.get_cursor_from_index(cindex + len_str)
                    ti4jp_prnt('カーソル位置を更新しました')
                    ti4jp_prnt('self.cursor;                ', self.cursor)
                    ti4jp_prnt('-------------------------------------------------------------')
                else:
                    ti4jp_prnt('')
                    ti4jp_prnt('-------------------------------------------------------------')
                    ti4jp_prnt('分岐2')
                    ti4jp_prnt('self.add_to_end が...       ; ', self.add_to_end, 'です（Trueであってる？）')
                    ti4jp_prnt('self.is_android_ime_on が...; ', self.is_android_ime_on, 'です(Falseで合ってる？)')
                    ti4jp_prnt('カーソル位置を更新します')
                    self.cursor = self.get_cursor_from_index(cindex + len_str)
                    ti4jp_prnt('カーソル位置を更新しました')
                    ti4jp_prnt('self.cursor;                  ', self.cursor)
                    ti4jp_prnt('-------------------------------------------------------------')
            else:
                if self.is_android_ime_on:
                    ti4jp_prnt('')
                    ti4jp_prnt('-------------------------------------------------------------')
                    ti4jp_prnt('分岐3')
                    ti4jp_prnt('self.add_to_end が...;        ', self.add_to_end, 'です（Falseであってる？）')
                    ti4jp_prnt('self.is_android_ime_on が...; ', self.is_android_ime_on, 'です(Trueで合ってる？)')
                    ti4jp_prnt('カーソル位置を更新します')
                    self.cursor = self.get_cursor_from_index(cindex)
                    ti4jp_prnt('カーソル位置を更新しました')
                    ti4jp_prnt('self.cursor;                  ', self.cursor)
                    ti4jp_prnt('-------------------------------------------------------------')
                else:
                    #両方ともFalseであれば
                    #(途中挿入でテキスト入力中かつ変換候補から選択しているケース) 、
                    #カーソル位置をテキスト挿入後の位置になるように調整する。
                    ti4jp_prnt('')
                    ti4jp_prnt('-------------------------------------------------------------')
                    ti4jp_prnt('分岐4')
                    ti4jp_prnt('self.add_to_end が...;        ', self.add_to_end, 'です（Falseであってる？）')
                    ti4jp_prnt('self.is_android_ime_on が...; ', self.is_android_ime_on, 'です(Falseで合ってる？)')
                    ti4jp_prnt('len(self._ime_composition);   ', len(self._ime_composition))
                    ti4jp_prnt('self._text_confirmedは。。;  [',self._text_confirmed, '] です')
                    ti4jp_prnt('self._row_start_of_typing;    ', self._row_start_of_typing)
                    ti4jp_prnt('self.cursor[1];               ', self.cursor)
                    ti4jp_prnt('self._ci_start_of_typing;    ', self._ci_start_of_typing)
                    ti4jp_prnt('text[:col]; ', text[:col])
                    ti4jp_prnt('text[col:]; ', text[col:])
                    ti4jp_prnt('self._ci_start_of_typing + len_str')
                    ti4jp_prnt(self._ci_start_of_typing, '+', len_str)
                    ti4jp_prnt('')
                    ti4jp_prnt('カーソル位置を更新します')
                    self.cursor = self.get_cursor_from_index(self._ci_start_of_typing + len_str)
                    ti4jp_prnt('カーソル位置を更新しました')
                    ti4jp_prnt('self.cursor;                  ', self.cursor)
                    ti4jp_prnt('_ci_start_of_typingを更新します')
                    self._ci_start_of_typing = self.cursor_index()
                    ti4jp_prnt('self._ci_start_of_typing;    ', self._ci_start_of_typing)
                    ti4jp_prnt('-------------------------------------------------------------')
            # handle undo and redo
            self._set_unredo_insert(cindex, cindex + len_str, substring, from_undo)
            ti4jp_prnt('self.cursor @ end of insert; ', self.cursor)
            self.is_android_ime_on = False
            ti4jp_prnt('self.is_android_ime_onを...  ', self.is_android_ime_on, '...に戻しました')
            ti4jp_prnt('')
            ti4jp_prnt('*******************************************************************')
            ti4jp_prnt('********************* end of insert_text **************************')
            ti4jp_prnt('*******************************************************************')
            ti4jp_prnt('')
    #androidでない場合は、IMEがONの時にテキストボックス中でのカーソル移動を無効にする
    def do_cursor_movement(self, action, control=False, alt=False):
        if platform == 'android':
            TextInput.do_cursor_movement(self, action, control=False, alt=False)
        else:
            if self.is_JP_ime_on:
                ti4jp_prnt('カーソルを動かさないようにreturnします')
                return
            else:
                ti4jp_prnt('カーソルを動かせるようにします')
                TextInput.do_cursor_movement(self, action, control=False, alt=False)
    #  on_focusについて #
    # - androidでないとき
    #textinputをdefocusしたときにis_JP_ime_onをFalseに変更する。
    #これによりIME入力中にdefocusになってもfocusが復帰した時にbackspaceが効く
    #また、defocusしたときはself._ime_compositionをリセットしておき、次にfocusしたときの入力に影響がないようにする
    # - androidのとき
    #input_typeを有するインスタンス(つまりTextInput)をfocusした場合、
    #言語設定が日本語のときはinput_typeを'text'にする。=> 日本語入力を受け付けるようになる。
    #言語設定が日本語以外ではinput_typeを'null'にする。=> English入力のみを受け付けるようになる（ただしGboardの入力予測などが使えない）
    def on_focus(self, instance, value):
        if value:
            ti4jp_prnt('User focused', instance)
            ti4jp_prnt(hasattr(instance, 'input_type'))
            if hasattr(instance, 'input_type'):
                if self.is_lang_ja == True:
                    self.input_type = 'text'
                else:
                    self.input_type ='null'
                ti4jp_prnt('self.input_type更新後; ', self.input_type)
        else:
            self.is_JP_ime_on = False
            self._ime_composition = ''
            ti4jp_prnt('User defocused', instance)
    #画面でのカーソル表示位置のupdate用
    def cursor_update(self, cursornow):
        self.cursor = cursornow[0], cursornow[1]+1
        ti4jp_prnt('self.cursor@cursor_update', self.cursor)
        return self.cursor
if __name__ == '__main__':
    ti4jp_prnt('TextInput for Japanese')
