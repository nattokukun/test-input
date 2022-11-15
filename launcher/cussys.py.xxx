# -*- coding: utf-8 -*-
#//////////////////////////////////////////////////////////////////////////////
#            cussys Custom System
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

#------------------------------------------------------------------------------
#                   関数群
#------------------------------------------------------------------------------
# デバッグログ
def debug_log(p_msg):
    tp_msg = p_msg .replace(':', '$')
    tp_msg = tp_msg.replace('\n', ' ')
    Logger.debug('### ' + tp_msg)

debug_log('************** Logger debug start *************')

import traceback
import platform
import os

import const
#------------------------------------------------------------------------------
#                   関数群
#------------------------------------------------------------------------------
# Windowsであるか
def is_windows():
    return (platform.system() == 'Windows')

# Androidであるか
def is_android():
    tp_name = platform.system()
    ## debug_log(tp_name)
    return (tp_name == 'Linux' or tp_name == 'Android')

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

#------------------------------------------------------------------------------
#                   定数定義
#------------------------------------------------------------------------------
# Android 用
if is_android():
    ANDROID_7  = 24
    ANDROID_10 = 29
    ANDROID_11 = 30

# 要求コードは任意でユニーク
const.REQUEST_ACCESS_STORAGE = 101


#------------------------------------------------------------------------------
#                   関数群
#------------------------------------------------------------------------------

# OpenGLの調整
def adjust_opengl(p_python_ver):    # pythonバージョンNo
    """
        OpenGLが2.0以上にも関わらず、当該認識をしない場合は、
                Python 3    (A)〇 (B)×
                Python 2    (A)× (B)〇
    """
    if not is_windows():
        return

    if p_python_ver == 3:
        ## (A)
        ## if platform.system() == 'Windows':
        if is_windows():
            # OpenGL2.0 を認識しない場合
            os.environ ['KIVY_GL_BACKEND'] = 'angle_sdl2'
        return

    if p_python_ver == 2:
        ## (B)
        ## if platform.system() == 'Windows':
        if is_windows():
            # OpenGL2.0 を認識しない場合
            from kivy import Config
            Config.set('graphics', 'multisamples', '0')
        return

# 外部ストレージパス(実際は内部ストレージパス)を得る
def adrd_get_external_storage_dir():    # 外部ストレージパス
    tp_environment = autoclass('android.os.Environment')
    tp_dir = tp_environment.getExternalStorageDirectory()
    # print('******')
    tp_str = tp_dir.getAbsolutePath()
    # print(tp_str)
    # print('******')
    return tp_str

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
        tp_ok = True
        for tp_grant in p_grants:
            if tp_grant == permissions.PERMISSION_GRANTED:
            # 許可
                pass
            if tp_grant == permissions.PERMISSION_DENIED:
            # 拒否
                tp_ok = False
                break

        if not tp_ok:
        # 全て許可されない
            self.result = False
        else:
        # 全て許可
            self.result = True
        debug_log('on_request_permission_callback end')

# 複数権限を点検する
def adrd_check_permissions(p_permissions):  # 権限
                                                # True:全て
    tp_ok = True
    for tp_permission in p_permissions:
        if not check_permission(tp_permission):
            tp_ok = False
            break
    return tp_ok

# 複数権限を得る
def adrd_check_request_permissions(p_permissions):  # 権限
                                                        # True:許可
    debug_log('start check request permission')
    # 点検
    tp_ok = adrd_check_permissions(p_permissions)
    ##    tp_ok = False # 以下実行するためのテスト用
    if tp_ok:
    # 許可有
        debug_log('check permission ok')
    else:
    # 許可無
        debug_log('check permission None')

        tp_request_permission = RequestPermission()
        # 許可を得る
        debug_log('  permission start')
        request_permissions(p_permissions, tp_request_permission.callback)
        debug_log('  permission end')

        while True:
            if tp_request_permission.result != None:
                break

    debug_log('permission return')
    return True

# ファイル書き込みテスト
def test_adrd_file_write(p_dir_doc,         # 場所
                            p_file_name):   # ファイル名
                                            # エラーメッセージ '':成功
    debug_log('filetest_adrd_file_write start :' + p_file_name)
    try:
        tp_file_doc = p_dir_doc.createFile('text/plain', p_file_name)
        tp_resolver = mActivity.getContentResolver()
        tp_outstrm  = tp_resolver.openOutputStream(tp_file_doc.uri) ## tp_uri) ## tp_file_doc)
        tp_outstrm.write(bytearray(b'hoge'))
        tp_outstrm.close()
        tp_errmsg = ''
    except:
        tp_errmsg = 'test_adrd_file_write ' + '\n' + \
                    traceback.format_exc()

    debug_log('filetest_adrd_file_write end')
    return tp_errmsg

