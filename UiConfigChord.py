import customtkinter

from Logger import Logger
from Model import Model
logger = Logger(__name__, Logger.DEBUG)

class UiConfigChord(customtkinter.CTkFrame):
    """
    設定画面のナビゲーションフレーム
    """
    def __init__(self,master,model:Model) -> None:
        super().__init__(master=master)
        self.model = model

        # MidiからMIDI機器一覧を受け取る(ブロッキング)
        self.hw_input_list = self.model.midi_input_HW_list.get()
        logger.debug(f"recv hw_input_list: { self.hw_input_list}")

        # MIDI入力機器
        label_midi_HW = customtkinter.CTkLabel(master=self, justify=customtkinter.LEFT, text="MIDI Input HW:")
        label_midi_HW.pack(pady=10, padx=10)

        optmenu_midi_HW = customtkinter.CTkOptionMenu(self, values=self.hw_input_list, command=self.callback_midiHW)
        optmenu_midi_HW.pack(pady=0, padx=10)

        # フォントスケール(便宜上フォントサイズと表記)
        label_fontsize = customtkinter.CTkLabel(master=self, justify=customtkinter.LEFT, text="Font Size:")
        label_fontsize.pack(pady=10, padx=10)

        slider_fontsize = customtkinter.CTkSlider(master=self, command=self.callback_fontscale, from_=0, to=1)
        slider_fontsize.pack(pady=0, padx=10)
        slider_fontsize.set(0)

        # フォントカラー
        label_fontcolor = customtkinter.CTkLabel(master=self, justify=customtkinter.LEFT, text="Font Color:")
        label_fontcolor.pack(pady=10, padx=10)

        color_list = ["green", "red", "yellow", "blue", "cyan", "magenta", "white", "black"]
        slider_fontcolor = customtkinter.CTkOptionMenu(self, values=color_list, command=self.callback_fontcolor)
        slider_fontcolor.pack(pady=0, padx=10)

        # フォント不透明度
        label_fontopacity = customtkinter.CTkLabel(master=self, justify=customtkinter.LEFT, text="Font Opacity:")
        label_fontopacity.pack(pady=10, padx=10)

        slider_fontopacity = customtkinter.CTkSlider(master=self, command=self.callback_fontopaticy, from_=0, to=1)
        slider_fontopacity.pack(pady=0, padx=10)
        slider_fontopacity.set(0.8)

    # コールバック
    def callback_fontscale(self, value):
        self.model.font_scale.put(value)

    def callback_fontcolor(self, value):
        self.model.font_color.put(value)

    def callback_fontopaticy(self, value):
        self.model.font_opacity.put(value)

    def callback_midiHW(self, value):
        self.model.midi_input_HW_selected.put(value)
