# -*- coding: utf-8 -*-
#//////////////////////////////////////////////////////////////////////////////
#            cssys Custom System
#            M.Ida 2022.03.18
#//////////////////////////////////////////////////////////////////////////////
# Debug 用
from kivy.logger import Logger
from kivy.config import Config
from pickle import TRUE
## from pickle import FALSE, TRUE

# ログ設定
Config.set('kivy', 'log_level', 'debug')  # デフォルトで debug になってないので
Config.set('kivy', 'log_enable', 1)
Config.set('kivy', 'log_dir', 'logs')  # 変更しなければ上でみた通り
Config.set('kivy', 'log_name', 'kivy_%y-%m-%d_%_.txt')  # 変更しなければ上でみた通り

import traceback
import platform
import os

## import const
#------------------------------------------------------------------------------
#                   関数群
#------------------------------------------------------------------------------
# デバッグログ
def debug_log(p_msg):
    t_msg = p_msg .replace(':', '$')
    t_msg = t_msg.replace('\n', ' ')
    Logger.debug('### ' + t_msg)

debug_log('************** Logger debug start *************')

# Windowsであるか
def is_windows():
    return (platform.system() == 'Windows')

# Androidであるか
def is_android():
    t_name = platform.system()
    ## debug_log(t_name)
    return (t_name == 'Linux' or t_name == 'Android')

#------------------------------------------------------------------------------
#                   初期処理
#------------------------------------------------------------------------------
# クリア
gl_errmsg = ''

# Android 用
if is_android():
    try:
        from jnius import autoclass
    except:
        gl_errmsg = traceback.format_exc()

    if gl_errmsg == '':
        # 何故か以下を実行する必要あり
        try:
            autoclass('org.jnius.NativeInvocationHandler')
        except:
            gl_errmsg = traceback.format_exc() + '\n' + 'autoclass exec error!'
        pass

    if gl_errmsg == '':
        """
        ANDROID_7  = 24
        ANDROID_10 = 29
        ANDROID_11 = 30
        """
        # from plyer.platforms.android import SDK_INT
        VERSION  = autoclass('android.os.Build$VERSION')

        from jnius import cast
        from android import permissions
        from android.permissions import request_permissions, Permission, \
                                        check_permission
        # from plyer.platforms.android import activity
        from android import mActivity, activity
        Activity = autoclass('android.app.Activity')
        Context  = autoclass('android.content.Context')
        Intent   = autoclass('android.content.Intent')
        File     = autoclass('java.io.File')
        """
        java.lang.Object
            java.io.Writer
                java.io.OutputStreamWriter
        """
        OutputStreamWriter = autoclass('java.io.OutputStreamWriter')
        """
        java.lang.Object
            android.support.v4.provider.DocumentFile
                -new-
        java.lang.Object
            androidx.documentfile.provider.DocumentFile
        """
        ## DocumentFile = autoclass('android.support.v4.provider.DocumentFile')
        DocumentFile      = autoclass('androidx.documentfile.provider.DocumentFile')
        DocumentsContract = autoclass('android.provider.DocumentsContract')
        Uri               = autoclass('android.net.Uri')
pass

# 点検
if gl_errmsg != '':
    raise Exception(gl_errmsg)

# Windows用
if is_windows():
    import winsound

#------------------------------------------------------------------------------
#                   定数定義
#------------------------------------------------------------------------------
# Android 用
if is_android():
    ANDROID_7  = 24
    ANDROID_10 = 29
    ANDROID_11 = 30

# 要求コードは任意でユニーク
REQUEST_ACCESS_STORAGE = 101


#------------------------------------------------------------------------------
#                   関数・クラス群
#------------------------------------------------------------------------------

# OpenGLの調整
def adjust_opengl(p_python_ver,                     # pythonバージョンNo
                  p_size_to_android_style=False):   # サイズをandroid風にする
    """
        OpenGLが2.0以上にも関わらず、当該認識をしない場合は、
                Python 3    (A)〇 (B)×
                Python 2    (A)× (B)〇
    """
    if not is_windows():
        # Windows以外は抜ける
        return

    if p_python_ver == 3:
        # OpenGL2.0 を認識しない場合
        os.environ ['KIVY_GL_BACKEND'] = 'angle_sdl2'

    if p_python_ver == 2:
        # OpenGL2.0 を認識しない場合
        from kivy import Config
        Config.set('graphics', 'multisamples', '0')

    if p_size_to_android_style:
        # サイズをandroid風にする
        SHIRINK = 0.37
        from kivy.core.window import Window
        Window.size = (1080 * SHIRINK, 1920 * SHIRINK)

