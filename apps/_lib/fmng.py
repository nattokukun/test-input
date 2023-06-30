# -*- coding: utf-8 -*-
#//////////////////////////////////////////////////////////////////////////////
#            fmng  File Manager
#            M.Ida 2022.03.04
#//////////////////////////////////////////////////////////////////////////////
import traceback
import os
from _lib import cssys
## import cssys
from _lib.cssys import debug_log
## import const
"""
from pickle import NONE
from struct import pack, unpack, calcsize, iter_unpack
from docutils.utils.math.latex2mathml import begin_environment
"""

#------------------------------------------------------------------------------
#                   定数定義
#------------------------------------------------------------------------------
if cssys.is_windows():
    PATH_DELM = '\\'
else:
    PATH_DELM = '/'

#------------------------------------------------------------------------------
#                   初期処理
#------------------------------------------------------------------------------
# Android 用
if cssys.is_android():
    from jnius   import autoclass
    from android import mActivity, activity

    Activity            = autoclass('android.app.Activity')
    Intent              = autoclass('android.content.Intent')
    Context             = autoclass('android.content.Context')
    Uri                 = autoclass('android.net.Uri')
    File                = autoclass('java.io.File')
    ContextCompat       = autoclass('androidx.core.content.ContextCompat')
    DocumentFile        = autoclass('androidx.documentfile.provider.DocumentFile')
    FileProvider        = autoclass('androidx.core.content.FileProvider')
    Environment         = autoclass('android.os.Environment')
    DocumentsContract   = autoclass('android.provider.DocumentsContract')
    ## FileUtils           = autoclass('android.os.FileUtils')
    OpenableColumns     = autoclass("android.provider.OpenableColumns")

    EXTERNAL_STORAGE_PROVIDER_AUTHORITY = "com.android.externalstorage.documents"

    InputStreamReader = autoclass('java.io.InputStreamReader')
    StandardCharsets  = autoclass('java.nio.charset.StandardCharsets')
    BufferedReader    = autoclass('java.io.BufferedReader')


if cssys.is_android():
    ADR_ENV_DIR_MUSIC           = Environment.DIRECTORY_MUSIC
    ADR_ENV_DIR_PODCASTS        = Environment.DIRECTORY_PODCASTS
    ADR_ENV_DIR_RINGTONES       = Environment.DIRECTORY_RINGTONES
    ADR_ENV_DIR_ALARMS          = Environment.DIRECTORY_ALARMS
    ADR_ENV_DIR_NOTIFICATIONS   = Environment.DIRECTORY_NOTIFICATIONS
    ADR_ENV_DIR_PICTURES        = Environment.DIRECTORY_PICTURES
    ADR_ENV_DIR_MOVIES          = Environment.DIRECTORY_MOVIES
    ADR_ENV_DIR_DOWNLOADS       = Environment.DIRECTORY_DOWNLOADS
    ADR_ENV_DIR_DCIM            = Environment.DIRECTORY_DCIM
    ADR_ENV_DIR_DOCUMENTS       = Environment.DIRECTORY_DOCUMENTS
    ADR_ENV_DIR_ROOT            = None
    ADR_ENV_DIR_DEFAULT         = ADR_ENV_DIR_DOCUMENTS
else:
    ADR_ENV_DIR_DEFAULT         = None

#------------------------------------------------------------------------------
#                   クラス
#------------------------------------------------------------------------------
# uri指定でのアンドロイドファイルクラス
class AdrFileByUri:
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            コンストラクタ
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def __init__(self, p_file_uri):     # ファイルuri
        self.class_name = 'AdrFileByUri'
        if not cssys.is_android():
            raise Exception(self.class_name + ' : android only class!')
        self.file_uri       = p_file_uri
        self.file_inp_strem = None
        self.file_out_strem = None
        ## self.read_eof       = False
        self.LF             = chr(0x0a)

        self.LF_ini = 0
        self.LF_ext = 1
        self.LF_non = 2
        self.end_mark       = self.LF_ini

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            オープン
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # インプットオープン
    def open_input(self):
        # 読み込みファイルオープン
        self.file_inp_strem = mActivity.getContentResolver().openInputStream(self.file_uri)
        ## self.read_eof       = False
        self.text_list      = []

    # アウトプットオープン
    def open_output(self):
        # 書き込みファイルオープン
        self.file_out_strem = mActivity.getContentResolver().openOutputStream(self.file_uri)

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            クローズ
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def close(self):
        if self.file_inp_strem != None:
            self.file_inp_strem.close()
        ## self.read_eof = False

        if self.file_out_strem != None:
            self.file_out_strem.close()

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            データ出力
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # データ出力
    def write(self, p_buf_int_list,     # 書き込むバッファ(int型リスト)
                    p_len):             # 書き込むバッファ長
        ###
        debug_log('write = {}'.format(p_buf_int_list))
        ###
        ## self.file_out_strem.write(p_buf_int_list, 0, p_len)
        self.file_out_strem.write(p_buf_int_list)

    # テキストデータ出力
    def write_text(self, p_text):   # 書き込むテキスト
        # ｓｔｒ型を bytes型リストに変換
        t_buf_byte_list = p_text.encode()
        self.write(t_buf_byte_list, len(p_text))

    # テキスト行データ出力
    def write_line(self, p_text):   # 書き込むテキス
        ## t_text = p_text + chr(0x0d) + chr(0x0a)
        ## t_text = p_text + chr(0x0a)
        t_text = p_text + self.LF
        self.write_text(t_text)

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            データ入力
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # データ入力
    def read(self, p_buf_len = 1024):   # 読み込むバッファ長
                                        # 読み込んだバッファ(bytes)
                                        # 読み込んだバイト数
        # バッファ確保
        t_buf_int_list = [0] * p_buf_len

        # 読む
        t_buf_count = self.file_inp_strem.read(t_buf_int_list)

        if t_buf_count > 0:
            t_bytes = bytes(t_buf_int_list)
            ###
            debug_log('read count = {}'.format(t_buf_count))
            debug_log('read 5byte = {} {} {} {} {}'.format(t_bytes[0], t_bytes[1], t_bytes[2], t_bytes[3], t_bytes[4]))
            ## debug_log('data type {}'.format(type(t_bytes)))
            ## debug_log('read data {}'.format(t_bytes))
            ###
        else:
            t_bytes = b''

        return t_bytes, t_buf_count

    # テキストデータ入力
    def read_text(self):
                            # 読み込んだテキスト
                            # True:読み込んだ結果EOF
        # データ入力
        t_buf_bytes, t_count = self.read()
        if t_count < 1:
            debug_log('read_text = eod')
            return '', True

        # 読み込んだリストが存在
        ## debug_log('{}'.format(t_buf_bytes))

        # 0 を全て削除 -> list -> bytes
        t_buf_bytes = bytes([t_byte for t_byte in t_buf_bytes if t_byte != 0])
        # bytes を文字列に変換
        t_text = t_buf_bytes.decode('utf-8')

        debug_log('read_text = {}'.format(t_text))

        return t_text, False

    # テキスト行データ入力の最終状態を得る
    def __get_end_mark(self, p_text):   # 判定するテキスト
                                        # 最終状態

        t_char = p_text[-1]
        if t_char == self.LF:
            t_end_mark = self.LF_ext
        else:
            t_end_mark = self.LF_non
        return t_end_mark

    # テキスト行データ入力の読み込み
    def __read_for_read_line(self, t_text_last_norelease):  # 未提供テキスト
                                                            # 読み込んだテキスト
                                                            # True:読み込んだ結果EOD(<>EOF)
        ROUTIN = '__read_for_read_line : '

        t_loop_idx = 0
        t_loop     = True
        while t_loop:
            t_loop = False
            # テキストデータ入力
            t_text, t_eof = self.read_text()

            # 新たな最終状態
            if t_eof:
                self.end_mark = self.LF_ini
            else:
                self.end_mark = self.__get_end_mark(t_text)
            # 新たに分割
            if t_eof:
                self.text_list = []
            else:
                self.text_list = t_text.split(self.LF)
            """
                aa/n bb/n cc/n
                aa bb cc ''
                となるため最後の要素を削除
            """
            if self.end_mark == self.LF_ext:
                if self.text_list[-1] == '':
                    del self.text_list[-1]

            if len(self.text_list) >= 1:
            # 新たなデータがある
                if self.text_list[0] == '':
                # na) or nb)
                    del self.text_list[0]
                    return t_text_last_norelease, False
                else:
                    if (len(self.text_list)  == 1          ) and \
                       (self.end_mark        == self.LF_non):
                    # ne)
                        if t_text_last_norelease == None:
                            t_text_last_norelease = self.text_list[0]
                        else:
                            t_text_last_norelease = t_text_last_norelease + self.text_list[0]

                        t_loop = True
                    else:
                    # nc) nd)
                        if t_text_last_norelease == None:
                            t_text = self.text_list[0]
                        else:
                            t_text = t_text_last_norelease + self.text_list[0]
                        del self.text_list[0]
                        return t_text, False
            else:
            # 新たなデータが無い
                # 未提供データ
                if t_text_last_norelease == None:
                    return '', True
                else:
                    return t_text_last_norelease, False
            # ループ判定
            if t_loop:
                t_loop_idx += 1
                if t_loop_idx > 10:
                    raise Exception(ROUTIN + 'loop max over !')
                # loop
            else:
                raise Exception(ROUTIN + 'program error 1')
            # loop

    # テキスト行データ入力
    def read_line(self):
                            # 読み込んだテキスト
                            # True:読み込んだ結果EOD(<>EOF)
        ROUTIN = 'read_line : '
        if len(self.text_list) > 0:
        # 未提供のテキスト有り
            if len(self.text_list) == 1:
            # 最後の一つ
                """
                最終状態
                end_mark
                -----------------------------
                LF_ini

                LF_ext : aaaa/n __|           xa) ..eof
                           aaaa/n |           xb) ..not eof
                           aaaa/n | bbb       xc) ..not eof

                LF_non :     aaaa | /n        na)
                             aaaa | /nbbb     nb)
                             aaaa | a/n       nc)
                             aaaa | a/nbbb    nd)
                             aaaa | aaaaaaa   ne)
                """
                if   self.end_mark == self.LF_ini:
                    raise Exception(ROUTIN + 'program error 1')
                elif self.end_mark == self.LF_ext:
                    # 先頭を提供する
                    t_text = self.text_list[0]
                    # 先頭を削除する
                    del self.text_list[0]
                    return t_text, False # False xa)もあえて次readさせる
                elif self.end_mark == self.LF_non:
                # 次読んでみないと na)～が不明
                    # テキスト行データ入力の読み込み
                    t_text, t_eod = self.__read_for_read_line(self.text_list[0])
                    return t_text, t_eod
            else:
            # 複数有る
                # 先頭を提供する
                t_text = self.text_list[0]
                # 先頭を削除する
                del self.text_list[0]
                return t_text, False

        # 未提供のテキスト無し

        # テキスト行データ入力の読み込み
        t_text, t_eod = self.__read_for_read_line(None)
        return t_text, t_eod

