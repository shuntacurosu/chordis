from queue import Empty
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
import multiprocessing as mp

from Model import Model
from Logger import Logger
logger = Logger(__name__, Logger.DEBUG)

class GUI():
    """
    GUI表示用プロセス。
    実際のGUIはインナークラス__GUIで定義。
    """
    def __init__(self, model:Model):
        self.model = model
        
    def start(self):
        """
        プロセスのエントリポイント
        """
        logger.debug("プロセスを起動しました")
        gui = self.__GUI(self.model)
        gui.after(20, gui.update)
        gui.mainloop()
        logger.debug("正常にプロセスを終了しました。")

    class __GUI(tk.Tk):
        """
        GUI本体
        """
        def __init__(self, model:Model):
            super().__init__()

            # パラメータ
            bg = "snow"
            fg = "green"
            alpha = 0.8
            x = 5
            y = 0
            font_size = 45

            self.model = model
            self.geometry(f"500x80+{x}+{y}")
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
            if self.model.isFinish:
                self.destroy()
                return

            # コード更新
            try:
                chord = self.model.chord_queue.get_nowait()
                self.label1_str.set(chord)
            except Empty:
                pass
            self.after(20, self.update)

if __name__ == "__main__":
    model = Model()
    model.chord_queue.put("G#aug7(b9)/F#")
    gui = GUI(model)
    gui.start()