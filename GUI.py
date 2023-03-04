import math
from queue import Empty
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font

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

            # 初期値
            self.init_w = 500
            self.init_h = 80
            bg = "snow"
            fg = "green"
            alpha = 0.8
            x = 0
            y = 0

            self.model = model
            self.geometry(f"{self.init_w}x{self.init_h}+{x}+{y}")
            self.config(bg=bg)
            self.attributes("-transparentcolor", bg, '-alpha', alpha, "-topmost", True)
            self.wm_overrideredirect(True)

            font = Font(family='Arial', size=self.font_size(self.init_w, self.init_h), weight='bold')
            self.label1_str = tk.StringVar(self)
            self.label1 = ttk.Label(self, textvariable=self.label1_str, font=font, foreground=fg, background=bg)  #文字ラベル設定
            self.label1.grid(row=0, column=0, sticky="nsew")

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

            # フォントサイズ更新
            try:
                font_scale = self.model.font_scale.get_nowait()
                resized_w = int(self.init_w + self.init_w*font_scale)
                resized_h = int(self.init_h + self.init_h*font_scale)
                self.geometry(f"{resized_w}x{resized_h}")
                self.label1.configure(font=("Arial", self.font_size(resized_w,resized_h), "bold"))
            except Empty:
                pass

            # フォントカラー更新
            try:
                color = self.model.font_color.get_nowait()
                self.label1.configure(foreground=color)
            except Empty:
                pass

            # フォント不透明度更新
            try:
                opacity = self.model.font_opatity.get_nowait()
                self.attributes("-alpha", opacity)
            except Empty:
                pass

            self.after(20, self.update)

        def font_size(self, w, h):
            """
            フォントサイズの計算
            """
            return int(math.sqrt(w**2+h**2) * 0.1)
        
if __name__ == "__main__":
    model = Model()
    model.chord_queue.put("G#aug7(b9)/F#")
    gui = GUI(model)
    gui.start()