# アンドロイドアプリファイルクラス
class AdrAppFile:
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            コンストラクタ
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def __init__(self, p_file_name):    # dirを除く 単体ファイル名
        self.class_name = 'AdrAppFile'
        if not cssys.is_android():
            raise Exception(self.class_name + ' is android only class!')
        self.file_name   = p_file_name
        self.fout_stream = None
        self.finp_stream = None
        self.buf_reader  = None
        self.read_eof    = False

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            オープン
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    # インプットオープン
    def open_input(self):
                            # True:オープン成功
        t_ok = False
        try:
            t_context = mActivity.getApplicationContext()
            ## self.finp_stream = Context.openFileInput(self.file_name)
            self.finp_stream = t_context.openFileInput(self.file_name)
            self.read_eof    = False
            t_ok = True
        except:
            self.finp_stream = None
            self.read_eof    = False
        return t_ok

    # アウトプットオープン
    def open_output(self):
        t_context = mActivity.getApplicationContext()
        ## self.fout_stream = Context.openFileOutput(self.file_name, Context.MODE_PRIVATE)
        self.fout_stream = t_context.openFileOutput(self.file_name, Context.MODE_PRIVATE)

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            クローズ
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def close(self):
        if self.fout_stream != None:
            self.fout_stream.close()

        if self.finp_stream != None:
            self.finp_stream.close()

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            テキストデータ出力
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    ## def write(self, p_text):    # 書き込むテキスト
    def write_text(self, p_text):    # 書き込むテキスト
        if self.fout_stream == None:
            raise Exception(self.class_name + ' write : not open!')
        self.fout_stream.write(bytearray(p_text.encode()))

    def write_line(self, p_text):   # 書き込むテキスト
        t_text = p_text + '\n'
        self.write_text(t_text)

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            テキスト行入力
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def read_line(self):
                            # テキスト行 None:eof
        if self.finp_stream == None:
            raise Exception(self.class_name + ' read_line : not open!')

        if self.read_eof:
            return None

        if self.buf_reader == None:
        # 未だ読んでいない
            t_inputStreamReader = InputStreamReader(self.finp_stream, StandardCharsets.UTF_8)
            self.buf_reader     = BufferedReader(t_inputStreamReader)

        # 読む
        t_line = self.buf_reader.readLine()
        if t_line == None:
            self.read_eof = True
            return None

        return t_line

#------------------------------------------------------------------------------
#                   関数群
#------------------------------------------------------------------------------
# フォルダサイズを得る  SDカードもOK
# (android のバージョンによっては未対応)
def get_dir_size(p_dir='.'):    # フォルダ名
                                # サイズ < 0:存在しない
    # py 3.5 以上
    """
    t_total = 0
    with os.scandir(p_dir) as it:
        for t_entry in it:
        # エントリーループ
            if t_entry.is_file():
                # ファイルサイズを得る
                t_total += t_entry.stat().st_size
            elif t_entry.is_dir():
                # フォルダサイズを得る
                t_total += get_dir_size(t_entry.path)
    return t_total
    """
    # py 2.7 以上
    # サブフォルダを含め全ファイル一覧を得る
    # https://www.sejuku.net/blog/63816
    t_total = 0
    for t_cur_dir, t_dirs, t_files in os.walk(p_dir):
        for t_file in t_files:
            # print(os.path.join(t_cur_dir, t_file))
            t_path = os.path.join(t_cur_dir, t_file)
            # ファイルサイズを得る
            try:
                t_total += os.path.getsize(t_path)
            except:
                # ファイルサイズが取得できない    # 原因不明のバグ有り
                print('--- Error! ---')
                print('dir :' + t_cur_dir)
                print('file:' + t_file)
                return -1;
    return t_total

# フォルダまたはファイルサイズを得る  SDカードもOK
# (android のバージョンによっては未対応)
def get_path_size(p_path='.'):  # フォルダ名orファイル名
                                # サイズ < 0:存在しない
    if os.path.isfile(p_path):
        # ファイルサイズを得る
        return os.path.getsize(p_path)
    elif os.path.isdir(p_path):
        # フォルダサイズを得る
        return get_dir_size(p_path)
    else:
        # アクセスエラー（存在しない等）
        # return 26
        return -1
    # return 27

