import pygame.midi
import multiprocessing as mp

from Logger import Logger
logger = Logger(__name__, Logger.DEBUG)

class Const:
    TRIAD_NUM = 3   # トライアドの音数
    SEVENTH_NUM = 4 # セブンスの音数
    NINTH_NUM = 5   # ナインスの音数
    NOTE_ON = 0x90  # midiステータス
    NOTE_OFF = 0x80 # midiステータス
    TONE_NUM = 12   # 12律

class Midi:
    def __init__(self, chord_queue:mp.Queue, isFinish:mp.Value):
        self.chord_queue = chord_queue
        self.isFinish = isFinish
        self.notes = []
        self.old_chord = ""
        self.chord = ""
        
    def start(self):
        """
        プロセスのエントリポイント
        """
        logger.debug("プロセスを起動しました")

        # midiデバイスの初期化
        pygame.midi.init()

        # 全てのmidi入力デバイスを選択
        midi_inputs = []
        for i in range(pygame.midi.get_count()):
            if pygame.midi.get_device_info(i)[2]: # is InputDevice?
                midi_inputs.append(pygame.midi.Input(i))
        try:
            while(not self.isFinish.value):
                [self.__updateChord(midi_input) for midi_input in midi_inputs]
                self.__putChord()
                pygame.time.wait(10)
        except KeyboardInterrupt:
                pass
        pygame.midi.quit()
        logger.debug("正常にプロセスを終了しました。")
        
    def stop(self):
        """
        プロセス終了時に実行する関数
        """
        self.isFinish.value = 1
        
    def __putChord(self):
        """
        コードをキューにエンキューします。
        """
        if self.old_chord != self.chord:
            self.chord_queue.put(self.chord)
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
        new_chord = None
        new_note = None
        octave_notes = sorted(octave_notes)
        for i in range(len(octave_notes)):
            diff = [octave_notes[j]-octave_notes[j-1] for j in range(1,len(octave_notes))]
            new_note=self.__midi_to_ansi_note(octave_notes[0])
            octave_notes = octave_notes[1:]+[octave_notes[0]+12]

            match diff:
                # トライアド
                case (4, 3): new_chord = new_note+""
                case (3, 4): new_chord = new_note+"m"
                case (3, 3): new_chord = new_note+"dim"
                case (4, 4): new_chord = new_note+"aug"
                case (5, 2): new_chord = new_note+"sus4"
                # セブンス
                case (4, 3, 4): new_chord = new_note+"M7"
                case (4, 3, 3): new_chord = new_note+"7"
                case (3, 4, 3): new_chord = new_note+"m7"
                case (3, 4, 4): new_chord = new_note+"m(M7)"
                case (3, 3, 4): new_chord = new_note+"m7b5"
                case (4, 4, 3): new_chord = new_note+"augM7"
                case (4, 4, 2): new_chord = new_note+"aug7"
                case (3, 3, 3): new_chord = new_note+"dim7"
                case (2, 2, 3): new_chord = new_note+"add9"
                # ナインス
                case (2, 2, 3, 4): new_chord = new_note+"M9"
                case (2, 2, 3, 3): new_chord = new_note+"9"
                case (2, 1, 4, 3): new_chord = new_note+"m9"
                case (2, 1, 4, 4): new_chord = new_note+"m(M9)"
                case (2, 2, 4, 2): new_chord = new_note+"aug9"
                case (1, 3, 4, 2): new_chord = new_note+"aug7(b9)"
            if new_chord != None:
                break
        # 判定有の場合コードを更新。判定無の場合空文字で更新。
        if not new_chord:
            self.chord = ""
        else:
            # オンコードを追記
            root = self.__midi_to_ansi_note(self.notes[0])
            if root == new_note:
                self.chord = new_chord
            else:
                self.chord = new_chord + "/" + root

if __name__ == "__main__":
    queue = mp.Queue()
    isFinish = mp.Value('B', 0)
    midi = Midi(queue, isFinish)
    midi.start()
