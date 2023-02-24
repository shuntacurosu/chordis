from queue import Empty
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
import multiprocessing as mp

from Logger import Logger
logger = Logger(__name__, Logger.DEBUG)

class GUI():
    """
    GUI表示用プロセス。
    実際のGUIはインナークラス__GUIで定義。
    """
    def __init__(self, chord_queue: mp.Queue, conf_queue:mp.Queue, isFinish:mp.Value):
        self.chord_queue = chord_queue
        self.conf_queue = conf_queue
        self.isFinish = isFinish

    def start(self):
        """
        プロセスのエントリポイント
        """
        logger.debug("プロセスを起動しました")
        gui = self.__GUI(self.chord_queue, self.conf_queue, self.isFinish)
        gui.after(20, gui.update)
        gui.mainloop()
        logger.debug("正常にプロセスを終了しました。")

    class __GUI(tk.Tk):
        """
        GUI本体
        """
        def __init__(self, chord_queue:mp.Queue, conf_queue:mp.Queue, isFinish:mp.Value):
            super().__init__()

            # パラメータ
            bg = "snow"
            fg = "green"
            alpha = 0.8
            x = 5
            y = 0
            font_size = 45

            self.chord_queue = chord_queue
            self.isFinish = isFinish
            self.conf_queue = conf_queue
            self.geometry(f"350x80+{x}+{y}")
            self.config(bg="snow")
            self.attributes("-transparentcolor", "snow", '-alpha', alpha, "-topmost", True)
            self.wm_overrideredirect(True)

            font1 = Font(family='Arial', size=font_size, weight='bold')
            self.label1_str = tk.StringVar(self)
            self.label1 = ttk.Label(self, textvariable=self.label1_str, font=font1, foreground=fg, background=bg)  #文字ラベル設定
            self.label1.pack(side="left")

        def mainloop(self, n: int = 0):
            try:
                super().mainloop(n)
            except KeyboardInterrupt:
                self.destroy()
        
        def update(self):
            # 終了判定
            if self.isFinish.value:
                self.destroy()
                return

            # パラメータ更新
            self.__updateConfig()

            # コード更新
            try:
                chord = self.chord_queue.get_nowait()
                self.label1_str.set(chord)
            except Empty:
                pass
            self.after(20, self.update)

        def __updateConfig(self):
            """
            パラメータを更新します。
            """
            pass

if __name__ == "__main__":
    import multiprocessing as mp
    queue = mp.Queue()
    isFinish = mp.Value('B', 0)
    queue.put("G#sus4/C#")
    gui = GUI(queue, isFinish)
    gui.start()