# フォルダが存在しなければ全作成する
#    使用禁止 → os.makedirs を使用する
def not_found_mkdir(p_path):    # フォルダ名絶対パス
                                # エラーメッセージ '':成功
    t_errmsg = ''
    if os.path.isdir(p_path):
    # 存在した
        pass
    else:
    # 存在しないので作成を試みる
        # 区切り文字で分割する
        t_path_parts = p_path.split(PATH_DELM)
        # 分割ループ
        t_path = ''
        t_count = 0
        for t_name in t_path_parts:
            if t_name != '':
                t_count += 1

                # 現在のパスを保存
                t_prev_path = t_path
                # 作成するパス名
                if t_path == '':
                    # 先頭
                    if cssys.is_windows():
                        t_path = t_path + t_name
                    else:
                        t_path = t_path + PATH_DELM + t_name
                else:
                    t_path = t_path + PATH_DELM + t_name

                # フォルダ処理をするかの判定
                if cssys.is_windows():
                    t_dir = (t_count > 1)
                else:
                    t_dir = (t_count > 2)
                    if t_dir:
                        if (t_name == '0') and \
                           (t_name == '1'):
                           t_dir = False

                t_msg = ''
                if t_dir:
                # フォルダ処理する
                    if os.path.isdir(t_path):
                    # フォルダが存在した
                        t_msg = 'exist dir'
                    else:
                    # フォルダが存在しない
                        t_msg = 'make dir process start'
                        # フォルダを作成する
                        try:
                            debug_log('make dir start : ' + t_path)
                            os.mkdir(t_path)
                            debug_log('make dir end   : ' + t_path)
                        except:
                            debug_log('make dir * error!')
                            t_errmsg = traceback.format_exc() # + '\n' + t_path
                            # raise Exception(t_errmsg)
                else:
                # フォルダ処理しない
                    t_msg = 'pass'
                pass
                debug_log(t_path + '.. ' + t_msg)
            pass

            if t_errmsg != '':
                debug_log('make dir process * break!')
                break
        pass # for loop

    if t_errmsg != '':
        debug_log(t_path + '\n' + t_errmsg)

    debug_log('not_found_mkdir return')
    return t_errmsg

# ファイルサイズを得る
def adr_get_file_size(p_file_uri):  # ファイルuri
                                    # サイズ < 0:存在しない

    from _lib import cssys
    t_file_doc = cssys.uri_to_doc(p_file_uri)
    t_size = t_file_doc.length()
    if t_size == 0:
    # ファイルが存在するか調査
        if t_file_doc.isFile():
        # ファイルが存在した
            return 0
        else:
        # ファイルが存在しない
            return -1
    else:
        return t_size

# フォルダサイズを得る
def adr_get_dir_size(p_dir_uri):    # フォルダuri
                                    # サイズ < 0:存在しない
    t_size = 0
    # メンバーループ
    t_dir_doc = cssys.uri_to_doc(p_dir_uri)
    t_docs = t_dir_doc.listFiles()
    for t_doc in t_docs:
        if t_doc.isDirectory():
        # フォルダ
            # フォルダサイズを得る
            t_size += adr_get_dir_size(t_doc.getUri())
        else:
        # ファイル
            # ファイルサイズを得る
            t_size += adr_get_file_size(t_doc.getUri())
    return t_size

# フォルダが存在しなければ全作成する
#    作成フォルダリストは既存でも良い
def adr_makedirs(p_parent_uri,  # 指定フォルダ Uri
                 p_child_dirs): # 作成フォルダリスト
                                # エラーメッセージ '':成功
                                # 最終フォルダ DocumentFile
    ROUTIN = 'adr_makedirs : '

    ## const.GETDOC_UNSUPPORTED_URI = 'uri_to_doc : unsupported uri!'
    t_errmsg    = ''
    t_child_doc = None

    test_adr_uri(p_parent_uri, ROUTIN, False)
    ## t_parent_doc = DocumentFile.fromTreeUri(mActivity, p_parent_uri)
    t_parent_doc = cssys.uri_to_doc(p_parent_uri)
    if t_parent_doc == None:
        ## raise Exception(const.GETDOC_UNSUPPORTED_URI)
        raise Exception(ROUTIN + 'unsupported uri!')

    print(ROUTIN + 'p_parent_uri path ' + p_parent_uri.getPath())
    """
    if t_parent_doc.canWrite():
        print('adr_makedirs its Can Write!')
    else:
        print('adr_makedirs its Can not Write!')
    """
    for t_child_dir in p_child_dirs:
        t_child_doc = t_parent_doc.findFile(t_child_dir)
        if t_child_doc == None:
        # 存在しない
            debug_log(ROUTIN + 'doc None :' + t_child_dir)
            # フォルダ作成
            try:
                debug_log(ROUTIN + 'create dir :' + t_child_dir)
                t_child_doc = t_parent_doc.createDirectory(t_child_dir)
                if t_child_doc != None:
                # 成功
                    debug_log(ROUTIN + 'create ok :' + t_child_dir)
                    t_parent_doc = t_child_doc
                else:
                    debug_log(ROUTIN + ' create error(1) :' + t_child_dir)
                    t_errmsg = ROUTIN + "can't create " + t_child_dir
                    t_child_doc = None
                    break
            except:
                debug_log(ROUTIN + 'create error(2) :' + t_child_dir)
                ## t_errmsg = traceback.format_exc() # + '\n' + t_path
                t_errmsg = ROUTIN + "create failed " + t_child_dir
                t_child_doc = None
                break
        else:
        # 存在する
            debug_log(ROUTIN + 'doc exist :' + t_child_dir)
            if t_child_doc.isDirectory():
            # 成功
                t_parent_doc = t_child_doc
                debug_log(ROUTIN + 'dir exist :' + t_child_dir)
            else:
            # フォルダではない物が存在
                debug_log(ROUTIN + 'not dir :' + t_child_dir)
                t_errmsg = ROUTIN + "can't create for exist file" + t_child_dir
                t_child_doc = None
                break

    return t_errmsg, t_child_doc

# Uriのdirが一致しているか
def uri_dir_is_same(p_uri_a, p_uri_b):  # 比較する uri
                                        # True:同一である
    return (p_uri_a.getHost()            == p_uri_b.getHost()           ) and \
           (p_uri_a.getLastPathSegment() == p_uri_b.getLastPathSegment())

# Uriからドライブパスとフォルダ以降のパスを得る
########### uri_to drv_path
def uri_to_drvpath(p_uri):  # uri
                            # ドライブパス       ex. /storage/F677-248B/
                            # フォルダ以降のパス  ex. MyData/xxx

    if not cssys.is_android():
        raise Exception('uri_to_drvpath() not android !')

    t_base = p_uri.getLastPathSegment()    # F677-248B:MyData/bb.backup/bb.02.02.02

    t_texts = t_base.split(':')
    t_count = len(t_texts)
    if 1 <= t_count <= 2:
        t_drv = '/storage/' + t_texts[0] + '/'
        if t_count == 2:
            t_dir = t_texts[1]
        else:
            t_dir = ''
    else:
        raise Exception('uri_to_drvpath() error! : ' + t_base)

    return t_drv, t_dir

# 外部ストレージフォルダ uri を得る /storage/emulated/0
def get_external_storage_dir_uri():
                                        # 外部ストレージフォルダ uri
    t_dir  = Environment.getExternalStorageDirectory().getAbsolutePath()
    t_file = File(t_dir)
    t_uri =  Uri.fromFile(t_file)
    return t_uri

"""
# bytes型だけが入ったlistを全てstr型に変換したlistに変換
# def bytelist_to_strlist(byte_list: list) -> list:
#    (別のユニットにすべき？)
def bytelist_to_strlist(p_byte_list):   # bytes型だけが入ったlist
                                        # str型だけが入ったlist
    return [t_i.decode('utf8') ]
"""

# アプリ固有の物理ストレージfilesフォルダ uri を得る /storage/emulated/0/Android/data/パッケージ/files
def get_external_app_files_dir_uri():
                                    # アプリ固有の物理ストレージfilesフォルダ uri
    t_external_storage_volume_files = \
            ContextCompat.getExternalFilesDirs(mActivity.getApplicationContext(), None);
    t_primary_file = t_external_storage_volume_files[0]; # 0がプライマリー
    ## print(t_primary_file.getPath())
    return t_primary_file


