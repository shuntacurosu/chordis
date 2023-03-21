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
    
        # MidiからMIDI入力機器一覧を受け取る(ブロッキング)
        self.hw_input_list = self.model.midi_input_HW_list.get()
        logger.debug(f"recv hw_input_list: { self.hw_input_list}")

        # MidiからMIDI出力機器一覧を受け取る(ブロッキング)
        self.hw_output_list = self.model.midi_output_HW_list.get()
        logger.debug(f"recv hw_output_list: { self.hw_output_list}")

        # MIDI入力機器
        row = 0
        label_midi_HW_label = customtkinter.CTkLabel(master=self, justify=customtkinter.LEFT, text="MIDI Input Device:")
        label_midi_HW_label.grid(row=row, column=0, padx=10, pady=20)
        optmenu_midi_HW = customtkinter.CTkOptionMenu(self, values=self.hw_input_list, command=self.callback_input_device)
        optmenu_midi_HW.grid(row=row, column=1, padx=10, pady=20)
        row += 1

        # フォントスケール(便宜上フォントサイズと表記)
        label_fontsize = customtkinter.CTkLabel(master=self, justify=customtkinter.LEFT, text="Font Size:")
        label_fontsize.grid(row=row, column=0, padx=10, pady=5)
        slider_fontsize = customtkinter.CTkSlider(master=self, command=self.callback_fontscale, from_=0, to=1)
        slider_fontsize.grid(row=row, column=1, padx=10, pady=5)
        slider_fontsize.set(0)
        row += 1

        # フォントカラー
        label_fontcolor = customtkinter.CTkLabel(master=self, justify=customtkinter.LEFT, text="Font Color:")
        label_fontcolor.grid(row=row, column=0, padx=10, pady=5)
        color_list = ["green", "red", "yellow", "blue", "cyan", "magenta", "white", "black"]
        slider_fontcolor = customtkinter.CTkOptionMenu(self, values=color_list, command=self.callback_fontcolor)
        slider_fontcolor.grid(row=row, column=1, padx=10, pady=5)
        row += 1

        # フォント不透明度
        label_fontopacity = customtkinter.CTkLabel(master=self, justify=customtkinter.LEFT, text="Font Opacity:")
        label_fontopacity.grid(row=row, column=0, padx=10, pady=5)
        slider_fontopacity = customtkinter.CTkSlider(master=self, command=self.callback_fontopaticy, from_=0, to=1)
        slider_fontopacity.grid(row=row, column=1, padx=10, pady=5)
        slider_fontopacity.set(0.8)
        row += 1

        # MIDI出力機器
        label_midi_HW_label = customtkinter.CTkLabel(master=self, justify=customtkinter.LEFT, text="MIDI Output Device:")
        label_midi_HW_label.grid(row=row, column=0, padx=10, pady=5)
        optmenu_midi_HW = customtkinter.CTkOptionMenu(self, values=self.hw_output_list, command=self.callback_output_device)
        optmenu_midi_HW.grid(row=row, column=1, padx=10, pady=5)
        row += 1

    # コールバック
    def callback_fontscale(self, value):
        self.model.font_scale.put(value)

    def callback_fontcolor(self, value):
        self.model.font_color.put(value)

    def callback_fontopaticy(self, value):
        self.model.font_opacity.put(value)

    def callback_input_device(self, value):
        self.model.midi_input_HW_selected.put(value)

    def callback_output_device(self, value):
        self.model.midi_output_HW_selected.put(value)