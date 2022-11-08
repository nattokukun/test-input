# -*- coding: utf-8 -*-
#//////////////////////////////////////////////////////////////////////////////
#            fmng  File Manager
#            M.Ida 2022.03.04
#//////////////////////////////////////////////////////////////////////////////
import traceback
import os
import cssys
from cssys import debug_log
## import const
from pickle import NONE
from struct import pack, unpack, calcsize, iter_unpack

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

#------------------------------------------------------------------------------
#                   クラス
#------------------------------------------------------------------------------
# アプリ固定ファイルクラス
class AppSpecificFile:
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            コンストラクタ
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def __init__(self, p_file_name):    # dirを除く 単体ファイル名
        if not cssys.is_android():
            raise 'AppSpecificFile is android only class!'
        self.file_name   = p_file_name
        self.fout_stream = None
        self.finp_stream = None
        self.buf_reader  = None
        self.read_eof    = False

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            アウトプットオープン
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def open_output(self):
        # 当該ファイルは
        self.fout_stream = Context.openFileOutput(self.file_name, Context.MODE_PRIVATE)

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            インプットオープン
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def open_input(self):
                            # True:オープン成功
        t_ok = False
        try:
            self.finp_stream = Context.openFileInput(self.file_name)
            self.read_eof    = False
            t_ok = True
        except:
            self.finp_stream = None
            self.read_eof    = False
        return t_ok

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
    def write(self, p_text):    # 書き込むテキスト
        if self.fout_stream == None:
            raise 'AppSpecificFile write : not open!'
        self.fout_stream.write(bytearray(p_text.encode()));

    def write_line(self, p_text):   # 書き込むテキスト
        t_text = p_text + '\n'
        self.write(t_text)

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            テキスト行入力
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def read_line(self):
                            # テキスト行 None:eof
        if self.finp_stream == None:
            raise 'AppSpecificFile read_line : not open!'

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
def get_dir_size(p_dir='.'):      # フォルダ名
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
def get_path_size(p_path='.'):    # フォルダ名orファイル名
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
def not_found_mkdir(p_path):  # フォルダ名絶対パス
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
def adr_get_file_size(p_file_uri):   # ファイルuri
                                        # サイズ < 0:存在しない

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
def adr_makedirs(p_parent_uri,    # 指定フォルダ Uri
                   p_child_dirs):   # 作成フォルダリスト
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

# Uriからドライブパスとフォルダ以降のパスを得る
def uri_to_drvpath(p_uri):   # uri
                                # ドライブパス        ex. /storage/F677-248B/
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

