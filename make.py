import os
import subprocess
import shutil

from Logger import Logger
logger = Logger(__name__, Logger.DEBUG)

"""
Python Embeddable環境を作成します。
"""
folder_root = "chordis"
folder_env = f"{folder_root}\\env"
python_version = "3.10.10"
git_url = "https://github.com/shuntacurosu/chordis.git"

is_need_tkinter = True

def make():

    # フォルダが存在しない場合
    if not os.path.exists(folder_env):
        # root,envフォルダを作成
        os.makedirs(folder_env, exist_ok=True)

        # python embeddableをインストール
        cmd = f"call powershell Invoke-WebRequest -Uri \"https://www.python.org/ftp/python/{python_version}/python-{python_version}-embed-amd64.zip\" -OutFile \"env.zip\""
        exec(cmd)

        # python embeddableを展開
        cmd = f"call powershell -command \"Expand-Archive ..\\env.zip\""
        exec(cmd, folder_root)

        # ._pthファイルを編集
        exec_edit_pth()

        # get-pipをインストール
        cmd = f"call powershell Invoke-WebRequest -Uri \"https://bootstrap.pypa.io/get-pip.py\" -OutFile \"get-pip.py\""
        exec(cmd,folder_env)

        # pipをインストール
        cmd = ".\\python.exe get-pip.py"
        exec(cmd,folder_env)

        # 直下にtkinterライブラリを展開
        if is_need_tkinter:
            exec_copy_tkinter_lib()

        # 直下にプログラムをfatch(pullは後段で行う)
        exec("git init",folder_env)
        exec(f"git remote add origin {git_url}",folder_env)
        exec("git fetch --all --prune",folder_env)

        # batをコピー
        shutil.copyfile(f"res\\execute.bat", f"{folder_root}\\{folder_root}.bat")

    # 最新のソースを持ってくる
    exec("git pull origin main",folder_env)

    # パッケージ一覧をエクスポート
    cmd = f"pip freeze > requirements.txt"
    exec(cmd)

    # パッケージをインストール
    cmd = f".\\python.exe -m pip install -r \"..\\..\\requirements.txt\""
    exec(cmd, folder_env)

    # キャッシュを削除
    if os.path.exists(f"{folder_env}\\__pycache__"):
        cmd = f"rmdir /s /q __pycache__"
        exec(cmd, folder_env)

    # .gitを削除
    if os.path.exists(f"{folder_env}\\.git"):
        cmd = f"rmdir /s .git"
        exec(cmd, folder_env)

    # zipファイル作成
    cmd = f"call powershell Compress-Archive -Path {folder_root} -DestinationPath {folder_root}.zip -Force"
    exec(cmd)


def exec_copy_tkinter_lib():
    """
    tkinterライブラリをコピーする
    """
    tkinter_path = f"{os.environ['PYENV_HOME']}versions\\{python_version}"
    shutil.copytree(f"{tkinter_path}\\tcl", f"{folder_env}\\tcl")
    shutil.copytree(f"{tkinter_path}\\Lib\\tkinter", f"{folder_env}\\tkinter")
    shutil.copyfile(f"{tkinter_path}\\DLLs\\tcl86t.dll", f"{folder_env}\\tcl86t.dll")
    shutil.copyfile(f"{tkinter_path}\\DLLs\\tk86t.dll", f"{folder_env}\\tk86t.dll")
    shutil.copyfile(f"{tkinter_path}\\DLLs\\_tkinter.pyd", f"{folder_env}\\_tkinter.pyd")

def exec_edit_pth():
    """
    python{version}._pthを編集する
    """
    # 変数 python_version から "." で区切られた部分をリストで取得する
    version_list = python_version.split(".")
    version = version_list[0] + version_list[1]

    path = f"{folder_env}\\python{version}._pth"

    # ファイルを読み込みモードで開く
    with open(path, "r") as f:
        content = f.read()

    # コメントの先頭にある # を削除する
    content = content.replace("#import", "import")

    # ファイルを書き込みモードで開き、書き込む
    with open(path, "w") as f:
        f.write(content)

def exec(cmd:str, folder_name=None, shell=True):
    """
    cmdを実行する
    """
    logger.debug(cmd)
    if folder_name == None:
        subprocess.check_call(cmd, shell=shell)
    else:
        subprocess.check_call(cmd, cwd=folder_name, shell=shell)

if __name__ == "__main__":
    try:
        make()
    except Exception as e:
        logger.alert(e)