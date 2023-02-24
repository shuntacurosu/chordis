import multiprocessing as mp

from GUI import GUI
from Midi import Midi
from ConfigGUI import ConfigGUI
from Logger import Logger
logger = Logger(__name__, Logger.DEBUG)

class Application:
    ps = []
    isFinish = mp.Value('B', 0)
    isSelectConfig = mp.Value('B', 0)
    chord_queue = mp.Queue()
    gui_conf_queue = mp.Queue()
    midi_conf_queue = mp.Queue()

    def start(self):
        """
        エントリポイント。スレッドを起動する。
        """
        logger.debug("プロセスを起動しました")

        

        gui = GUI(self.chord_queue, self.gui_conf_queue, self.isFinish)
        midi = Midi(self.chord_queue, self.midi_conf_queue, self.isFinish)
        config_gui = ConfigGUI(self.isFinish, self.isSelectConfig, self.gui_conf_queue, self.midi_conf_queue)
        self.ps = [
            mp.Process(target=gui.start),
            mp.Process(target=midi.start),
            mp.Process(target=config_gui.start),
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
        self.isFinish.value = 1

    def config(self):
        """
        設定画面を表示する
        """
        self.isSelectConfig.value = 1

if __name__ == "__main__":
    Application().start()