# アプリ固有の物理ストレージfilesフォルダ uri を得る /storage/emulated/0/Android/data/パッケージ/files (a)
# (a) + 指定ファイル名 のuriを得る
# (a) フォルダが存在しなければ作成する
def get_external_app_files_file_uri(p_file_name,    # 指定ファイル名
                                    p_make_dir):    # True:～data/パッケージ/files までが存在しなければ作成する
                                                    # ～data/パッケージ/files/指定ファイル名 のuri
    ## print(p_file_name)
    # アプリ固有の物理ストレージfilesフォルダ uri を得る /storage/emulated/0/Android/data/パッケージ/files
    t_files_uri = get_external_app_files_dir_uri()
    t_files_dir = t_files_uri.getPath()

    # ファイルuriを得る
    t_file_name = t_files_uri.getPath() + PATH_DELM + p_file_name
    t_file = File(t_file_name)
    t_file_uri = Uri.fromFile(t_file)
    # print(t_file_uri.getPath())

    if p_make_dir:
    # True:～data/パッケージ/files までが存在しなければ作成する

        # アプリ固有の物理ストレージフォルダ uri を得る /storage/emulated/0/Android/data
        t_data_uri = get_external_app_dir_uri()
        t_data_dir = t_data_uri.getPath()

        # data/移行のフォルダリストを得る
        t_dirs = t_files_dir.split(t_data_dir)      # "","/パッケージ/files"
        t_mk_dirs = t_dirs[1].split('/')            # /パッケージ/files -> "","パッケージ","files"
        t_mk_dirs.pop(0)                            # 先頭の''を削除
        # print(t_mk_dirs)

        # フォルダが存在しなければ全作成する
        #    作成フォルダリストは既存でも良い
        t_errmsg, t_files_doc = adr_makedirs(t_data_uri, t_mk_dirs)
        if t_errmsg != '':
            raise Exception('make dirs error : ' + t_errmsg)

    return t_file_uri

# アプリ固有の物理ストレージフォルダ uri を得る /storage/emulated/0/Android/data
def get_external_app_dir_uri():
                                    # アプリ固有の物理ストレージフォルダ uri
    """
    t_external_storage_volume_files = \
            ContextCompat.getExternalFilesDirs(mActivity.getApplicationContext(), None);
    t_primary_file = t_external_storage_volume_files[0]; # 0がプライマリー
    """
    # アプリ固有の物理ストレージfilesフォルダ uri を得る /storage/emulated/0/Android/data/パッケージ/files
    t_primary_file = get_external_app_files_dir_uri()

    # 上記だと、モジュール名から左を得る必要あり
    t_context = mActivity.getApplicationContext()
    ## print('x ' + t_context.getPackageName())
    t_texts = t_primary_file.getPath().split(PATH_DELM + t_context.getPackageName())
    if len(t_texts) >= 2:
        t_primary_file = File(t_texts[0])
        t_uri = Uri.fromFile(t_primary_file)
    else:
        raise Exception('get_external_app_dir_uri error!')
    return t_uri

"""
# アプリ固有の物理ストレージを得る
def get_adr_primary_external_storage_uri(p_app_context):    # True:Application Context
                                                            # False:Application Context Top dir
                                                            # 物理ストレージ uri
    const.ANDROID_DATA = 'Android/data'
    t_external_storage_volume_files = \
            ContextCompat.getExternalFilesDirs(mActivity.getApplicationContext(), None);
    t_primary_external_storage_file = t_external_storage_volume_files[0];

    if p_app_context:
    # True:Application Context
        pass
    else:
    # False:Application Context Top dir
        # Topフォルダを探す
        # print(t_primary_external_storage_file.getParent()) # /storage/emulated/0/Android/data/org.kivy.un_official_launcher/files
        t_dir = t_primary_external_storage_file.getParent()
        t_sepa_dirs = t_dir.split(const.ANDROID_DATA)
        t_dir = t_sepa_dirs[0] + const.ANDROID_DATA
        t_primary_external_storage_file = File(t_dir)

    t_uri =  Uri.fromFile(t_primary_external_storage_file)
    debug_log(t_uri.getPath()) # /storage/emulated/0/Android/data/org.kivy.un_official_launcher/files
    return t_uri
"""

def test_adr_uri(p_uri,
                 p_title,
                 p_put = False):
    if not p_put:
        return

    try:
        debug_log(' ')
        debug_log('   ' + p_title)
        """
        debug_log(' 1:' + p_uri.getAuthority())
        debug_log(' 2:' + p_uri.getEncodedAuthority())
        ## debug_log(' 3:' + p_uri.getEncodedFragment())
        debug_log(' 4:' + p_uri.getEncodedPath())
        debug_log(' 5:' + p_uri.getEncodedSchemeSpecificPart())
        ## debug_log(' 6:' + p_uri.getEncodedUserInfo())
        ## debug_log(' 7:' + p_uri.getFragment())
        debug_log(' 8:' + p_uri.getHost())
        debug_log(' 9:' + p_uri.getLastPathSegment())
        debug_log('10:' + p_uri.getPath())
        debug_log('11:' + p_uri.getScheme())
        debug_log('12:' + p_uri.getSchemeSpecificPart())
        ## debug_log('13:' + p_uri.getUserInfo())
        """
        debug_log(f'14:{p_uri.toString()}')
    except:
        pass
    """
    t_file_id = DocumentsContract.getDocumentId(p_uri)
    ## file_type, file_name = file_id.split(':')
    debug_log('file id :' + t_file_id)
    """

    """
    # : が存在する場合を SD とする
    t_sd = ':' in p_uri.getPath()
    if t_sd:
        debug_log('   This is SD')
    else:
        debug_log('   This is not SD')

    if not t_sd:
    # SD 以外
        t_file = File(p_uri.getPath())
        t_doc = DocumentFile.fromFile(t_file)
    else:
    # SD
        if p_uri.getScheme() == 'file':
        # SDなのに file の場合は、未対応とする
            t_doc  = None
        else:
        # context
            ## t_file = File(p_uri.getPath())
            t_doc = DocumentFile.fromTreeUri(mActivity, p_uri)
    pass
    """
    # uri から DocumentFile を得る
    try:
        t_doc = cssys.uri_to_doc(p_uri)
    except:
        t_doc = None

    if t_doc == None:
        t_msg = '< SD and file Schema is unsupported! >'
    else:
        if t_doc.canRead():
            t_msg = '< Can Read >'
        else:
            t_msg = '< Can not Read >'

        if t_doc.canWrite():
            t_msg = t_msg + ' < Can Write >'
        else:
            t_msg = t_msg + ' < Can not Write >'

    debug_log('   ' + t_msg + ' : ' + f'{p_uri.getPath()}')
    debug_log(' ')
    return

"""
        get で取得した内容
  1:
  2:
  4:/storage/emulated/0/Android/data/jp.co.wasabiapps.bestbowling
  5:///storage/emulated/0/Android/data/jp.co.wasabiapps.bestbowling
  8:
  9:jp.co.wasabiapps.bestbowling
 10:/storage/emulated/0/Android/data/jp.co.wasabiapps.bestbowling
 11:file
 12:///storage/emulated/0/Android/data/jp.co.wasabiapps.bestbowling
 14:file:///storage/emulated/0/Android/data/jp.co.wasabiapps.bestbowling

        get で取得した内容
  1:
  2:
  4:/tree/F677-248B%3A/document/F677-248B%3AMyData/bb.backup/bb.2022.05.12
  5:///tree/F677-248B%3A/document/F677-248B%3AMyData/bb.backup/bb.2022.05.12
  8:
  9:bb.2022.05.12
 10:/tree/F677-248B:/document/F677-248B:MyData/bb.backup/bb.2022.05.12
 11:file
 12:///tree/F677-248B:/document/F677-248B:MyData/bb.backup/bb.2022.05.12
 14:file:///tree/F677-248B%3A/document/F677-248B%3AMyData/bb.backup/bb.2022.05.12

        permission で取得した内容
 1:com.android.externalstorage.documents
 2:com.android.externalstorage.documents
 4:/tree/F677-248B%3A
 5://com.android.externalstorage.documents/tree/F677-248B%3A
 8:com.android.externalstorage.documents
 9:F677-248B:
10:/tree/F677-248B:
11:content
12://com.android.externalstorage.documents/tree/F677-248B:
14:content://com.android.externalstorage.documents/tree/F677-248B%3A

"""

def test_adr_uri_by_path(p_path,
                         p_title):

    t_uri = Uri.fromFile(File(p_path))
    test_adr_uri(t_uri, p_title)
    return

# uriの最終名の(親)フォルダuriを得る
#    ファイルの時は当該ファイルのフォルダ
#    フォルダの時は親フォルダ
def parent_dir_uri_of_uri(p_uri):   # uri
                                    # 最終名の(親)フォルダuri
    # フォルダ部を得る
    t_last_len = len(p_uri.getLastPathSegment()) + 1
    t_file_dir = p_uri.getPath()
    t_len = len(t_file_dir)
    t_dir = t_file_dir[0:(0 + t_len - t_last_len)]

    # フォルダ部 docを得る
    t_dir_uri = path_to_uri(t_dir)
    ## fmng.test_adr_uri(t_dir_uri, '%%%%%%%% t_dir_uri %%%%%%%%', True)
    return t_dir_uri

