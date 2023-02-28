# chordis
MIDIキーボードから入力された和音をディスプレイ左上に表示するアプリケーションです。

## Demo
![demo](res/demo.gif)

## 機能
- MIDIキーボードから入力された和音名をリアルタイムに表示します。
- 和音名は英語表記で表示されます。

## インストール
- [ここ](https://github.com/shuntacurosu/chordis/releases)から最新バージョンのchordis.zipをダウンロードしてください。
- ダウンロードしたzipファイルを解凍してください。
- 解凍したフォルダ内にあるchordis.batを実行するとアプリケーションが起動します。

## 使い方
- MIDIキーボードをPCに接続します。
- chordis.batを実行します。タスクトレイにアイコンが表示されます。
- MIDIキーボードで和音を弾きます。ディスプレイ左上に和音名が表示されます。
- 終了するときはタスクトレイのアイコンを右クリックし、「quit」を選択します。

## 開発環境
```
$ python --version
Python 3.10.10

$ pip install -U pip
$ pip install -r requirements.txt
```

## ライセンス
このプロジェクトはGNU General Public License v3.0のもとで公開されています。詳細は[LICENSE](https://github.com/shuntacurosu/chordis/blob/main/LICENSE)を参照してください
