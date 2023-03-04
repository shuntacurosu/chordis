import multiprocessing as mp

from Logger import Logger
logger = Logger(__name__, Logger.DEBUG)

class Model:
    def __init__(self) -> None:
        self._isFinish = mp.Value('B', 0)
        self._isSelectConfig = mp.Value('B', 0)
        self._window_size= mp.Value('f', 0)
        self.font_color= mp.Queue()
        self.font_opatity= mp.Queue()
        self.chord_queue = mp.Queue()
        self.midi_input_HW_list = mp.Queue()
        self.midi_input_HW_selected = mp.Queue()

    # getter
    @property
    def isFinish(self):
        return self._isFinish.value

    @property
    def isSelectConfig(self):
        return self._isSelectConfig.value

    @property
    def window_size(self):
        return self._window_size.value
    
    # setter
    @isFinish.setter
    def isFinish(self, isFinish):
        self._isFinish.value = isFinish

    @isSelectConfig.setter
    def isSelectConfig(self, isSelectConfig):
        self._isSelectConfig.value = isSelectConfig

    @window_size.setter
    def window_size(self, window_size):
        self._window_size.value = window_size
        
if __name__ == "__main__":
    mpmodel = Model()

