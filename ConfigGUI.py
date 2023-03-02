import multiprocessing as mp
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

            # パラメータ
            self.hw_input_list = None
            self.hw_input_id = None

            # MidiからMIDI機器一覧を受け取る(ブロッキング)
            self.hw_input_list = self.model.midi_input_HW_list.get()
            logger.debug(f"recv hw_input_list(key): { self.hw_input_list.keys()}")
            logger.debug(f"recv hw_input_list(val): { self.hw_input_list.values()}")

            # ID=0の機器を初期設定とする
            self.hw_input_id = 0

            # configure window
            self.title("CHORDIS 設定")
            self.geometry(f"{400}x{300}")

            frame_1 = customtkinter.CTkFrame(master=self)
            frame_1.pack(pady=20, padx=30, fill="both", expand=True)

            # MIDI入力機器
            label_1 = customtkinter.CTkLabel(master=frame_1, justify=customtkinter.LEFT, text="MIDI Input HW:")
            label_1.pack(pady=10, padx=10)

            self.optionmenu_1 = customtkinter.CTkOptionMenu(frame_1, values=list(self.hw_input_list.keys()), command=self.callback_updateHW)
            self.optionmenu_1.pack(pady=0, padx=10)

            label_2 = customtkinter.CTkLabel(master=frame_1, justify=customtkinter.LEFT, text="Font Size:")
            label_2.pack(pady=10, padx=10)

            slider_1 = customtkinter.CTkSlider(master=frame_1, command=self.slider_callback, from_=0, to=1)
            slider_1.pack(pady=0, padx=10)
            slider_1.set(0)

        def slider_callback(self, value):
            self.model.window_size = value
            
        def callback_updateHW(self, choice):
            """
            オプションメニューのcallback。
            設定値が更新されていればMIDI機器のIDをMidiに送信する
            """
            new_hw_input_id = self.hw_input_list[choice]
            logger.debug(f"select hw_input: {str(choice)}")

            if self.hw_input_id != new_hw_input_id:
                self.hw_input_id = new_hw_input_id
                self.model.midi_input_HW_selected.put(self.hw_input_id)
                logger.debug(f"send hw_input_id: {self.hw_input_id}")


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
    model.midi_input_HW_list.put({"test InputHW":0, "YAMAHA XXXX":1})
    model.isSelectConfig = 1

    config_gui = ConfigGUI(model)
    config_gui.start()