import multiprocessing as mp

from Logger import Logger
logger = Logger(__name__, Logger.DEBUG)

class Model:
    def __init__(self) -> None:
        self._isFinish = mp.Value('B', 0)
        self.selectConfig = mp.Queue()
        self.font_scale= mp.Queue()
        self.font_color= mp.Queue()
        self.font_opatity= mp.Queue()
        self.chord_queue = mp.Queue()
        self.midi_input_HW_list = mp.Queue()
        self.midi_input_HW_selected = mp.Queue()

    # getter
    @property
    def isFinish(self):
        return self._isFinish.value
    
    # setter
    @isFinish.setter
    def isFinish(self, isFinish):
        self._isFinish.value = isFinish

if __name__ == "__main__":
    mpmodel = Model()

