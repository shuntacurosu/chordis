import os
import subprocess
import shutil

from Logger import Logger
logger = Logger(__name__, Logger.DEBUG)

"""
Python Embeddable環境を作成します。
"""
folder_name = "chordis"
python_version = "3.10.10"
git_url = "https://github.com/shuntacurosu/chordis.git"
is_need_tkinter = True

def make():
    # フォルダが存在しない場合、
    if not os.path.exists(folder_name):
        # python embeddableをインストール
        cmd = f"call powershell Invoke-WebRequest -Uri \"https://www.python.org/ftp/python/{python_version}/python-{python_version}-embed-amd64.zip\" -OutFile \"{folder_name}.zip\""
        exec(cmd)

        # python embeddableを展開
        cmd = f"call powershell -command \"Expand-Archive {folder_name}.zip\""
        exec(cmd)

        # ._pthファイルを編集
        exec_edit_pth()

        # get-pipをインストール
        cmd = f"call powershell Invoke-WebRequest -Uri \"https://bootstrap.pypa.io/get-pip.py\" -OutFile \"get-pip.py\""
        exec(cmd,folder_name)

        # pipをインストール
        cmd = ".\\python.exe get-pip.py"
        exec(cmd,folder_name)

        # 直下にtkinterライブラリを展開
        if is_need_tkinter:
            exec_copy_tkinter_lib()

        # 直下にプログラムを展開
        exec("git init",folder_name)
        exec(f"git remote add origin {git_url}",folder_name)
        exec("git fetch --all --prune",folder_name)
        exec("git pull origin main",folder_name)

        # batをコピー
        shutil.copyfile(f"res\\execute.bat", f"{folder_name}\\{folder_name}.bat")

    # パッケージ一覧をエクスポート
    cmd = f"pip freeze > requirements.txt"
    exec(cmd)

    # パッケージをインストール
    cmd = f".\\python.exe -m pip install -r ..\\requirements.txt"
    exec(cmd, folder_name)

def exec_copy_tkinter_lib():
    """
    tkinterライブラリをコピーする
    """
    tkinter_path = f"{os.environ['PYENV_HOME']}versions\\{python_version}"
    shutil.copytree(f"{tkinter_path}\\tcl", f"{folder_name}\\tcl")
    shutil.copytree(f"{tkinter_path}\\Lib\\tkinter", f"{folder_name}\\tkinter")
    shutil.copyfile(f"{tkinter_path}\\DLLs\\tcl86t.dll", f"{folder_name}\\tcl86t.dll")
    shutil.copyfile(f"{tkinter_path}\\DLLs\\tk86t.dll", f"{folder_name}\\tk86t.dll")
    shutil.copyfile(f"{tkinter_path}\\DLLs\\_tkinter.pyd", f"{folder_name}\\_tkinter.pyd")

def exec_edit_pth():
    """
    python{version}._pthを編集する
    """
    # 変数 python_version から "." で区切られた部分をリストで取得する
    version_list = python_version.split(".")
    version = version_list[0] + version_list[1]

    path = f"{folder_name}\\python{version}._pth"

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