from queue import Empty
import customtkinter
from PIL import Image

from UiConfigChord import UiConfigChord
from UiConfigCircleOfFifths import UiConfigCircleOfFifths
from Model import Model
from Logger import Logger
logger = Logger(__name__, Logger.DEBUG)

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class UiConfig():
    """
    設定画面表示用プロセス。
    実際の設定画面はインナークラス__ConfigGUIで定義。
    """
    def __init__(self, model):
        self.model = model

    def start(self):
        """
        プロセスのエントリポイント
        """
        logger.debug("プロセスを起動しました")
        config_gui = self.__UiConfig(self.model)
        config_gui.protocol("WM_DELETE_WINDOW", config_gui.click_close) # ウィンドウを閉じないようにする
        config_gui.after(20, config_gui.update)                         # 遅延実行処理(キュー処理、終了判定)
        config_gui.mainloop()                                           # メインループ
        logger.debug("正常にプロセスを終了しました。")

    class __UiConfig(customtkinter.CTk):
        def __init__(self, model:Model):
            """
            コンストラクタ。
            フレームを配置する。
            """
            super().__init__()
            self.model = model

            # configure window
            self.title("Chordis 設定")
            self.geometry(f"{600}x{400}")

            # アイコン
            self.iconbitmap("res\\favicon.ico")
            
            # グリッドレイアウト 1x2(ナビゲーション(左)、設定(右))
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)

            # ナビゲーションフレーム
            self.generateNavigationFrame()
            
            # コードのフレーム
            self.chord_frame = UiConfigChord(self, self.model)

            # 5度圏のフレーム
            self.circleOfFifths_frame = UiConfigCircleOfFifths(self, self.model)

            # デフォルトのフレームを選択する
            self.select_frame_by_name("chord")

        def select_frame_by_name(self, name):
            """
            ボタンに応じて表示するフレームを変更する
            """
            # ボタンの色を変更する
            self.chord_button.configure(fg_color=("gray75", "gray25") if name == "chord" else "transparent")
            self.circleOfFifths_button.configure(fg_color=("gray75", "gray25") if name == "circleOfFifths" else "transparent")

            # 選択されたフレームを表示する
            if name == "chord":
                self.chord_frame.grid(row=0, column=1, sticky="nsew")
            else:
                self.chord_frame.grid_forget()
            if name == "circleOfFifths":
                self.circleOfFifths_frame.grid(row=0, column=1, sticky="nsew")
            else:
                self.circleOfFifths_frame.grid_forget()

        def generateNavigationFrame(self):
            """
            ナビゲーションフレーム。
            """
            logo_image = customtkinter.CTkImage(Image.open("res\\icon.png"), size=(26, 26))
            self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
            self.navigation_frame.grid(row=0, column=0, sticky="nsew")
            self.navigation_frame.grid_rowconfigure(3, weight=1)
            
            # アイコン
            navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  Chordis", image=logo_image,
                                                            compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
            navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

            # コード
            self.chord_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Chord",
                                                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                command=(self.chord_button_event))
            self.chord_button.grid(row=1, column=0, sticky="ew")

            # 5度圏
            self.circleOfFifths_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Circle Of Fifths",
                                                    fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                    command=self.circleOfFifths_button_event)
            self.circleOfFifths_button.grid(row=2, column=0, sticky="ew")

        def chord_button_event(self):
            """
            コードボタンのコールバック。
            """
            self.select_frame_by_name("chord")

        def circleOfFifths_button_event(self):
            """
            5度圏ボタンのコールバック。
            """
            self.select_frame_by_name("circleOfFifths")

        def mainloop(self, n: int = 0):
            """
            メインループ
            """
            try:
                super().mainloop(n)
            except KeyboardInterrupt:
                self.destroy()

        def click_close(self):
            """
            閉じるボタン押下時の処理。画面を非表示にする。
            """
            logger.debug("閉じるボタンが押されました")
            self.withdraw()

        def update(self):
            """
            遅延処理(ループ処理)。終了判定、設定押下判定を行う
            """
            # 終了判定
            if self.model.isFinish:
                self.destroy()
                return
            
            try:
                # 「設定」押下時 
                if self.model.selectConfig.get_nowait():
                    # 非表示中であれば表示する
                    if (self.state() != 'normal') and (self.state() != 'iconic'):
                        self.deiconify()
                    self.attributes("-topmost", True)
                    self.attributes("-topmost", False)
            except Empty:
                    pass

            self.after(20, self.update)

if __name__ == "__main__":
    model = Model()
    model.midi_input_HW_list.put(["test InputHW","YAMAHA XXXX"])
    model.midi_output_HW_list.put(["", "test OutputHW", "Yamaha xxx"])
    model.selectConfig.put(True)

    config_gui = UiConfig(model)
    config_gui.start()