# パスからuriを得る
def path_to_uri(p_path):    # パス
                            # uri
    return Uri.fromFile(File(p_path))

# パスをドライブ部uriとフォルダ部pathに分ける
########### path_to_drvuri_path
def path_to_uri_dir(p_path):    # パス
                                # ドライブ部uri
                                # フォルダ部path

    t_uri = Uri.fromFile(File(p_path))

    # コロンがあるか
    t_dirs = t_uri.getPath().split(':')
    t_count = len(t_dirs)

    if t_count == 1:
    # コロン無し
    # 10:/storage/emulated/0/Android/data/jp.co.wasabiapps.bestbowling

        t_tmp1_dirs = t_uri.getPath().split('/emulated/')
        t_count1 = len(t_tmp1_dirs)
        if t_count1 < 2:
            raise Exception('path_to_uri_dir cant separated(1) : ' + p_path)

        t_tmp2_dirs = t_tmp1_dirs[1].split('/')
        t_count2 = len(t_tmp2_dirs)
        if t_count1 < 1:
            raise Exception('path_to_uri_dir cant separated(2) : ' + p_path)
        if '0' <= t_tmp2_dirs[0][0] <= '9':
            pass
        else:
            raise Exception('path_to_uri_dir cant separated(3) : ' + p_path)

        del t_tmp1_dirs[1]
        t_drv = ''
        for t_tmp1 in t_tmp1_dirs:
            if t_drv != '':
                t_drv = t_drv + '/'
            t_drv = t_drv + t_tmp1
        t_drv = t_drv + '/emulated/' + t_tmp2_dirs[0]

        del t_tmp2_dirs[0]
        t_dir = ''
        for t_tmp2 in t_tmp2_dirs:
            if t_dir != '':
                t_dir = t_dir + '/'
            t_dir = t_dir + t_tmp2
        t_drv = t_drv + '/'
    else:
    # コロン有り
    # 例 10:/tree/F677-248B:/document/F677-248B:MyData/bb.backup/bb.2022.05.12

        t_dir = t_dirs[(t_count - 1)]
        """
        del t_dirs[(t_count - 1)]
        t_drv = ''
        for t_tmp in t_dirs:
            if t_drv != '':
                t_drv = t_drv + ':'
            t_drv = t_drv + t_tmp
        """
        t_drv = t_dirs[0]
        t_drv = t_drv + ':'

    debug_log('path to drv ' + t_drv)
    debug_log('path to dir ' + t_dir)

    t_drv_uri = Uri.fromFile(File(t_drv))
    return t_drv_uri, t_dir

