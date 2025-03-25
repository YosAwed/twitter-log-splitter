# Twitter Log Splitter

Twitterの投稿ログ（JSONファイル）を時系列順に分割するPythonスクリプトです。大量のTwitterデータを扱いやすい小さなファイルに整理します。

## 機能

- Twitter投稿ログ（JSON形式）を時系列順に分割
- 年月ごとにグループ化して整理
- ファイルサイズの制限に従って複数ファイルに分割
- 様々なTwitterエクスポート形式に対応
  - 標準Twitter APIフォーマット
  - Twitterアーカイブエクスポート
  - カスタムJSON形式

## 使用方法

コマンドラインから以下のように実行します：

python twitter-log-splitter.py <入力ファイル> <出力ディレクトリ> [最大ファイルサイズ(MB)]
引数
<入力ファイル>: 入力JSONファイルのパス（必須）
<出力ディレクトリ>: 出力ディレクトリのパス（必須）
[最大ファイルサイズ(MB)]: 各出力ファイルの最大サイズ（MB単位、オプション、デフォルト: 5MB）

例
## 基本的な使用法
```bash
python twitter-log-splitter.py twitter_archive.json output_directory
```
ファイルサイズを10MBに指定
```bash
python twitter-log-splitter.py twitter_archive.json output_directory 10
```

## 出力
スクリプトは指定された出力ディレクトリに以下の形式でファイルを生成します：

YYYY-MM_part_N.json
YYYY-MM: 年と月（例: 2023-01）
N: パート番号
対応フォーマット
このスクリプトは以下の日時フォーマットを自動的に検出します：

Twitter API形式: %a %b %d %H:%M:%S +0000 %Y
ISO形式: %Y-%m-%dT%H:%M:%S.%fZ
標準形式: %Y-%m-%d %H:%M:%S

## 必要環境
Python 3.6以上
標準ライブラリのみ使用（追加パッケージ不要）

## ライセンス
MITライセンスの下で公開されています。詳細はLICENSEファイルを参照してください。
 