# アプリ固有の物理ストレージフォルダ uri を得る /storage/emulated/0/Android/data
def get_external_app_dir_uri():
                                    # アプリ固有の物理ストレージフォルダ uri を得る
    t_external_storage_volume_files = \
            ContextCompat.getExternalFilesDirs(mActivity.getApplicationContext(), None);
    t_primary_file = t_external_storage_volume_files[0]; # 0がプライマリー
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
def get_adr_primary_external_storage_uri(p_app_context):     # True:Application Context
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

    print(' ')
    print('   ' + p_title)
    print(' 1:' + p_uri.getAuthority())
    print(' 2:' + p_uri.getEncodedAuthority())
    ## print(' 3:' + p_uri.getEncodedFragment())
    print(' 4:' + p_uri.getEncodedPath())
    print(' 5:' + p_uri.getEncodedSchemeSpecificPart())
    ## print(' 6:' + p_uri.getEncodedUserInfo())
    ## print(' 7:' + p_uri.getFragment())
    print(' 8:' + p_uri.getHost())
    print(' 9:' + p_uri.getLastPathSegment())
    print('10:' + p_uri.getPath())
    print('11:' + p_uri.getScheme())
    print('12:' + p_uri.getSchemeSpecificPart())
    ## print('13:' + p_uri.getUserInfo())
    print('14:' + p_uri.toString())

    """
    t_file_id = DocumentsContract.getDocumentId(p_uri)
    ## file_type, file_name = file_id.split(':')
    print('file id :' + t_file_id)
    """

    """
    # : が存在する場合を SD とする
    t_sd = ':' in p_uri.getPath()
    if t_sd:
        print('   This is SD')
    else:
        print('   This is not SD')

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
    t_doc = cssys.uri_to_doc(p_uri)

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

    print('   ' + t_msg + ' : ' + p_uri.getPath())
    print(' ')
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

# パスをドライブ部uriとフォルダ部pathに分ける
def path_to_uri_dir(p_path):     # パス
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

# DocumentFileリストからgetPath()を検索する
def adr_get_docs_index_by_getpath(p_docs,      # docリスト
                                       p_get_path): # 検索する getPath()値
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
def adr_docs_sort(p_org_docs):    # 元docリスト
                                    # ソート後docリスト
    ROUTIN = 'adr_doc_sort : '
    # 文字列リストにコピーする
    t_new_names = []
    for t_org_doc in p_org_docs:
        t_new_names.append(t_org_doc.getUri().getPath())
    # 文字列リストをソートする
    t_new_names = sorted(t_new_names)

    t_new_docs = []
    # ソートした文字列リストループ
    for t_new_name in t_new_names:
        # DocumentFileリストからgetPath()を検索する
        t_idx = adr_get_docs_index_by_getpath(p_org_docs, t_new_name)
        if t_idx < 0:
            raise Exception(ROUTIN + 'not found path')
        t_new_docs.append(p_org_docs[t_idx])

    return t_new_docs

# uri から最終フォルダまたはファイル名を得る
def adr_get_lastname_of_uri(p_uri):  # uri
                                        # 最終フォルダまたはファイル名

    t_text = p_uri.getLastPathSegment()
    t_texts = t_text.split(PATH_DELM)
    if len(t_texts) > 1:
      return t_texts[len(t_texts) - 1]
    else:
      return t_text

# ファイルコピー
def adr_copy_file_by_uri(p_send_file_uri,          # 送り側ファイル
                            p_recv_parent_dir_uri):    # 受け側親フォルダ

    ROUTIN = 'adr_copy_file_by_uri : '
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

    # 受け側ファイルをオープンする
    t_recv_dir_doc = cssys.uri_to_doc(p_recv_parent_dir_uri)
    t_recv_file_doc = t_recv_dir_doc.createFile("application/octet-stream", t_lastname)
    t_out = mActivity.getContentResolver().openOutputStream(t_recv_file_doc.uri)
    if t_out == None:
        raise Exception(ROUTIN + 'Can not open ' + t_recv_file_doc.uri.getPath())

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
    """
    print('-----')
    t_send_file_doc = cssys.uri_to_doc(p_send_file_uri)
    t_uri = t_send_file_doc.getUri()
    print(t_uri.getPath())
    print(t_send_file_doc.length())

    print('-----')
    t_uri = t_recv_file_doc.getUri()
    print(t_uri.getPath())
    print(t_recv_file_doc.length())
    """

    """
    t_send_file_doc = cssys.uri_to_doc(p_send_file_uri)
    if t_recv_file_doc.length() != t_send_file_doc.length():
        raise Exception(ROUTIN + 'File copy failed ! ' + p_send_file_uri.getPath())
    """
    t_recv_size = adr_get_file_size(t_recv_file_doc.getUri())
    if t_recv_size != adr_get_file_size(p_send_file_uri):
        raise Exception(ROUTIN + 'File copy failed ! ' + p_send_file_uri.getPath())
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
def swap_adr_data_uri(p_uri):    # 元uri
                                    # 新uri
    ROUTIN = 'swap_adr_data_uri : '

    t_adr_ver = cssys.AndroidVersion()
    if not t_adr_ver.is_10_11:
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
def adr_copy_dir_by_uri(p_send_dir_uri,            # 送り側フォルダ
                           p_recv_parent_dir_uri,     # 受け側親フォルダ
                           p_on_copy_file=None):      # コピーファイル前後イベント

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