# callback 処理クラス
class __RequestAccessCallback_OpenDir:
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            コンストラクタ
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def __init__(self, p_request_code):
        self.wait_request_code = p_request_code
        self.result = None

        # 発行のコールバックをセット
        # スレッドの重複はクラスが見つけられない場合有り
        # https://issuehint.com/issue/kivy/python-for-android/2533
        activity.bind(on_activity_result = self._on_activity_result)

        self.dir_uri = None

        # androidバージョンクラス
        self.adrd_ver = cssys.AndroidVersion()

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #           callbackハンドラ
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def _on_activity_result(self, p_request_code, p_result_code, p_intent):
        debug_log('on_activity_result start')
        t_end = False
        if p_request_code == self.wait_request_code:
        # 当該リクエスト
            if p_result_code  == Activity.RESULT_OK:
                # 許可
                debug_log('on_activity_result ok!')
                t_result = True

                ### Uri uri = data.getData();
                ### getContentResolver().takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION |
                ###                                                        Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
                ### DocumentFile pickedDir = DocumentFile.fromTreeUri(this, uri);

                # uriを得る
                ## Intent   = autoclass('android.content.Intent')
                self.dir_uri = p_intent.getData()

                # 許可を保存
                t_saved = True
                t_resolver = mActivity.getContentResolver()
                if self.adrd_ver.is_7_9:
                    # 以下が正しいかは不明であるが上手くいっている？
                    t_resolver.takePersistableUriPermission(self.dir_uri,
                                                            Intent.FLAG_GRANT_READ_URI_PERMISSION or
                                                            Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
                elif self.adrd_ver.more_than_10:
                    t_resolver.takePersistableUriPermission(self.dir_uri,
                                                            p_intent.getFlags() and
                                                            (Intent.FLAG_GRANT_READ_URI_PERMISSION or
                                                             Intent.FLAG_GRANT_WRITE_URI_PERMISSION   ))
                else:
                    t_saved = False

                if t_saved:
                    debug_log('saved permission')
                else:
                    debug_log('saved permission error! (android ver error)')
            else:
                # 拒否処理
                debug_log('on_activity_result cancel!')
                t_result = False

            t_end = True
        else:
            debug_log('on_activity_result not request')

        if t_end:
            # バインド解除
            debug_log('on_activity_result unbind')
            activity.unbind(on_activity_result=self._on_activity_result)

        if t_end:
            self.result = t_result
        debug_log('on_activity_result return')

# android 7
# 外部ストレージの指定フォルダのアクセス許可を得て当該uriを返す
def adr_open_dir_7(p_dir_name = ADR_ENV_DIR_DEFAULT):   # 指定フォルダ 以下の何れか
                                                        # ADR_ENV_DIR_MUSIC
                                                        # ADR_ENV_DIR_PODCASTS
                                                        # ADR_ENV_DIR_RINGTONES
                                                        # ADR_ENV_DIR_ALARMS
                                                        # ADR_ENV_DIR_NOTIFICATIONS
                                                        # ADR_ENV_DIR_PICTURES
                                                        # ADR_ENV_DIR_MOVIES
                                                        # ADR_ENV_DIR_DOWNLOADS
                                                        # ADR_ENV_DIR_DCIM
                                                        # ADR_ENV_DIR_DOCUMENTS
                                                        # ADR_ENV_DIR_ROOT
                                                        # ADR_ENV_DIR_DEFAULT : DOCUMENTS
                                                            # 当該フォルダのuri
    # Android 7.0
    # https://techium.hatenablog.com/entry/2016/08/27/090000

    ### private void startStorageAccessIntent(int requestCode){
    ###             |
    ### sm = (StorageManager)getSystemService(Context.STORAGE_SERVICE);
    ### StorageVolume volume = sm.getPrimaryStorageVolume();
    from android import mActivity, activity
    t_sto_mng = mActivity.getSystemService(Context.STORAGE_SERVICE)
    t_sto_vol = t_sto_mng.getPrimaryStorageVolume()

    ### Intent intent = volume.createAccessIntent(Environment.DIRECTORY_DCIM);
    ### startActivityForResult(intent, requestCode);
    t_intent = t_sto_vol.createAccessIntent(p_dir_name)

    #          当該androidは、許可があると再確認が来ない

    # コールバッククラスインスタンス作成 & コールバックをセット
    t_request_access = __RequestAccessCallback_OpenDir(cssys.REQUEST_ACCESS_STORAGE)
    # intent 発行
    mActivity.startActivityForResult(t_intent, cssys.REQUEST_ACCESS_STORAGE)
    """
        例外が発生したら以下を検討
        except:
            t_intent = Intent()
            t_intent.setAction(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)

            # コールバッククラスインスタンス作成 & コールバックをセット
            t_request_access = RequestAccessCallback_P1(REQUEST_ALL_FILE_PERMISSION)

            # intent 発行
            debug_log('startActivityForResult 2')
            mActivity.startActivityForResult(t_intent, REQUEST_ALL_FILE_PERMISSION)
    """

    # 許可の応答を待つ
    debug_log('request_access wait start')
    t_uri = None
    while True:
        if t_request_access.result != None:
        # 結果が入った
            if t_request_access.result:
            # 許可
                t_uri = t_request_access.dir_uri
            break
        else:
            # wait
            pass

    debug_log('request_access wait end')
    return t_uri

# android 11
# 外部ストレージのフォルダのアクセス許可を得て当該uriを返す
def adr_open_dir_11(p_init_dir = "Documents"):  # 初期フォルダ
                                                # 当該フォルダのuri
                                                # True:初期フォルダ False:初期フォルダ以外
    ROUTIN = 'adr_open_dir_11.. '
    ## Intent   = autoclass('android.content.Intent')
    ## DocumentsContract = autoclass('android.provider.DocumentsContract')

    ### 参照サイト
    ### https://stackoverflow-com.translate.goog/questions/67552027/android-11-action-open-document-tree-set-initial-uri-to-the-documents-folder?_x_tr_sl=en&_x_tr_tl=ja&_x_tr_hl=ja&_x_tr_pto=sc

    ## StorageManager sm = (StorageManager) context.getSystemService(Context.STORAGE_SERVICE);
    t_sto_mng = mActivity.getSystemService(Context.STORAGE_SERVICE)

    ## Intent intent = sm.getPrimaryStorageVolume().createOpenDocumentTreeIntent();
    t_sto_vol = t_sto_mng.getPrimaryStorageVolume()
    t_intent  = t_sto_vol.createOpenDocumentTreeIntent()

    ## //String startDir = "Android";
    ## //String startDir = "Download"; // Not choosable on an Android 11 device
    ## //String startDir = "DCIM";
    ## //String startDir = "DCIM/Camera";  // replace "/", "%2F"
    ## //String startDir = "DCIM%2FCamera";
    ## String startDir = "Documents";
    ###  t_start_Dir = p_init_dir

    ## Uri uri = intent.getParcelableExtra("android.provider.extra.INITIAL_URI");
    t_tmp_uri = t_intent.getParcelableExtra("android.provider.extra.INITIAL_URI");

    ## String scheme = uri.toString();
    t_scheme = t_tmp_uri.toString()

    ## scheme = scheme.replace("/root/", "/document/");
    t_scheme = t_scheme.replace("/root/", "/document/");

    ## scheme += "%3A" + startDir;
    t_scheme += "%3A" + p_init_dir;

    # t_scheme : 以下の内容であるはず これは選択結果uriとは違う
    # content://com.android.externalstorage.documents/document/primary%3ADocuments
    ### debug_log('init.. ' + t_scheme)

    # 初期フォルダuriを作成
    ## uri = Uri.parse(scheme);
    t_init_dir_uri = Uri.parse(t_scheme);
    test_adr_uri(t_init_dir_uri, ROUTIN + '[ init folder uri ]', True)

    # 初期フォルダが既に許可があるか

    t_exist_permission = False
    t_open_uri = None

    debug_log('')
    debug_log('### permissinlist start ###')
    SPC = '     '
    # アプリによって保持されているすべての URI 権限付与のリストを得る
    t_resolver = mActivity.getContentResolver()
    for t_uri_permission in t_resolver.getPersistedUriPermissions():   # PersistedUriPermissions:
        t_permission_uri = t_uri_permission.getUri()

        # content://com.android.externalstorage.documents/tree/primary%3ADocuments
        debug_log(SPC + t_permission_uri.toString())
        if uri_dir_is_same(t_permission_uri, t_init_dir_uri):
        # 同一フォルダである
            debug_log(SPC + '-> same folder')
            debug_log(SPC + '-> ' + t_uri_permission.toString())
            t_open_uri = t_permission_uri

            ## 本来は以下にしたいところであるが、
            ##     if t_uri_permission.isWritePermission():
            ## どこを調べても Write にならないので、以下にする
            if (t_uri_permission.isReadPermission() or
                t_uri_permission.isWritePermission()   ):
                debug_log(SPC + '-> exist permission')
                t_exist_permission = True
            # 調査中止
            break
    debug_log('### permissinlist end ###')

    if t_exist_permission:
    # 初期フォルダが既に許可がある
        t_same_folder = True
        return t_open_uri, t_same_folder

    # 許可を求める

    from jnius import cast
    t_Parcelable_uri = cast('android.os.Parcelable', t_init_dir_uri)    # 当ステップがないと例外エラーとなる

    ## intent.putExtra("android.provider.extra.INITIAL_URI", uri);
    t_intent.putExtra("android.provider.extra.INITIAL_URI", t_Parcelable_uri);

    # コールバッククラスインスタンス作成 & コールバックをセット
    t_request_access = __RequestAccessCallback_OpenDir(cssys.REQUEST_ACCESS_STORAGE)
    # intent 発行
    mActivity.startActivityForResult(t_intent, cssys.REQUEST_ACCESS_STORAGE)

    # 許可の応答を待つ
    debug_log('request_access wait start')
    t_open_uri = None
    while True:
        if t_request_access.result != None:
        # 結果が入った
            if t_request_access.result:
            # 許可
                t_open_uri = t_request_access.dir_uri
            break
        else:
            # wait
            pass

    debug_log('request_access wait end')
    test_adr_uri(t_open_uri, ROUTIN + '[ open folder uri ]', True)

    # 一致しているか
    """
    t_same_folder = (t_init_dir_uri.getHost()            == t_open_uri.getHost()           ) and \
                    (t_init_dir_uri.getLastPathSegment() == t_open_uri.getLastPathSegment())

    """
    t_same_folder = uri_dir_is_same(t_init_dir_uri, t_open_uri)

    return t_open_uri, t_same_folder

# 外部ストレージの指定フォルダのアクセス許可を得て当該uriを返す
def adr_open_dir(p_dir_name = ADR_ENV_DIR_DEFAULT):     # 指定フォルダ 以下の何れか
                                                        # ADR_ENV_DIR_MUSIC
                                                        # ADR_ENV_DIR_PODCASTS
                                                        # ADR_ENV_DIR_RINGTONES
                                                        # ADR_ENV_DIR_ALARMS
                                                        # ADR_ENV_DIR_NOTIFICATIONS
                                                        # ADR_ENV_DIR_PICTURES
                                                        # ADR_ENV_DIR_MOVIES
                                                        # ADR_ENV_DIR_DOWNLOADS
                                                        # ADR_ENV_DIR_DCIM
                                                        # ADR_ENV_DIR_DOCUMENTS
                                                        # ADR_ENV_DIR_ROOT
                                                        # ADR_ENV_DIR_DEFAULT : DOCUMENTS
                                                            # 当該フォルダのuri
                                                            # 日本語エラーメッセージ
    t_errmsg = ''
    t_download_uri = None

    # androidバージョンクラス
    adr_ver = cssys.AndroidVersion()
    if adr_ver.is_7_9:
    # Android 7～9
        # 外部ストレージの指定フォルダのアクセス許可を得て当該uriを返す
        t_download_uri = adr_open_dir_7(p_dir_name)
    elif adr_ver.more_than_11:
    # Android 11 以上
        t_init_dir = ''
        if p_dir_name == ADR_ENV_DIR_MUSIC:
            t_init_dir = 'Music'
        elif p_dir_name == ADR_ENV_DIR_PODCASTS:
            t_init_dir = 'Podcasts'
        elif p_dir_name == ADR_ENV_DIR_RINGTONES:
            t_init_dir = 'Ringtones'
        elif p_dir_name == ADR_ENV_DIR_ALARMS:
            t_init_dir = 'Alarms'
        elif p_dir_name == ADR_ENV_DIR_NOTIFICATIONS:
            t_init_dir = 'Notifications'
        elif p_dir_name == ADR_ENV_DIR_PICTURES:
            t_init_dir = 'Pictures'
        elif p_dir_name == ADR_ENV_DIR_MOVIES:
            t_init_dir = 'Movies'
        elif p_dir_name == ADR_ENV_DIR_DOWNLOADS:
            t_init_dir = 'Download'
        elif p_dir_name == ADR_ENV_DIR_DCIM:
            t_init_dir = 'DCIM'
        elif p_dir_name == ADR_ENV_DIR_DOCUMENTS:
            t_init_dir = 'Documents'
        elif p_dir_name == ADR_ENV_DIR_ROOT:
            ## t_errmsg = ROUTIN + 'Root is invalid'
            t_errmsg = 'ROOTの指定はできません'
        else:
            ## t_errmsg = ROUTIN + 'ADR_ENV_DIR is invalid'
            t_errmsg = 'ADR_ENV_DIRが無効です'

        if t_errmsg == '':
            # 外部ストレージのフォルダのアクセス許可を得て当該uriを返す
            t_download_uri, t_same_dir = adr_open_dir_11(t_init_dir)
            if not t_same_dir:
            # 指定されたものが相違した
                t_errmsg = '無効なフォルダが指定されました'
    else:
        t_errmsg = ROUTIN + 'anddroidバージョンが無効です'

    # 最終確認
    if t_errmsg == '':
        if t_download_uri == None:
            ## raise Exception(ROUTIN + "can't open directory!")
            ## t_errmsg = ROUTIN + "can't open directory!"
            t_errmsg = "フォルダが取得できません"

    return t_download_uri, t_errmsg

# フォルダ内の全FileFolderリストを得る
def adr_find_files(p_folder_uri,            # 検索するフォルダuri
                   p_select_file_name = '', # 一致ファイル名先頭テキスト ex. xxx とした場合は xxx*
                   p_file_folder_all = 1):  # 1:ファイルのみ 2:フォルダのみ 3:全て
                                            # フォルダ内の全DocumentFileリスト
    ROUTIN = 'adr_find_files.. '

    # uri から DocumentFile を得る
    t_folder_doc = cssys.uri_to_doc(p_folder_uri)
    t_all_docs = t_folder_doc.listFiles()
    if (p_select_file_name == '') and \
       (p_file_folder_all  ==  3)       :
    # 条件無し
        return t_all_docs

    # 条件有り
    t_result_docs = []

    # 全FileFolder ループ
    for t_doc in t_all_docs:
        t_ok = False

        if p_file_folder_all == 1:
        # 1:ファイルのみ
            t_ok = t_doc.isFile()
        elif p_file_folder_all == 2:
        # 2:フォルダのみ
            t_ok = t_doc.isDirectory()
        else:
            raise Exception(ROUTIN + 'parameter error!')

        if t_ok:
            if p_select_file_name != '':
            # ファイル名比較必要
                t_ok = t_doc.getName().startswith(p_select_file_name)
        if t_ok:
            t_result_docs.append(t_doc)

    return t_result_docs

# DocumentFileリストからgetPath()を検索する
def adr_get_docs_index_by_getpath(p_docs,       # docリスト
                                  p_get_path):  # 検索する getPath()値
                                                # index < 0:エラー
    t_resut = -1
    t_idx = -1
    for t_doc in p_docs:
        t_idx += 1
        if t_doc.getUri().getPath() == p_get_path:
            t_result = t_idx
            break
    return t_result

# DocumentFileリストをパス順にソートする
def adr_docs_sort(p_org_docs):  # 元docリスト
                                # ソート後docリスト

    return adr_docs_sort_name(p_org_docs)

def adr_docs_sort_name(p_org_docs): # 元docリスト
                                    # ソート後docリスト
    ROUTIN = 'adr_docs_sort_name : '
    # 文字列リストにコピーする
    t_names = []
    for t_org_doc in p_org_docs:
        t_names.append(t_org_doc.getUri().getPath())
    # 文字列リストをソートする
    t_names = sorted(t_names)

    t_new_docs = []
    # ソートした文字列リストループ
    for t_name in t_names:
        # DocumentFileリストからgetPath()を検索する
        t_idx = adr_get_docs_index_by_getpath(p_org_docs, t_name)
        if t_idx < 0:
            raise Exception(ROUTIN + 'not found path')
        t_new_docs.append(p_org_docs[t_idx])

    return t_new_docs

# DocumentFileリストを時間順にソートする
def adr_docs_sort_time(p_org_docs): # 元docリスト
                                    # ソート後docリスト
    ROUTIN = 'adr_docs_sort_time : '

    # 文字列リストにコピーする
    t_idx = -1
    t_timetexts = []
    for t_org_doc in p_org_docs:
        t_idx += 1
        t_dt = t_org_doc.lastModified()
        t_text  = t_dt.strftime('%Y%m%d%H%M%S')
        t_text += '@' + str(t_idx)
        # 追加
        t_timetexts.append(t_text)

    # 文字列リストをソートする
    t_timetexts = sorted(t_timetexts)

    t_new_docs = []
    # ソートした文字列リストループ
    for t_timetext in t_timetexts:
        t_texts = t_timetext.split('@')
        if len(t_texts) != 2:
            raise Exception(ROUTIN + 'internal error!')
        t_idx = int(t_texts[1])
        t_new_docs.append(p_org_docs[t_idx])

    return t_new_docs

# uri から最終フォルダまたはファイル名を得る
def adr_get_lastname_of_uri(p_uri): # uri
                                    # 最終フォルダまたはファイル名

    t_text = p_uri.getLastPathSegment()
    t_texts = t_text.split(PATH_DELM)
    if len(t_texts) > 1:
        t_text = t_texts[len(t_texts) - 1]
    else:
        t_text = t_text

    t_texts = t_text.split(':')
    if len(t_texts) > 1:
        return t_texts[len(t_texts) - 1]
    else:
        return t_text

# uri から最終フォルダまたはファイル名とドライブフォルダ部を分割する
def adr_sepa_path_of_uri(p_uri):    # uri
                                    # ドライブフォルダ部
                                    # 最終フォルダまたはファイル名
    ROUTIN = 'adr_sepa_name_of_uri.. '
    # uri から最終フォルダまたはファイル名を得る
    t_lastname = adr_get_lastname_of_uri(p_uri)

    t_full_path = p_uri.getPath()
    t_texts = t_full_path.split(PATH_DELM + t_lastname)
    if len(t_texts) != 2:
        raise Exception(ROUTIN + 'not found path')
    return t_texts[0], t_lastname

# ファイルコピー
def adr_copy_file_by_uri(p_send_file_uri,       # 送り側ファイル
                         p_recv_parent_dir_uri, # 受け側親フォルダ
                         p_overwrite = True):   # True:上書き False:(1) (2).. とファイルができる

    ROUTIN = 'adr_copy_file_by_uri.. '
    #---
    test_adr_uri(p_send_file_uri,       'copy_file send file')
    test_adr_uri(p_recv_parent_dir_uri, 'copy_file recv dir')
    #---

    # uri から最終フォルダまたはファイル名を得る
    t_lastname = adr_get_lastname_of_uri(p_send_file_uri)

    """ 参考
    https://www.memory-lovers.blog/entry/2017/09/25/221651
    https://qiita.com/kksk/items/35c16e50466485e11ddc
    https://prettytabby.com/mime-type-list/
    """

    # 送り側ファイルをオープンし 存在を確認する
    t_in = mActivity.getContentResolver().openInputStream(p_send_file_uri)
    if t_in == None:
        raise Exception(ROUTIN + 'Can not open ' + p_send_file_uri.getPath())

    # 受け側フォルダのdoc作成
    t_recv_dir_doc = cssys.uri_to_doc(p_recv_parent_dir_uri)

    if p_overwrite:
    # True:上書き
    # オープンする受け側ファイルが存在すれば消す
        t_delete_file_doc = t_recv_dir_doc.findFile(t_lastname)
        if t_delete_file_doc != None:
        # 存在する
            # 削除する
            if t_delete_file_doc.delete():
                debug_log(ROUTIN + f'deleted {t_lastname}')
            else:
                raise Exception(ROUTIN + "can't delete {}, {}".format(t_recv_dir_doc.uri.getPath(), t_lastname))
        else:
        # 存在しない
            pass
    else:
    # (1) (2).. とファイルができる
        pass

    # 受け側ファイルをオープンする
    t_recv_file_doc = t_recv_dir_doc.createFile("application/octet-stream", t_lastname)
    if t_recv_file_doc == None:
        raise Exception(ROUTIN + "can't createFile {}, {}".format(t_recv_dir_doc.getUri().getPath(), t_lastname))
    t_out = mActivity.getContentResolver().openOutputStream(t_recv_file_doc.uri)
    if t_out == None:
        raise Exception(ROUTIN + "can't open " + t_recv_file_doc.getUri().getPath())

    # 読み書き
    t_buf = [0] * 1024

    while True:
        # 読む
        t_buf_count = t_in.read(t_buf, 0, 1024)
        if t_buf_count > 0:
            # データがあるので書き込む
            ## t_out.write(t_buf)
            t_out.write(t_buf, 0, t_buf_count)

        # 終了の判定
        if t_buf_count < 1024:
            break
    pass

    t_in.close()
    t_out.close()

    # サイズ比較
    t_recv_size = adr_get_file_size(t_recv_file_doc.getUri())
    if t_recv_size != adr_get_file_size(p_send_file_uri):
        raise Exception(ROUTIN + 'File copy failed ! not equal file size ' + p_send_file_uri.getPath())
    return

# Android/data access テスト
def test_adr_data_access():
    # Android 10 11 は以下を参照
    # https://stackoverflow-com.translate.goog/questions/65967690/how-do-some-apps-reach-the-contents-of-android-sub-folders-on-android?_x_tr_sl=en&_x_tr_tl=ja&_x_tr_hl=ja&_x_tr_pto=sc

    # queryによりリストを得る
    ANDROID_DOCID = "primary:Android"
    ## ANDROID_DOCID = "primary:Android/data"
    """
    t_android_uri = DocumentsContract.buildDocumentUri(
                                                EXTERNAL_STORAGE_PROVIDER_AUTHORITY,
                                                ANDROID_DOCID)
    """
    t_android_tree_uri = DocumentsContract.buildTreeDocumentUri(
                                                EXTERNAL_STORAGE_PROVIDER_AUTHORITY,
                                                ANDROID_DOCID)

    t_parent_doc_id = DocumentsContract.getTreeDocumentId(t_android_tree_uri) + "/data/"

    t_children_uri = DocumentsContract.buildChildDocumentsUriUsingTree(t_android_tree_uri,
                                                                       t_parent_doc_id)
    debug_log('** get list by query')
    debug_log(t_children_uri.getPath())

    t_cursor = mActivity.getContentResolver().query(t_children_uri, None, None, None)

    nameIndex = t_cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME) # other.. SIZE
    mimeIndex = t_cursor.getColumnIndex("mime_type")

    print('** query list start!')
    while t_cursor.moveToNext():
        print('**')
        print(t_cursor.getString(nameIndex))
        print(t_cursor.getString(mimeIndex))
        # OK!
    print('** query list end')

    # query を使用せず リストを得る
    ## ANDROID_DOCID = "primary:Android"
    ANDROID_DOCID = "primary:Android/data"

    t_android_tree_uri = DocumentsContract.buildTreeDocumentUri(
                                        EXTERNAL_STORAGE_PROVIDER_AUTHORITY,
                                        ANDROID_DOCID)
    """
    t_children_uri = DocumentsContract.buildChildDocumentsUriUsingTree(t_android_tree_uri,
                                DocumentsContract.getTreeDocumentId(t_android_tree_uri)+"/data/")
    """
    t_android_tree_doc = DocumentFile.fromTreeUri(mActivity, t_android_tree_uri);

    t_xxx_doc = t_android_tree_doc.findFile('xxx.xxx')   # data/xxx.xxx テストデータ
    if t_xxx_doc == None:
        debug_log("Can't access xxx.xxx ")
    else:
        t_xxx_uri = t_xxx_doc.getUri()
        t_in = mActivity.getContentResolver().openInputStream(t_xxx_doc.getUri())
        if t_in != None:
            debug_log('Open Ok : ' + t_xxx_uri.getPath())
        else:
            debug_log('Cant open : ' + t_xxx_uri.getPath())

        debug_log('** list start')
        t_send_docs = t_android_tree_doc.listFiles()
        for t_send_doc in t_send_docs:
            t_uri = t_send_doc.getUri()
            debug_log(t_uri.getPath())
        debug_log('** list end')
    return