# 外部ストレージパス(実際は内部ストレージパス)を得る
def adr_get_external_storage_dir():    # 外部ストレージパス
    t_environment = autoclass('android.os.Environment')
    t_dir = t_environment.getExternalStorageDirectory()
    # print('******')
    t_str = t_dir.getAbsolutePath()
    # print(t_str)
    # print('******')
    return t_str

# callback 処理クラス
class RequestPermission:
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            コンストラクタ
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def __init__(self):
        self.result = None

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            callbackハンドラ
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def callback(self, p_permissions, p_grants):
        debug_log('on_request_permission_callback start')
        t_ok = True
        for t_grant in p_grants:
            if t_grant == permissions.PERMISSION_GRANTED:
            # 許可
                pass
            if t_grant == permissions.PERMISSION_DENIED:
            # 拒否
                t_ok = False
                break

        if not t_ok:
        # 全て許可されない
            self.result = False
        else:
        # 全て許可
            self.result = True
        debug_log('on_request_permission_callback end')

# 複数権限を点検する
def adr_check_permissions(p_permissions):   # 権限
                                            # True:全て
    t_ok = True
    for t_permission in p_permissions:
        if not check_permission(t_permission):
            t_ok = False
            break
    return t_ok

# 複数権限を得る
def adr_check_request_permissions(p_permissions):   # 権限
                                                    # True:許可
    debug_log('start check request permission')
    # 点検
    t_ok = adr_check_permissions(p_permissions)
    ##    t_ok = False # 以下実行するためのテスト用
    if t_ok:
    # 許可有
        debug_log('check permission ok')
    else:
    # 許可無
        debug_log('check permission None')

        t_request_permission = RequestPermission()
        # 許可を得る
        debug_log('  permission start')
        request_permissions(p_permissions, t_request_permission.callback)
        debug_log('  permission end')

        while True:
            if t_request_permission.result != None:
                break

    debug_log('permission return')
    return True

# ファイル書き込みテスト
def test_adr_file_write(p_dir_doc,          # 場所
                           p_file_name):    # ファイル名
                                            # エラーメッセージ '':成功
    debug_log('filetest_adr_file_write start :' + p_file_name)
    try:
        t_file_doc = p_dir_doc.createFile('text/plain', p_file_name)
        t_resolver = mActivity.getContentResolver()
        t_outstrm  = t_resolver.openOutputStream(t_file_doc.uri) ## t_uri) ## t_file_doc)
        t_outstrm.write(bytearray(b'hoge'))
        t_outstrm.close()
        t_errmsg = ''
    except:
        t_errmsg = 'test_adr_file_write ' + '\n' + \
                    traceback.format_exc()

    debug_log('filetest_adr_file_write end')
    return t_errmsg

# ストレージ検証
def test_adr_storage():
    # StorageManager    STORAGE_SERVICE
    t_sto_mng = mActivity.getSystemService(Context.STORAGE_SERVICE)

    # t_sto_vols = t_sto_mng.getRecentStorageVolumes()
    t_sto_vols = t_sto_mng.getStorageVolumes()
    for t_str_vol in t_sto_vols:
        print('a1 :' + t_str_vol.toString())
        ## getDescription(Context context)
        print('a2 :' + t_str_vol.getDescription(mActivity))
        ## getMediaStoreVolumeName()
        ## print('a3 :' + t_str_vol.getMediaStoreVolumeName())  # error

    t_sto_vol = t_sto_mng.getPrimaryStorageVolume()
    print('b :' + t_str_vol.toString())
    return

