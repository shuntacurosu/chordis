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
    "Cb":11, "C": 0, "C#":1,
    "Db":1,  "D": 2, "D#":3,
    "Eb":3,  "E": 4, "E#":5,
    "Fb":4,  "F": 5, "F#":6,
    "Gb":6,  "G": 7, "G#":8,
    "Ab":8,  "A": 9, "A#":10,
    "Bb":10, "B": 11,"B#":0,
}

class Midi:
    def __init__(self, model:Model):
        self.model = model
        self.notes = []
        self.old_chord = ""
        self.chord = ""
        
        # MIDI入出力先
        self.midi_input = None
        self.midi_output = None
        self.hw_input_list = {"":-1}
        self.hw_output_list = {"":-1}
        self.hw_input_id = -1
        self.hw_output_id = -1

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
            self.model.midi_output_HW_list.put([]) #ConfigGUIがget()でブロックされているため
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
        # 全てのmidiデバイスを取得
        for i in range(pygame.midi.get_count()):
            device_info = pygame.midi.get_device_info(i)
            if device_info[2] ==  0: # is OutputDevice?
                self.hw_output_list[device_info[1]] = i
            if device_info[2] ==  1: # is InputDevice?
                self.hw_input_list[device_info[1]] = i
        
        # ConfigGUIにmidi入力デバイスリストを送信
        self.model.midi_input_HW_list.put(list(self.hw_input_list.keys()))
        self.model.midi_output_HW_list.put(list(self.hw_output_list.keys()))
        logger.debug(f"send hw_input_list.keys: {list(self.hw_input_list.keys())}")
        logger.debug(f"send hw_output_list.keys: {list(self.hw_output_list.keys())}")

        # ループ内でコード判定、終了判定、MIDI機器設定変更を行う
        try:
            while(not self.model.isFinish):
                self.__updateMidiDevice()
                if self.midi_input:
                    self.__updateChord()
                    self.__putChord()
                pygame.time.wait(10)
        except KeyboardInterrupt:
                pass
        
    def stop(self):
        """
        プロセス終了時に実行する関数
        """
        self.model.isFinish = 1

    def __updateMidiDevice(self):
        """
        GUIで選択されたMIDI機器のIDを取得(ノンブロッキング)
        """
        midi_input_HW = None
        midi_output_HW = None

        # MIDI入力機器
        try:
            midi_input_HW = self.model.midi_input_HW_selected.get_nowait()
            self.hw_input_id = self.hw_input_list[midi_input_HW]            
        except Empty:
            pass

        # MIDI出力機器
        try:
            midi_output_HW = self.model.midi_output_HW_selected.get_nowait()
            self.hw_output_id = self.hw_output_list[midi_output_HW]            
        except Empty:
            pass

        if (midi_input_HW != None) or (midi_output_HW != None):
            # クローズ処理
            if self.midi_input:
                pygame.midi.Input.close(self.midi_input)
                self.midi_input = None
            if self.midi_output:
                pygame.midi.Output.close(self.midi_output)
                self.midi_output = None
            pygame.midi.quit()
            
            # 初期化処理
            pygame.midi.init()
            if self.hw_input_id > -1:
                self.midi_input = pygame.midi.Input(self.hw_input_id)
            if self.hw_output_id > -1:
                self.midi_output = pygame.midi.Output(self.hw_output_id)
                self.midi_output.set_instrument(0)

            logger.debug(f"set input_midi_device: {self.hw_input_id}:{midi_input_HW}")
            logger.debug(f"set output_midi_device: {self.hw_output_id}:{midi_output_HW}")
    
            self.notes = []
            self.old_chord = ""
            self.chord = ""

    def __putChord(self):
        """
        コードをキューにエンキューします。
        """
        if self.old_chord != self.chord:
            self.model.chord_queue.put(self.chord)
            self.model.chord_queue2.put(self.chord)
            self.old_chord = self.chord
            logger.debug(f"Chord: {self.chord}")

    def __updateChord(self):
        """
        キーボードから入力されたコードを返します。
        """
        self.__update_notes()
        self.__notes_to_chord()

    def __update_notes(self):
        """
        キーボードからMIDI信号を受け取りnotesを更新します。
        """
        # キーボードからの入力値を取得
        if self.midi_input.poll():
            midi_events = self.midi_input.read(1)
            status = midi_events[0][0][0]
            note = midi_events[0][0][1]
            velocity = midi_events[0][0][2]
        else:
            return

        # 押されているキーを更新
        match status:
            case Const.NOTE_ON:
                if note not in self.notes:
                    if self.midi_output:
                        self.midi_output.note_on(note, velocity)
                    self.notes.append(note)
                    self.notes = sorted(self.notes)
            case Const.NOTE_OFF:
                if note in self.notes:
                    if self.midi_output:
                        self.midi_output.note_off(note)
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
                case (5, 2, 3): suffix = "7sus4"
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
    model.midi_input_HW_selected.put(b"MPK mini 3")# (b"JUNO-DS") (b"MPK mini 3")
    model.midi_output_HW_selected.put(b"JUNO-DS")  # (b"JUNO-DS") (b"")
    midi.start()
