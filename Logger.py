import logging
from tkinter import messagebox

mapping = {
    "TRACE":    "TRACE",
    "DEBUG":    "\x1b[0;36mDEBUG\x1b[0m",
    "INFO":     "\x1b[0;32mINFO\x1b[0m",
    "WARNING": "\x1b[0;33mWARNING\x1b[0m",
    "ERROR":    "\x1b[0;31mERROR\x1b[0m",
    "CRITICAL": "\x1b[0;37;41mALERT\x1b[0m",
}

class ColorfulHandler(logging.StreamHandler):
    def emit(self, record: logging.LogRecord) -> None:
        record.levelname = mapping[record.levelname]
        super().emit(record)

class Logger:
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    ALERT = logging.CRITICAL
    
    def __init__(self, name, loglevel=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(loglevel)

        # loggerのフォーマット、出力先ファイルを定義
        formatter = logging.Formatter('%(levelname)s\t[%(name)s] %(message)s')
        
        # コンソールに出力するためのStreamHandlerを設定
        stream_handler = ColorfulHandler()
        stream_handler.setFormatter(formatter)

        # ハンドラを追加
        self.logger.addHandler(stream_handler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def alert(self, msg):
        self.logger.critical(msg)

    @staticmethod
    def msg_error(msg):
        messagebox.showerror("Error", msg)

    @staticmethod
    def msg_warning(msg):
        messagebox.showwarning("Warning", msg)

    @staticmethod
    def msg_info(msg):
        messagebox.showinfo("Info", msg)

if __name__ == "__main__":
    logger = Logger(__name__, logging.DEBUG)
    logger.debug("debug")
    logger.info("info")
    logger.warning("warning")
    logger.error("error")
    logger.alert("alert")
    Logger.msg_info("test1")
    Logger.msg_warning("test2")
    Logger.msg_error("test3")