import customtkinter
from screeninfo import get_monitors

from Logger import Logger
from Model import Model
logger = Logger(__name__, Logger.DEBUG)

class UiConfigCircleOfFifths(customtkinter.CTkFrame):
    """
    設定画面のナビゲーションフレーム
    """
    def __init__(self,master,model:Model) -> None:
        super().__init__(master=master)
        self.model = model
        self.x = 0
        self.y = 0

        # 表示・非表示切り替え
        row = 0
        visible_label = customtkinter.CTkLabel(master=self, justify=customtkinter.LEFT, text="Visible")
        visible_label.grid(row=row, column=0, padx=10, pady=20)
        self.switch_visible = customtkinter.CTkSwitch(self, command=self.callback_visible, text="")
        self.switch_visible.grid(row=row, column=1, padx=10, pady=20)
        self.switch_visible.select(1)
        row += 1

        # 座標
        # 画面解像度を取得する
        max_x, max_y = getScreenInfo()

        label_coord_x = customtkinter.CTkLabel(master=self, justify=customtkinter.LEFT, text="Coordinate.X:")
        label_coord_x.grid(row=row, column=0, padx=10, pady=5)
        slider_coord_x = customtkinter.CTkSlider(master=self, command=self.callback_coordinate_x, from_=0, to=max_x-1, number_of_steps=max_x)
        slider_coord_x.grid(row=row, column=1, padx=10, pady=5)
        slider_coord_x.set(0)
        row += 1

        label_coord_y = customtkinter.CTkLabel(master=self, justify=customtkinter.LEFT, text="Coordinate.Y:")
        label_coord_y.grid(row=row, column=0, padx=10, pady=5)
        slider_coord_y = customtkinter.CTkSlider(master=self, command=self.callback_coordinate_y, from_=0, to=max_y-1, number_of_steps=max_y)
        slider_coord_y.grid(row=row, column=1, padx=10, pady=5)
        slider_coord_y.set(0)
        row += 1

        # エリアの色
        label_areacolor = customtkinter.CTkLabel(master=self, justify=customtkinter.LEFT, text="Area Color:")
        label_areacolor.grid(row=row, column=0, padx=10, pady=5)
        color_list = ["green", "red", "yellow", "blue", "cyan", "magenta", "white", "black"]
        optmenu_areacolor = customtkinter.CTkOptionMenu(self, values=color_list, command=self.callback_areacolor)
        optmenu_areacolor.grid(row=row, column=1, padx=10, pady=5)
        row += 1

        # 5度圏が透過するスピード
        label_fadingspeed = customtkinter.CTkLabel(master=self, justify=customtkinter.LEFT, text="Fading Speed:")
        label_fadingspeed.grid(row=row, column=0, padx=10, pady=5)
        slider_coord_x = customtkinter.CTkSlider(master=self, command=self.callback_fadingspeed, from_=0, to=0.02)
        slider_coord_x.grid(row=row, column=1, padx=10, pady=5)
        slider_coord_x.set(0.01)
        row += 1
        
    # コールバック
    def callback_visible(self):
        self.model.visible.put(self.switch_visible.get())

    def callback_coordinate_x(self, value):
        self.x = int(value)
        self.model.coordinate.put((self.x, self.y))

    def callback_coordinate_y(self, value):
        self.y = int(value)
        self.model.coordinate.put((self.x, self.y))

    def callback_areacolor(self, value):
        self.model.area_color.put(value)

    def callback_fadingspeed(self, value):
        self.model.fading_speed.put(value)

def getScreenInfo():
    for m in get_monitors():
        if m.is_primary:
            return m.width, m.height