from pystray import Icon , Menu, MenuItem
from PIL import Image

from Application import Application

from Logger import Logger
logger = Logger(__name__, Logger.DEBUG)

global icon # タスクトレイ
global app  # アプリ

def setup(icon):
    icon.visible = True
    app.start()
    quit_app()

def main():
    global icon
    title = "CHORDIS"
    image = Image.open("res\\favicon.ico")
    menu = Menu(MenuItem('閉じる', quit_app))
    icon = Icon(name=title, icon=image, title=title, menu=menu)

    global app
    app = Application()

    icon.run(setup=setup)
    logger.debug("正常にプロセスを終了しました。")

def quit_app():
    app.stop()
    icon.stop()

if __name__ == "__main__":
    main()