# callback 処理クラス
# Android 7～9
class RequestAccessCallback_7_9:
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            コンストラクタ
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def __init__(self, p_request_code):
        self.uri = None
        self.result = None
        self.wait_request_code = p_request_code

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #           callbackハンドラ
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def on_activity_result(self, p_request_code, p_result_code, p_intent):
        debug_log('on_activity_result start')
        t_end = False
        if p_request_code == self.wait_request_code: # REQUEST_ACCESS_STORAGE:
        # 当該リクエスト
            if p_result_code  == Activity.RESULT_OK:
                # 許可を保存
                t_uri = p_intent.getData()
                t_resolver = mActivity.getContentResolver()
                t_resolver.takePersistableUriPermission(t_uri,
                                                        Intent.FLAG_GRANT_READ_URI_PERMISSION or
                                                        Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
                """ ##
                # ファイル書き込みテスト
                t_errmsg = test_adr_file_write(t_uri, 'xx1')
                if t_errmsg != '':
                    raise t_errmsg

                # ファイル書き込みテスト
                t_errmsg = test_adr_file_write(t_uri, 'xx2')
                if t_errmsg != '':
                    raise t_errmsg
                ## """
                # uri sd 保存
                self.uri = t_uri
                debug_log('on_activity_result ok!')
                t_result = True
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
            activity.unbind(on_activity_result=self.on_activity_result)

        if t_end:
            self.result = t_result
        debug_log('on_activity_result return')

# callback 処理クラス
# Android 10～11
class RequestAccessCallback_10_11:
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            コンストラクタ
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def __init__(self, p_request_code):
        self.uri = None
        self.result = None
        self.wait_request_code = p_request_code

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #           callbackハンドラ
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def on_activity_result(self, p_request_code, p_result_code, p_intent):
        debug_log('on_activity_result start')
        t_end = False
        if p_request_code == self.wait_request_code: # REQUEST_ACCESS_STORAGE:
        # 当該リクエスト

            # 以下のifをTrueにする
            p_result_code = Activity.RESULT_OK
            if p_result_code  == Activity.RESULT_OK:
                # 許可を保存
                t_uri = p_intent.getData()

                t_take_flag = (Intent.FLAG_GRANT_READ_URI_PERMISSION or
                               Intent.FLAG_GRANT_WRITE_URI_PERMISSION)

                t_resolver = mActivity.getContentResolver()
                t_resolver.takePersistableUriPermission(t_uri, t_take_flag)

                # uri sd 保存
                self.uri = t_uri
                debug_log('on_activity_result ok!')
                t_result = True
            else:
                # 拒否処理
                debug_log('on_activity_result cancel!')
                t_result = False

            t_end = True
        else:
        # 当該リクエストではない
            debug_log('on_activity_result not request')

        if t_end:
            # バインド解除
            debug_log('on_activity_result unbind')
            activity.unbind(on_activity_result=self.on_activity_result)

        if t_end:
            self.result = t_result
        debug_log('on_activity_result return')


# uri から DocumentFile を得る
def uri_to_doc(p_uri):
                                # :DocumentFile =None:エラー
    ROUTIN = 'uri_to_doc : '
    # : が存在する場合を SD とする
    t_sd_fuu = ':' in p_uri.getPath()
    """
    if t_sd_fuu:
        debug_log('uri_to_doc : This is SD')
    else:
        debug_log('uri_to_doc : This is not SD')
    """
    if not t_sd_fuu:
        t_file = File(p_uri.getPath())
        t_doc = DocumentFile.fromFile(t_file)
    else:
        if p_uri.getScheme() == 'file':
        # SDなのに file の場合は、未対応とする
            """
            # 変換する.. 以下上手くいかない
            t_File = File(p_uri.getPath())
            t_context = Context.getApplicationContext()
            t_uri = FileProvider.getUriForFile(mActivity, \
                                                t_context.getPackageName() + ".provider", \
                                                t_File)
            p_uri = t_uri
            """
            t_doc = None
            raise Exception(ROUTIN + 'this uri not supported!' + p_uri.getPath())
        else:
        # context
            ## t_file = File(p_uri.getPath())
            t_doc = DocumentFile.fromTreeUri(mActivity, p_uri)
    pass
    return t_doc

# ディレクトリアクセス権要求するintent生成
def create_open_doctree_intent(p_volume):   # volume
                                            # intent
    ROUTIN = 'create_open_doctree_intent : '

    if VERSION.SDK_INT >= ANDROID_7:
    # Android 7 以上
        # ok
        pass
    else:
    # Android 7 未満
        raise Exception(ROUTIN + 'Android 7 are not supported')

    if VERSION.SDK_INT >= ANDROID_10:
    # Android 10 以上
    #  権限の記憶ができない？
        t_intent = p_volume.createOpenDocumentTreeIntent()
    else:
    # Android 10 未満
        t_intent = p_volume.createAccessIntent(None) # None:root

    return t_intent

# SDカード uriを得る
def get_sd_uri():
                    # sd_uri ルート

    ROUTIN = 'get_sd_uri : '
    t_storage_manager = mActivity.getSystemService(Context.STORAGE_SERVICE)

    # 全ボリュームを得る
    t_storageVolumes = t_storage_manager.storageVolumes

    t_uri = None
    # 全ボリュームループ
    for t_volume in t_storageVolumes:
        if (t_volume.getUuid() != None) and t_volume.isRemovable:
            """ 7-9 NG
            t_file = t_volume.getDirectory()
            t_uri = Uri.fromFile(t_file)
            #####################
            上記は NG でああるが、ここに入ってくれば SDは存在するのは分かる
            #####################
            """
            android_version = AndroidVersion()
            if android_version.is_10_11:
                t_file = t_volume.getDirectory()
                t_uri = Uri.fromFile(t_file)
            else:
                """
                print('*** ' + t_volume.getUuid())
                """
                """
                t_file = File('/storage/' + t_volume.getUuid() + '/')
                t_uri = Uri.fromFile(t_file)
                t_doc = uri_to_doc(t_uri)
                t_uri = t_doc.getUri()
                """
                raise Exception(ROUTIN + 'android version not supported!')
            break
        pass

    return t_uri

# ストレージアクセス許可を得る
def request_access_storage():
                                        # True:許可(Win:True)
                                        # SDカードuri(Android 7～9)
    t_sd_uri = None
    if is_android():
        t_adr_ver = AndroidVersion()
        if t_adr_ver.is_10_11:
        # Android 10 以上
        # SDカードは許可されているが、Android/data 内が読めない
            t_access_ok = request_access_storage_10_11()
        else:
        # Android 10 未満
        # SDカードの許可が必要
            t_access_ok, t_sd_uri = request_access_storage_7_9()
        """
        if not t_access_ok:
            raise Exception('request_access_storage　: Access Error!')
        """
        debug_log('request_access_storage completed')
    else:
    # android以外
        t_access_ok = True

    return t_access_ok, t_sd_uri

# ストレージアクセス許可を得る
# Android 7～9
def request_access_storage_7_9():
                                        # True:許可
                                        # SDカードuri

    p_fix = False # True:固定ストレージ False:取外ストレージ

    t_ok  = False
    t_uri = None

    if p_fix:
    # 固定は非対応
        raise Exception('request_access_storage : fix storage unsupported!')

    debug_log('get system service')
    # StorageManager    STORAGE_SERVICE
    t_storage_manager = mActivity.getSystemService(Context.STORAGE_SERVICE)

    # 全ボリュームを得る
    t_storageVolumes = t_storage_manager.storageVolumes

    # t_volume : android.os.storage.StorageVolume
    # https://developer.android.com/reference/android/os/storage/StorageVolume
    # https://android-googlesource-com.translate.goog/platform/frameworks/base/+/master/core/java/android/os/storage/StorageVolume.java?_x_tr_sl=en&_x_tr_tl=ja&_x_tr_hl=ja&_x_tr_pto=op,sc

    t_request = False
    # 全ボリュームループ
    for t_volume in t_storageVolumes:
        t_ok = False
        """
        if t_volume.getUuid() != None:
        # 有効
            if p_fix and (not t_volume.isRemovable):
                t_ok = True
            else:
                if (not p_fix) and t_volume.isRemovable:
                    t_ok = True
        """
        """
        if p_fix and (not t_volume.isRemovable):
            t_ok = True
        else:
            if (not p_fix) and t_volume.isRemovable:
                t_ok = True
        """
        # 注意！固定ストレージが上手くいかない
        if p_fix and (t_volume.getUuid() != None) and (not t_volume.isRemovable):
            ## ここが上手くとれない
            t_ok = True
        else:
            if (not p_fix) and (t_volume.getUuid() != None) and t_volume.isRemovable:
                t_ok = True

        debug_log('one volume proc : ' + t_volume.getState())
        ## t_file = t_volume.getDirectory()
        ## debug_log('one volume proc : ' + t_file.getName())
        ## debug_log('one volume proc : ' + t_volume.getMediaStoreVolumeName())

        """
        if (t_volume.isRemovable and
            t_volume.getUuid() != None):
        # SDカードである
        """
        if t_ok:
        # 当該ボリューム
            t_request = True
            """ ##
            t_msg = t_volume.getUuid() + ' | ' + t_volume.toString()
            debug_log('volume removable : ' + t_msg)
            ## """
            debug_log('volume ok : ' + t_volume.toString())


            # ディレクトリアクセス権要求する intent 生成
            ## t_intent = t_volume.createAccessIntent(None) # None:root
            t_intent = create_open_doctree_intent(t_volume)

            # コールバッククラスインスタンス作成
            t_request_access = RequestAccessCallback_7_9(REQUEST_ACCESS_STORAGE)
            # 発行のコールバックをセット
            # スレッドの重複はクラスが見つけられない場合有り
            # https://issuehint.com/issue/kivy/python-for-android/2533
            debug_log('bind start')
            activity.bind(on_activity_result = t_request_access.on_activity_result)
            debug_log('bind end')

            # intent 発行
            debug_log('startActivityForResult')
            mActivity.startActivityForResult(t_intent, REQUEST_ACCESS_STORAGE)

            # 許可の応答を待つ
            debug_log('request_access wait start')
            while True:
                if t_request_access.result != None:
                # 結果が入った
                    if t_request_access.result:
                    # 許可
                        t_ok  = True
                        t_uri = t_request_access.uri
                    break
                else:
                    # wait
                    pass
            debug_log('request_access wait end')
            break
        else:
        # 当該ボリューム以外
            debug_log('volume skip : ' + t_volume.toString())

    if not t_request:
        raise Exception('No request access storage! (not found SD drive)')

    return t_ok, t_uri

class RequestAccessActiviry_10_11():
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            コンストラクタ
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def __init__(self, **kwargs):
        self.got_permission = False

        EXTERNAL_STORAGE_PROVIDER_AUTHORITY = "com.android.externalstorage.documents"
        ## ANDROID_DOCID = "primary:Android"
        ANDROID_DOCID = "primary:Android/data"

        self.android_uri = DocumentsContract.buildDocumentUri(
                EXTERNAL_STORAGE_PROVIDER_AUTHORITY, ANDROID_DOCID
            )
        self.android_tree_uri = DocumentsContract.buildTreeDocumentUri(
                EXTERNAL_STORAGE_PROVIDER_AUTHORITY, ANDROID_DOCID
            )
        return

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            check if got access
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def check_if_got_access(self):
        # 権限があるか探す
        t_ret = False
        t_resolver = mActivity.getContentResolver()
        for t_uri_permission in t_resolver.getPersistedUriPermissions():   # PersistedUriPermissions:
            t_uri = t_uri_permission.getUri()
            """ ##
            print('permission loop')
            print(t_uri.getPath())
            ## """
            t_ret = (t_uri.equals(self.android_tree_uri) and
                                                t_uri_permission.isReadPermission and
                                                t_uri_permission.isWritePermission
                        )
            if t_ret:
            # 見つかった
                break
        return t_ret

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            execute
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def execute(self):  ## open_directory(self):
        """ ## for debug
        t_ok = False
        if t_ok:
        ## """
        if self.check_if_got_access():
            self.on_got_permission()
        else:
        # 許可を得る
            # StorageManager    STORAGE_SERVICE
            t_storage_manager = mActivity.getSystemService(Context.STORAGE_SERVICE)
            # ボリュームを得る
            t_primary_storage_volume = t_storage_manager.getPrimaryStorageVolume()

            t_intent = t_primary_storage_volume.createOpenDocumentTreeIntent()
            t_parcelable = cast('android.os.Parcelable', self.android_uri)
            t_intent.putExtra(DocumentsContract.EXTRA_INITIAL_URI, t_parcelable)
            ## t_intent.putExtra(DocumentsContract.EXTRA_INITIAL_URI, self.android_uri)

            # コールバッククラスインスタンス作成
            t_request_access = RequestAccessCallback_10_11(REQUEST_ACCESS_STORAGE)
            # 発行のコールバックをセット
            activity.bind(on_activity_result = t_request_access.on_activity_result)
            # intent 発行
            debug_log('startActivityForResult')
            mActivity.startActivityForResult(t_intent, REQUEST_ACCESS_STORAGE)

            # 許可の応答を待つ
            debug_log('request_access wait start')
            t_ok = False
            while True:
                if t_request_access.result != None:
                # 結果が入った
                    if t_request_access.result:
                    # 許可
                        t_ok  = True
                    break
                else:
                    # wait
                    pass
            debug_log('request_access wait end')

            if not t_ok:
                debug_log("you didn't grant permission to the correct folder(1)")
                return

            if self.check_if_got_access():
                self.on_got_permission()
            else:
                debug_log("you didn't grant permission to the correct folder(2)")
            pass

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            got permission
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def on_got_permission(self):    ## on_got_access(self):
        self.got_permission = True
        debug_log("called 'on_got_permission'")
        pass

# ストレージアクセス許可を得る
# Android 10～11
def request_access_storage_10_11():
                                        # True:許可

    t_request = RequestAccessActiviry_10_11()
    t_request.execute()    ## open_directory()
    return t_request.got_permission

# androidバージョンクラス
class AndroidVersion():
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            コンストラクタ
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def __init__(self):
        ROUTIN = 'AndroidVersion : '

        if not is_android():
            raise Exception(ROUTIN + 'platform is not andoroid!')

        self.is_7_9   = False
        self.is_10_11 = False

        if VERSION.SDK_INT < ANDROID_7:
            raise Exception(ROUTIN + 'not supported! (under)')
        if VERSION.SDK_INT > ANDROID_11:
            raise Exception(ROUTIN + 'not supported! (over)')

        if VERSION.SDK_INT >= ANDROID_10:
        # Android 10 以上
            self.is_10_11 = True
        else:
        # Android 10 未満
            self.is_7_9   = True
        return

# beep (windows)
def win_beep(p_sec):    # 秒
    if is_windows():
        t_frequency = 500   # Hz ex.2000
        t_duration  = int(1000 * p_sec) # sec
        winsound.Beep(t_frequency, t_duration)

# バイブを鳴らす
def adr_vib(p_sec):     # 秒
    if not is_android():
        return
    """
    ## t_python_activity = autoclass('org.renpy.android.PythonActivity')
    t_python_activity = autoclass('org.kivy.android.PythonActivity')
    t_activity = t_python_activity.mActivity

    t_context = autoclass('android.content.Context')
    t_vibrator = t_activity.getSystemService(t_context.VIBRATOR_SERVICE)
    t_vibrator.vibrate(1000) # 1秒
    """
    t_vibrator = mActivity.getSystemService(Context.VIBRATOR_SERVICE)
    t_vibrator.vibrate(p_sec * 1000) # 秒
    return

# boo (windows : ブザー android : バイブ)
def boo(p_sec = 0.2):   # 秒
    if is_android():
        """
        from jnius import autoclass
        AudioManager = autoclass("android.media.AudioManager")
        ToneGenerator = autoclass("android.media.ToneGenerators")
        toneGenerator = ToneGenerator(AudioManager.STREAM_SYSTEM, ToneGenerator.MAX_VOLUME)
        toneGenerator.startTone(ToneGenerator.TONE_PROP_BEEP);
        """
        # バイブを鳴らす
        adr_vib(p_sec)

    if is_windows():
        """
        import winsound
        t_frequency = 500   # Hz ex.2000
        t_duration  = int(1000 * p_sec) # sec
        winsound.Beep(t_frequency, t_duration)
        """
        # beep (windows)
        win_beep(p_sec)
