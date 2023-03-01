import multiprocessing as mp

from ConfigGUI import ConfigGUI
from GUI import GUI
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

        gui = GUI(self.model)
        midi = Midi(self.model)
        config = ConfigGUI(self.model)
        self.ps = [
            mp.Process(target=gui.start),
            mp.Process(target=midi.start),
            mp.Process(target=config.start),
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
        self.model.isSelectConfig = 1
        
if __name__ == "__main__":
    Application().start()