# androidのバージョンにより必要に応じて android/data であれば、uriをスワップする
def swap_adr_data_uri(p_uri):   # 元uri
                                # 新uri
    ROUTIN = 'swap_adr_data_uri : '

    t_adr_ver = cssys.AndroidVersion()
    ## if not t_adr_ver.is_10_11:
    if t_adr_ver.is_7_9:
    # スワップ不要
        return p_uri

    t_path = p_uri.getEncodedPath()
    t_texts = t_path.split('/storage/emulated/0/Android/data/')

    if len(t_texts) == 2  and \
       t_texts[0]   == '':
    # スワップ必要有
        debug_log(ROUTIN + 'uri swap :  ' + t_path)

        ## ANDROID_DOCID = "primary:Android"
        ANDROID_DOCID = "primary:Android/data" + PATH_DELM + t_texts[1]

        t_uri = DocumentsContract.buildTreeDocumentUri(
                                            EXTERNAL_STORAGE_PROVIDER_AUTHORITY,
                                            ANDROID_DOCID)
        debug_log(ROUTIN + 'uri swap -> ' + t_uri.getEncodedPath())
    else:
    # スワップ必要無
        debug_log(ROUTIN + 'uri not swap : ' + t_path)
        t_uri = p_uri
    return t_uri

# フォルダコピー
#    受け側フォルダが存在しなければ作成する
def adr_copy_dir_by_uri(p_send_dir_uri,             # 送り側フォルダ
                           p_recv_parent_dir_uri,   # 受け側親フォルダ
                           p_on_copy_file=None):    # コピーファイル前後イベント

    ROUTIN = 'adr_copy_dir_by_uri : '
    #---
    test_adr_uri(p_send_dir_uri,        'copy_dir send : ', False)
    test_adr_uri(p_recv_parent_dir_uri, 'copy_dir recv : ', False)
    #---

    # 受け側親フォルダの直下に送り側フォルダ作成

    # (uri から最終フォルダまたはファイル名を得る)
    t_send_lastname = adr_get_lastname_of_uri(p_send_dir_uri)

    """
    print('***************')
    print(t_send_lastname)
    print('***************')
    """

    # フォルダが存在しなければ全作成する
    #    作成フォルダリストは既存でも良い
    t_errmsg, t_recv_dir_doc = adr_makedirs(p_recv_parent_dir_uri, [t_send_lastname])
    if t_errmsg != '':
        raise Exception(ROUTIN + t_errmsg)

    """
    # android 10 11 で、android/data であれば、uriをスワップする
    t_adr_ver = cssys.AndroidVersion()
    if t_adr_ver.is_10_11:
        # android/data であれば、uriをスワップする
        p_send_dir_uri        = swap_adr_data_uri(p_send_dir_uri)
        p_recv_parent_dir_uri = swap_adr_data_uri(p_recv_parent_dir_uri)
    """
    # androidのバージョンに応じて必要であり、android/data であれば、uriをスワップする
    p_send_dir_uri        = swap_adr_data_uri(p_send_dir_uri)
    p_recv_parent_dir_uri = swap_adr_data_uri(p_recv_parent_dir_uri)

    # 送り側のメンバーループ
    t_send_dir_doc = cssys.uri_to_doc(p_send_dir_uri)
    t_send_docs = t_send_dir_doc.listFiles()

    """
    print(t_send_dir_doc.getUri().getPath())
    if t_send_dir_doc.canRead():
        print('can read')
    else:
        print('can not read')
    print(len(t_send_docs))
    """

    for t_send_doc in t_send_docs:
        # print(t_send_doc)
        if t_send_doc.isDirectory():
        # フォルダ
            # フォルダコピー
            adr_copy_dir_by_uri(t_send_doc.getUri(), t_recv_dir_doc.getUri(),
                                p_on_copy_file)
        else:
        # ファイル
            # ファイルコピー
            if p_on_copy_file != None:
                t_uri = t_send_doc.getUri()
                p_on_copy_file(t_uri.getPath())

            adr_copy_file_by_uri(t_send_doc.getUri(), t_recv_dir_doc.getUri())

            if p_on_copy_file != None:
                p_on_copy_file('')

    # フォルダサイズを得る
    t_send_size = adr_get_dir_size(t_send_dir_doc.getUri())
    t_recv_size = adr_get_dir_size(t_recv_dir_doc.getUri())

    if t_send_size != t_recv_size:
        raise Exception(ROUTIN + 'Folder copy failed ! ' + p_send_dir_uri.getPath())

    debug_log('size : ' + str(t_send_size) + '  Copy folder : ' + p_send_dir_uri.getPath())
    return
