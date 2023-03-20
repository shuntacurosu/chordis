import math
from queue import Empty
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font

from Model import Model
from Logger import Logger
logger = Logger(__name__, Logger.DEBUG)

ALPHA = 0.5

INIT = 0
PRESS = 1
RELEASE = 2

class UiCircleOfFifth():
    """
    5度圏
    実際のGUIはインナークラス__UiCircleOfFifthで定義。
    """
    def __init__(self, model:Model):
        self.model = model
        
    def start(self):
        """
        プロセスのエントリポイント
        """
        logger.debug("プロセスを起動しました")
        gui = self.__UiCircleOfFifth(self.model)
        gui.after(20, gui.update)
        gui.mainloop()
        logger.debug("正常にプロセスを終了しました。")

    class __UiCircleOfFifth(tk.Tk):
        """
        GUI本体
        """
        def __init__(self, model:Model):
            super().__init__()
            self.model = model
            
            # コードに対応するcanvasのID
            self.arcID = []
            self.nowID = None
            self.state = INIT

            # ウィンドウ
            width = 600
            height = 600
            self.fadingSpeed = 0.01  # 消えるスピード
            self.bg = "white"   # 背景色
            self.fg = "green"   # 文字の色
            self.alpha = 0
            self.attributes("-transparentcolor", self.bg, '-alpha', self.alpha, "-topmost", True)
            self.wm_overrideredirect(True)

            # キャンバス
            self.canvas = tk.Canvas(self, width=width, height=height, bg=self.bg, highlightthickness=0)
            self.canvas.grid(row=0, column=0)

            # 中心座標と半径を設定
            center_x = width/2
            center_y = height/2
            radius1 = 250   # 外側の円の半径
            radius2 = 170   # 内側の大きい円の半径
            radius3 = 80    # 内側の小さい円の半径

            # 5度圏の各音名を定義
            self.noteIDs = {}
            self.maj_notes = ["C", "G", "D", "A", "E", "B", "F#", "Db", "Ab", "Eb", "Bb", "F"]
            self.min_notes = ["Am", "Em", "Bm", "F#m", "Dbm", "Abm", "Ebm", "Bbm", "Fm", "Cm", "Gm", "Dm"]

            # 外の扇
            for i in range(12):
                self.noteIDs[self.maj_notes[i]] = self.canvas.create_arc(center_x - radius1, center_y - radius1,
                                center_x + radius1, center_y + radius1,
                                start= 90 - (i + 0.5) * 30,
                                extent=30, width = 2, fill="snow")
                
            # 内の扇
            for i in range(12):
                self.noteIDs[self.min_notes[i]] = self.canvas.create_arc(center_x - radius2, center_y - radius2,
                                center_x + radius2, center_y + radius2,
                                start= 90 - (i + 0.5) * 30,
                                extent=30, width = 2, fill="snow")

            # 内側の小さい円を描画
            self.noteIDs["other"] = self.canvas.create_oval(center_x - radius3, center_y - radius3,
                            center_x + radius3, center_y + radius3,
                            outline="black",
                            fill="snow")

            for i in range(12):

                # 角度（ラジアン）を計算
                angle = math.pi/2 + i * math.pi / 6

                # 外の音名のテキストを描画
                offset = 17
                x1 = center_x - (radius1-offset) * math.cos(angle - math.pi / 12)
                y1 = center_y - (radius1-offset) * math.sin(angle - math.pi / 12)
                x2 = center_x - (radius1-offset) * math.cos(angle + math.pi / 12)
                y2 = center_y - (radius1-offset) * math.sin(angle + math.pi / 12)
                self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2,
                                text=self.maj_notes[i],
                                font=("Arial",24),
                                fill="black")

                # 内の音名のテキストを描画
                offset = 30
                x1 = center_x - (radius2-offset) * math.cos(angle - math.pi / 12)
                y1 = center_y - (radius2-offset) * math.sin(angle - math.pi / 12)
                x2 = center_x - (radius2-offset) * math.cos(angle + math.pi / 12)
                y2 = center_y - (radius2-offset) * math.sin(angle + math.pi / 12)
                self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2,
                                text=self.min_notes[i],
                                font=("Arial",22),
                                fill="black")

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

            # 表示・非表示を更新
            try:
                visible = self.model.visible.get_nowait()
                if visible:
                    self.deiconify()
                else:
                    self.withdraw()
            except Empty:
                pass

            # 透過するスピードを更新
            try:
                self.fadingSpeed = self.model.fading_speed.get_nowait()
            except Empty:
                pass

            # エリアの色を更新
            try:
                self.fg = self.model.area_color.get_nowait()
                if self.nowID != None:
                    self.canvas.itemconfig(self.nowID,  fill=self.fg) # arcのfill属性を変更
            except Empty:
                pass

            # 座標を更新
            try:
                (x, y) = self.model.coordinate.get_nowait()
                w = self.winfo_width()
                h = self.winfo_height()
                self.geometry(f"{w}x{h}+{x}+{y}")
            except Empty:
                pass
        
            # 5度圏更新
            chord = None
            try:
                chord = self.model.chord_queue2.get_nowait()
            except Empty:
                pass
            self.updateCircleOfFifth(chord)

            self.after(20, self.update)
        
        def updateCircleOfFifth(self, chord):
            if self.state == INIT: # キーは押されていない
                if (chord != None) and (chord != ""):
                    # キーが押された
                    self.state = PRESS

                    # 不透明度を更新
                    self.update_alpha(init=True)
                    
                    # 色を付ける
                    parsedChord = self.getParsedChord(chord)
                    self.nowID = self.noteIDs[parsedChord]
                    self.canvas.itemconfig(self.nowID,  fill=self.fg) # arcのfill属性を変更

            elif self.state == PRESS: # キーを押している
                if (chord == None):
                    # 押されたままなので何もしない
                    return
                if (chord == ""):
                    # キーが離された
                    self.state = RELEASE
                    self.update_alpha()
            
            elif self.state == RELEASE: # キーを離している最中
                if (chord != None) and (chord != ""):
                    # キーが押された
                    self.state = PRESS

                    # 直前の色を削除
                    self.canvas.itemconfig(self.nowID,  fill="snow") # arcのfill属性を変更

                    # 不透明度を更新
                    self.update_alpha(init=True)
                    
                    # 色を付ける
                    parsedChord = self.getParsedChord(chord)
                    self.nowID = self.noteIDs[parsedChord]
                    self.canvas.itemconfig(self.nowID,  fill=self.fg) # arcのfill属性を変更
                
                if (chord == None):
                    # キーを離したまま
                    self.update_alpha()
                
                # 色を消してIDをクリア
                if not self.alpha:
                    self.canvas.itemconfig(self.nowID,  fill="snow") # arcのfill属性を変更
                    self.nowID = None
                    self.state = INIT

        def getParsedChord(self, chord):
            # major,minor以外 
            other_notes = ["aug", "dim", "add", "sus", "b5"]
            if any([x in chord for x in other_notes]):
                return "other"

            # minor
            idx = [chord.startswith(x) for x in self.min_notes]
            if any(idx):
                return self.min_notes[idx.index(True)]
            
            # major 記号あり
            maj_notes_symbol = [x for x in self.maj_notes if len(x) >= 2]
            idx = [chord.startswith(x) for x in maj_notes_symbol]
            if any(idx):
                return maj_notes_symbol[idx.index(True)]
            
            # major 記号なし
            maj_notes_no_symbol = [x for x in self.maj_notes if len(x) == 1]
            idx = [chord.startswith(x) for x in maj_notes_no_symbol]
            if any(idx):
                return maj_notes_no_symbol[idx.index(True)]

        def update_alpha(self,init=False):
            if init:
                self.alpha = ALPHA
                self.attributes('-alpha', self.alpha)
            elif self.alpha > 0.0:
                self.alpha = max(self.alpha-self.fadingSpeed, 0)
                self.attributes('-alpha', self.alpha)
            return
