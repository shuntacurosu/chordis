from queue import Empty
import pygame.midi

from Model import Model
from Logger import Logger
logger = Logger(__name__, Logger.DEBUG)

class MidiInitError(Exception):
    pass

class Const:
    TRIAD_NUM = 3   # トライアドの音数
    SEVENTH_NUM = 4 # セブンスの音数
    NINTH_NUM = 5   # ナインスの音数
    NOTE_ON = 0x90  # midiステータス
    NOTE_OFF = 0x80 # midiステータス
    TONE_NUM = 12   # 12律

octave = {
    "C":    0,
    "C#":   1,
    "D":    2,
    "D#":   3,
    "E":    4,
    "F":    5,
    "F#":   6,
    "G":    7,
    "G#":   8,
    "A":    9,
    "A#":   10,
    "B":    11,
}

class Midi:
    def __init__(self, model:Model):
        self.model = model
        self.notes = []
        self.old_chord = ""
        self.chord = ""
        
        # MIDI入力デバイス一覧
        self.hw_input_list = {}

    def start(self):
        """
        プロセスのエントリポイント
        """
        logger.debug("プロセスを起動しました")
        try:
            pygame.midi.init()
            self.__start()
        except MidiInitError as ex:
            self.model.midi_input_HW_list.put([]) #ConfigGUIがget()でブロックされているため
            logger.msg_error(ex)
        except Exception as ex:    
            logger.msg_error(ex)
        finally: 
            pygame.midi.quit()
            self.model.isFinish = 1
        
    def __start(self):
        """
        実際のプロセスのエントリポイント
        """
        # 全てのmidi入力デバイスを選択
        for i in range(pygame.midi.get_count()):
            device_info = pygame.midi.get_device_info(i)
            if device_info[2]: # is InputDevice?
                self.hw_input_list[device_info[1]] = i
        
        # midi入力デバイスが存在しない場合エラー
        if len(self.hw_input_list) == 0:
            raise MidiInitError("MIDI入力機器が接続されていません。chordisを終了します。")
        
        try:
            # 先頭の入力デバイスを初期値として設定
            self.midi_input_id = list(self.hw_input_list.values())[0]
            midi_input = pygame.midi.Input(self.midi_input_id)
        except Exception as ex:
            raise MidiInitError("使用可能なMIDIデバイスが存在しません。chordisを終了します。")

        # ConfigGUIにmidi入力デバイスリストを送信
        self.model.midi_input_HW_list.put(list(self.hw_input_list.keys()))
        logger.debug(f"send hw_input_list(key): list(self.hw_input_list.keys())")

        # ループ内でコード判定、終了判定、MIDI機器設定変更を行う
        try:
            while(not self.model.isFinish):
                midi_input = self.__updateMidiInput(midi_input)
                self.__updateChord(midi_input)
                self.__putChord()
                pygame.time.wait(10)
        except KeyboardInterrupt:
                pass
        
    def stop(self):
        """
        プロセス終了時に実行する関数
        """
        self.model.isFinish = 1

    def __updateMidiInput(self, midi_input):
        """
        GUIで選択されたMIDI機器のIDを取得(ノンブロッキング)
        """
        try:
            midi_input_HW = self.model.midi_input_HW_selected.get_nowait()
            midi_input_HW_id = self.hw_input_list[midi_input_HW]
            pygame.midi.Input.close(midi_input)
            pygame.midi.quit()
            pygame.midi.init()
            midi_input = pygame.midi.Input(midi_input_HW_id)
            logger.debug(f"set input_midi_device: {midi_input_HW_id}:{midi_input_HW}")
        except Empty:
            pass

        return midi_input
    
    def __putChord(self):
        """
        コードをキューにエンキューします。
        """
        if self.old_chord != self.chord:
            self.model.chord_queue.put(self.chord)
            self.old_chord = self.chord
            logger.debug(f"Chord: {self.chord}")

    def __updateChord(self, midi_input):
        """
        キーボードから入力されたコードを返します。
        """
        self.__update_notes(midi_input)
        self.__notes_to_chord()

    def __update_notes(self, midi_input):
        """
        キーボードからMIDI信号を受け取りnotesを更新します。
        """
        # キーボードからの入力値を取得
        if midi_input.poll():
            midi_events = midi_input.read(1)
            status = midi_events[0][0][0]
            note = midi_events[0][0][1]
        else:
            return

        # 押されているキーを更新
        match status:
            case Const.NOTE_ON:
                if note not in self.notes:
                    self.notes.append(note)
                    self.notes = sorted(self.notes)
            case Const.NOTE_OFF:
                if note in self.notes:
                    self.notes.remove(note)

    def __midi_to_ansi_note(self, midi_note):
        """
        MIDI信号をANSI NOTEに変換する
        """
        ansi_note = pygame.midi.midi_to_ansi_note(midi_note%Const.TONE_NUM)[:-2]
        match ansi_note:
            case "A#": ansi_note = "Bb"
            case "C#": ansi_note = "Db"
            case "D#": ansi_note = "Eb"
            case "G#": ansi_note = "Ab"
        return ansi_note
    
    def __notes_to_chord(self):
        """
        MIDIノートナンバーをコードに変換します。
        """

        if len(self.notes) < Const.TRIAD_NUM:
            self.chord = ""
            return
        
        # 1オクターブ(1-12)に変換
        octave_notes = []  # 重複を削除した後の要素を格納する配列
        unique_set = set()  # 重複している要素を記憶するためのセット
        for note in [note%Const.TONE_NUM for note in self.notes]:
            if note not in unique_set:
                octave_notes.append(note)
                unique_set.add(note)

        # ノートからコードを探索
        new_note = None
        suffix = None
        octave_notes = sorted(octave_notes)
        for i in range(len(octave_notes)):
            diff = [octave_notes[j]-octave_notes[j-1] for j in range(1,len(octave_notes))]
            new_note=self.__midi_to_ansi_note(octave_notes[0])
            octave_notes = octave_notes[1:]+[octave_notes[0]+12]

            match diff:
                # トライアド
                case (4, 3): suffix = ""
                case (3, 4): suffix = "m"
                case (3, 3): suffix = "dim"
                case (4, 4): suffix = "aug"
                case (5, 2): suffix = "sus4"
                # # シックス
                # case (4, 3, 2): suffix = "6"
                # case (3, 4, 2): suffix = "m6"
                # セブンス
                case (4, 3, 4): suffix = "M7"
                case (4, 3, 3): suffix = "7"
                case (3, 4, 3): suffix = "m7"
                case (3, 4, 4): suffix = "m(M7)"
                case (4, 2, 4): suffix = "7b5"
                case (3, 3, 4): suffix = "m7b5"
                case (4, 4, 3): suffix = "augM7"
                case (4, 4, 2): suffix = "aug7"
                case (3, 3, 3): suffix = "dim7"
                case (2, 2, 3): suffix = "add9"
                # ナインス
                case (2, 2, 3, 4): suffix = "M9"
                case (2, 2, 3, 3): suffix = "9"
                case (2, 1, 4, 3): suffix = "m9"
                case (2, 1, 4, 4): suffix = "m(M9)"
                case (2, 2, 4, 2): suffix = "aug9"
                case (1, 3, 4, 2): suffix = "aug7(b9)"

                # 特殊
                case (3, 2, 2, 3): suffix = "m7" # Ⅱm7/Ⅴ
            if suffix != None:
                break

        # 判定有の場合コードを更新。判定無の場合空文字で更新。
        if suffix == None:
            self.chord = ""
            return

        # ルートを取得
        root = self.__midi_to_ansi_note(self.notes[0])

        # ルートとコードの音差
        diff = octave[new_note] - octave[root]

        if (suffix == "m7") and ((diff == 9) or (diff == -3)):
            # 6コード判定
            self.chord = new_note+"6"
        elif (suffix == "m7b5") and ((diff == 9) or (diff == -3)):
            # m6コード判定
            self.chord = new_note+"m6"
        elif diff == 0:
            # 基本形
            self.chord = new_note+suffix
        else:
            # 転回形
            self.chord = new_note+suffix + "/" + root

if __name__ == "__main__":
    model = Model()
    midi = Midi(model)
    model.midi_input_HW_selected.put(b"JUNO-DS")
    midi.start()
