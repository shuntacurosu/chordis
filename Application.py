import multiprocessing as mp

from UiCircleOfFifth import UiCircleOfFifth
from UiConfig import UiConfig
from UiChord import UiChord
from Midi import Midi
from Logger import Logger
from Model import Model
logger = Logger(__name__, Logger.DEBUG)

class Application:
    ps = []
    model = Model()

    def start(self):
        """
        エントリポイント。スレッドを起動する。
        """
        logger.debug("プロセスを起動しました")

        ui_chord = UiChord(self.model)
        midi = Midi(self.model)
        ui_config = UiConfig(self.model)
        ui_circleOfFifth = UiCircleOfFifth(self.model)
        self.ps = [
            mp.Process(target=ui_chord.start),
            mp.Process(target=midi.start),
            mp.Process(target=ui_config.start),
            mp.Process(target=ui_circleOfFifth.start),
        ]

        try:
            for p in self.ps:
                p.daemon = True
                p.start()

            for p in self.ps:
                p.join()
        except KeyboardInterrupt:
            self.stop()

        logger.debug("正常にプロセスを終了しました。")

    def stop(self):
        """
        起動しているスレッドを終了する。
        """
        self.model.isFinish = 1

    def config(self):
        """
        設定画面を開く
        """
        self.model.selectConfig.put(True)
        
if __name__ == "__main__":
    Application().start()
