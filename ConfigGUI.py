import customtkinter

from Logger import Logger
from Model import Model
logger = Logger(__name__, Logger.DEBUG)

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class ConfigGUI():
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
        config_gui = self.__ConfigGUI(self.model)
        config_gui.protocol("WM_DELETE_WINDOW", config_gui.click_close) # ウィンドウを閉じないようにする
        config_gui.after(20, config_gui.update)                         # 遅延実行処理(キュー処理、終了判定)
        config_gui.mainloop()                                           # メインループ
        logger.debug("正常にプロセスを終了しました。")

    class __ConfigGUI(customtkinter.CTk):
        def __init__(self, model:Model):
            super().__init__()
            self.model = model

            # MidiからMIDI機器一覧を受け取る(ブロッキング)
            self.hw_input_list = self.model.midi_input_HW_list.get()
            logger.debug(f"recv hw_input_list: { self.hw_input_list}")

            # configure window
            self.title("CHORDIS 設定")
            self.geometry(f"{400}x{400}")

            frame = customtkinter.CTkFrame(master=self)
            frame.pack(pady=20, padx=30, fill="both", expand=True)

            # MIDI入力機器
            label_midi_HW = customtkinter.CTkLabel(master=frame, justify=customtkinter.LEFT, text="MIDI Input HW:")
            label_midi_HW.pack(pady=10, padx=10)

            optmenu_midi_HW = customtkinter.CTkOptionMenu(frame, values=self.hw_input_list, command=self.callback_midiHW)
            optmenu_midi_HW.pack(pady=0, padx=10)

            # フォントサイズ
            label_fontsize = customtkinter.CTkLabel(master=frame, justify=customtkinter.LEFT, text="Font Size:")
            label_fontsize.pack(pady=10, padx=10)

            slider_fontsize = customtkinter.CTkSlider(master=frame, command=self.callback_fontsize, from_=0, to=1)
            slider_fontsize.pack(pady=0, padx=10)
            slider_fontsize.set(0)

            # フォントカラー
            label_fontcolor = customtkinter.CTkLabel(master=frame, justify=customtkinter.LEFT, text="Font Color:")
            label_fontcolor.pack(pady=10, padx=10)

            color_list = ["green", "red", "yellow", "blue", "cyan", "magenta", "white", "black"]
            slider_fontcolor = customtkinter.CTkOptionMenu(frame, values=color_list, command=self.callback_fontcolor)
            slider_fontcolor.pack(pady=0, padx=10)

            # フォント不透明度
            label_fontopacity = customtkinter.CTkLabel(master=frame, justify=customtkinter.LEFT, text="Font Opacity:")
            label_fontopacity.pack(pady=10, padx=10)

            slider_fontopacity = customtkinter.CTkSlider(master=frame, command=self.callback_fontopaticy, from_=0, to=1)
            slider_fontopacity.pack(pady=0, padx=10)
            slider_fontopacity.set(0.8)

        def callback_fontsize(self, value):
            self.model.window_size = value

        def callback_fontcolor(self, value):
            self.model.font_color.put(value)

        def callback_fontopaticy(self, value):
            self.model.font_opatity.put(value)

        def callback_midiHW(self, value):
            self.model.midi_input_HW_selected.put(value)

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
            self.model.isSelectConfig=0

        def update(self):
            """
            遅延処理(ループ処理)。終了判定、設定押下判定を行う
            """
            # 終了判定
            if self.model.isFinish:
                self.destroy()
                return
            
            # 「設定」押下時
            if self.model.isSelectConfig:
                # 非表示中であれば表示する
                if (self.state() != 'normal') and (self.state() != 'iconic'):
                    self.deiconify()
                self.focus_set()

            self.after(20, self.update)

if __name__ == "__main__":
    model = Model()
    model.midi_input_HW_list.put(["test InputHW","YAMAHA XXXX"])
    model.isSelectConfig = 1

    config_gui = ConfigGUI(model)
    config_gui.start()