# ストレージ検証
def test_adrd_storage():
    # StorageManager    STORAGE_SERVICE
    tp_sto_mng = mActivity.getSystemService(Context.STORAGE_SERVICE)

    # tp_sto_vols = tp_sto_mng.getRecentStorageVolumes()
    tp_sto_vols = tp_sto_mng.getStorageVolumes()
    for tp_str_vol in tp_sto_vols:
        print('a1 :' + tp_str_vol.toString())
        ## getDescription(Context context)
        print('a2 :' + tp_str_vol.getDescription(mActivity))
        ## getMediaStoreVolumeName()
        ## print('a3 :' + tp_str_vol.getMediaStoreVolumeName())  # error

    tp_sto_vol = tp_sto_mng.getPrimaryStorageVolume()
    print('b :' + tp_str_vol.toString())
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
        tp_end = False
        if p_request_code == self.wait_request_code: # const.REQUEST_ACCESS_STORAGE:
        # 当該リクエスト
            if p_result_code  == Activity.RESULT_OK:
                # 許可を保存
                tp_uri = p_intent.getData()
                tp_resolver = mActivity.getContentResolver()
                tp_resolver.takePersistableUriPermission(tp_uri,
                                                         Intent.FLAG_GRANT_READ_URI_PERMISSION or
                                                         Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
                """ ##
                # ファイル書き込みテスト
                tp_errmsg = test_adrd_file_write(tp_uri, 'xx1')
                if tp_errmsg != '':
                    raise tp_errmsg

                # ファイル書き込みテスト
                tp_errmsg = test_adrd_file_write(tp_uri, 'xx2')
                if tp_errmsg != '':
                    raise tp_errmsg
                ## """
                # uri sd 保存
                self.uri = tp_uri
                debug_log('on_activity_result ok!')
                tp_result = True
            else:
                # 拒否処理
                debug_log('on_activity_result cancel!')
                tp_result = False

            tp_end = True
        else:
            debug_log('on_activity_result not request')

        if tp_end:
            # バインド解除
            debug_log('on_activity_result unbind')
            activity.unbind(on_activity_result=self.on_activity_result)

        if tp_end:
            self.result = tp_result
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
        tp_end = False
        if p_request_code == self.wait_request_code: # const.REQUEST_ACCESS_STORAGE:
        # 当該リクエスト

            # 以下のifをTrueにする
            p_result_code = Activity.RESULT_OK
            if p_result_code  == Activity.RESULT_OK:
                # 許可を保存
                tp_uri = p_intent.getData()

                tp_take_flag = (Intent.FLAG_GRANT_READ_URI_PERMISSION or
                                Intent.FLAG_GRANT_WRITE_URI_PERMISSION)

                tp_resolver = mActivity.getContentResolver()
                tp_resolver.takePersistableUriPermission(tp_uri, tp_take_flag)

                # uri sd 保存
                self.uri = tp_uri
                debug_log('on_activity_result ok!')
                tp_result = True
            else:
                # 拒否処理
                debug_log('on_activity_result cancel!')
                tp_result = False

            tp_end = True
        else:
        # 当該リクエストではない
            debug_log('on_activity_result not request')

        if tp_end:
            # バインド解除
            debug_log('on_activity_result unbind')
            activity.unbind(on_activity_result=self.on_activity_result)

        if tp_end:
            self.result = tp_result
        debug_log('on_activity_result return')


# uri から DocumentFile を得る
def get_doc_by_uri(p_uri):
                                # :DocumentFile =None:エラー
    ROUTIN = 'get_doc_by_uri : '
    # : が存在する場合を SD とする
    tp_sd_fuu = ':' in p_uri.getPath()
    """
    if tp_sd_fuu:
        debug_log('get_doc_by_uri : This is SD')
    else:
        debug_log('get_doc_by_uri : This is not SD')
    """
    if not tp_sd_fuu:
        tp_file = File(p_uri.getPath())
        tp_doc = DocumentFile.fromFile(tp_file)
    else:
        if p_uri.getScheme() == 'file':
        # SDなのに file の場合は、未対応とする
            """
            # 変換する.. 以下上手くいかない
            tp_File = File(p_uri.getPath())
            tp_context = Context.getApplicationContext()
            tp_uri = FileProvider.getUriForFile(mActivity, \
                                                tp_context.getPackageName() + ".provider", \
                                                tp_File)
            p_uri = tp_uri
            """
            tp_doc = None
            raise Exception(ROUTIN + 'this uri not supported!' + p_uri.getPath())
        else:
        # context
            ## tp_file = File(p_uri.getPath())
            tp_doc = DocumentFile.fromTreeUri(mActivity, p_uri)
    pass
    return tp_doc

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
        tp_intent = p_volume.createOpenDocumentTreeIntent()
    else:
    # Android 10 未満
        tp_intent = p_volume.createAccessIntent(None) # None:root

    return tp_intent

# SDカード uriを得る
def get_sd_uri():
                    # sd_uri ルート

    ROUTIN = 'get_sd_uri : '
    tp_storage_manager = mActivity.getSystemService(Context.STORAGE_SERVICE)

    # 全ボリュームを得る
    tp_storageVolumes = tp_storage_manager.storageVolumes

    tp_uri = None
    # 全ボリュームループ
    for tp_volume in tp_storageVolumes:
        if (tp_volume.getUuid() != None) and tp_volume.isRemovable:
            """ 7-9 NG
            tp_file = tp_volume.getDirectory()
            tp_uri = Uri.fromFile(tp_file)
            """
            android_version = AndroidVersion()
            if android_version.is_10_11:
                tp_file = tp_volume.getDirectory()
                tp_uri = Uri.fromFile(tp_file)
            else:
                """
                print('*** ' + tp_volume.getUuid())
                """
                """
                tp_file = File('/storage/' + tp_volume.getUuid() + '/')
                tp_uri = Uri.fromFile(tp_file)
                tp_doc = get_doc_by_uri(tp_uri)
                tp_uri = tp_doc.getUri()
                """
                raise Exception(ROUTIN + 'android version not supported!')
            break
        pass

    return tp_uri

# アクセス権を得る
# Android 7～9
def request_access_storage_7_9():
                                        # True:許可
                                        # SDカードuri

    p_fix = False # True:固定ストレージ False:取外ストレージ

    tp_ok  = False
    tp_uri = None

    if p_fix:
    # 固定は非対応
        raise Exception('request_access_storage : fix storage unsupported!')

    debug_log('get system service')
    # StorageManager    STORAGE_SERVICE
    tp_storage_manager = mActivity.getSystemService(Context.STORAGE_SERVICE)

    # 全ボリュームを得る
    tp_storageVolumes = tp_storage_manager.storageVolumes

    # tp_volume : android.os.storage.StorageVolume
    # https://developer.android.com/reference/android/os/storage/StorageVolume
    # https://android-googlesource-com.translate.goog/platform/frameworks/base/+/master/core/java/android/os/storage/StorageVolume.java?_x_tr_sl=en&_x_tr_tl=ja&_x_tr_hl=ja&_x_tr_pto=op,sc

    tp_request = False
    # 全ボリュームループ
    for tp_volume in tp_storageVolumes:
        tp_ok = False
        """
        if tp_volume.getUuid() != None:
        # 有効
            if p_fix and (not tp_volume.isRemovable):
                tp_ok = True
            else:
                if (not p_fix) and tp_volume.isRemovable:
                    tp_ok = True
        """
        """
        if p_fix and (not tp_volume.isRemovable):
            tp_ok = True
        else:
            if (not p_fix) and tp_volume.isRemovable:
                tp_ok = True
        """
        # 注意！固定ストレージが上手くいかない
        if p_fix and (tp_volume.getUuid() != None) and (not tp_volume.isRemovable):
            ## ここが上手くとれない
            tp_ok = True
        else:
            if (not p_fix) and (tp_volume.getUuid() != None) and tp_volume.isRemovable:
                tp_ok = True

        debug_log('one volume proc : ' + tp_volume.getState())
        ## tp_file = tp_volume.getDirectory()
        ## debug_log('one volume proc : ' + tp_file.getName())
        ## debug_log('one volume proc : ' + tp_volume.getMediaStoreVolumeName())

        """
        if (tp_volume.isRemovable and
            tp_volume.getUuid() != None):
        # SDカードである
        """
        if tp_ok:
        # 当該ボリューム
            tp_request = True
            """ ##
            tp_msg = tp_volume.getUuid() + ' | ' + tp_volume.toString()
            debug_log('volume removable : ' + tp_msg)
            ## """
            debug_log('volume ok : ' + tp_volume.toString())


            # ディレクトリアクセス権要求する intent 生成
            ## tp_intent = tp_volume.createAccessIntent(None) # None:root
            tp_intent = create_open_doctree_intent(tp_volume)

            # コールバッククラスインスタンス作成
            tp_request_access = RequestAccessCallback_7_9(const.REQUEST_ACCESS_STORAGE)
            # 発行のコールバックをセット
            # スレッドの重複はクラスが見つけられない場合有り
            # https://issuehint.com/issue/kivy/python-for-android/2533
            debug_log('bind start')
            activity.bind(on_activity_result = tp_request_access.on_activity_result)
            debug_log('bind end')

            # intent 発行
            debug_log('startActivityForResult')
            mActivity.startActivityForResult(tp_intent, const.REQUEST_ACCESS_STORAGE)

            # 許可の応答を待つ
            debug_log('request_access wait start')
            while True:
                if tp_request_access.result != None:
                # 結果が入った
                    if tp_request_access.result:
                    # 許可
                        tp_ok  = True
                        tp_uri = tp_request_access.uri
                    break
                else:
                    # wait
                    pass
            debug_log('request_access wait end')
            break
        else:
        # 当該ボリューム以外
            debug_log('volume skip : ' + tp_volume.toString())

    if not tp_request:
        raise Exception('No request access storage!')

    return tp_ok, tp_uri

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
        tp_ret = False
        tp_resolver = mActivity.getContentResolver()
        for tp_uri_permission in tp_resolver.getPersistedUriPermissions():   # PersistedUriPermissions:
            tp_uri = tp_uri_permission.getUri()
            """ ##
            print('permission loop')
            print(tp_uri.getPath())
            ## """
            tp_ret = (tp_uri.equals(self.android_tree_uri) and
                                                tp_uri_permission.isReadPermission and
                                                tp_uri_permission.isWritePermission
                        )
            if tp_ret:
            # 見つかった
                break
        return tp_ret

    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    #            execute
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    def execute(self):  ## open_directory(self):
        """ ## for debug
        tp_ok = False
        if tp_ok:
        ## """
        if self.check_if_got_access():
            self.on_got_permission()
        else:
        # 許可を得る
            # StorageManager    STORAGE_SERVICE
            tp_storage_manager = mActivity.getSystemService(Context.STORAGE_SERVICE)
            # ボリュームを得る
            tp_primary_storage_volume = tp_storage_manager.getPrimaryStorageVolume()

            tp_intent = tp_primary_storage_volume.createOpenDocumentTreeIntent()
            tp_parcelable = cast('android.os.Parcelable', self.android_uri)
            tp_intent.putExtra(DocumentsContract.EXTRA_INITIAL_URI, tp_parcelable)
            ## tp_intent.putExtra(DocumentsContract.EXTRA_INITIAL_URI, self.android_uri)

            # コールバッククラスインスタンス作成
            tp_request_access = RequestAccessCallback_10_11(const.REQUEST_ACCESS_STORAGE)
            # 発行のコールバックをセット
            activity.bind(on_activity_result = tp_request_access.on_activity_result)
            # intent 発行
            debug_log('startActivityForResult')
            mActivity.startActivityForResult(tp_intent, const.REQUEST_ACCESS_STORAGE)

            # 許可の応答を待つ
            debug_log('request_access wait start')
            tp_ok = False
            while True:
                if tp_request_access.result != None:
                # 結果が入った
                    if tp_request_access.result:
                    # 許可
                        tp_ok  = True
                    break
                else:
                    # wait
                    pass
            debug_log('request_access wait end')

            if not tp_ok:
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

# アクセス権を得る
# Android 10～11
def request_access_storage_10_11():
                                        # True:許可

    tp_request = RequestAccessActiviry_10_11()
    tp_request.execute()    ## open_directory()
    return tp_request.got_permission

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

# バイブを鳴らす
def adrd_vib(p_sec):    # 秒
    if not is_android():
        return
    """
    ## tp_python_activity = autoclass('org.renpy.android.PythonActivity')
    tp_python_activity = autoclass('org.kivy.android.PythonActivity')
    tp_activity = tp_python_activity.mActivity

    tp_context = autoclass('android.content.Context')
    tp_vibrator = tp_activity.getSystemService(tp_context.VIBRATOR_SERVICE)
    tp_vibrator.vibrate(1000) # 1秒
    """
    tp_vibrator = mActivity.getSystemService(Context.VIBRATOR_SERVICE)
    tp_vibrator.vibrate(p_sec * 1000) # 秒
    return
