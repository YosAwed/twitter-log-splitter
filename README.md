# Twitter Log Splitter

A Python script that splits Twitter post logs (JSON files) chronologically. It organizes large Twitter data into smaller, more manageable files.

## Features

- Splits Twitter post logs (JSON format) chronologically
- Organizes tweets by year and month
- Divides into multiple files according to file size limits
- Supports various Twitter export formats
  - Standard Twitter API format
  - Twitter archive export
  - Custom JSON formats

## Usage

Run from the command line as follows:

```
python twitter-log-splitter.py <input_file> <output_directory> [max_file_size(MB)]
```

### Arguments
- `<input_file>`: Path to the input JSON file (required)
- `<output_directory>`: Path to the output directory (required)
- `[max_file_size(MB)]`: Maximum size for each output file in MB (optional, default: 5MB)

### Examples
#### Basic usage
```bash
python twitter-log-splitter.py twitter_archive.json output_directory
```

#### Specify file size as 10MB
```bash
python twitter-log-splitter.py twitter_archive.json output_directory 10
```

## Output
The script generates files in the specified output directory with the following format:

`YYYY-MM_part_N.json`
- YYYY-MM: Year and month (e.g., 2023-01)
- N: Part number

## Supported Formats
This script automatically detects the following datetime formats:

- Twitter API format: %a %b %d %H:%M:%S +0000 %Y
- ISO format: %Y-%m-%dT%H:%M:%S.%fZ
- Standard format: %Y-%m-%d %H:%M:%S

## Requirements
- Python 3.6 or higher
- Uses only standard library (no additional packages needed)

## License
Released under the MIT License. See the LICENSE file for details.

---

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

```
python twitter-log-splitter.py <入力ファイル> <出力ディレクトリ> [最大ファイルサイズ(MB)]
```

### 引数
- `<入力ファイル>`: 入力JSONファイルのパス（必須）
- `<出力ディレクトリ>`: 出力ディレクトリのパス（必須）
- `[最大ファイルサイズ(MB)]`: 各出力ファイルの最大サイズ（MB単位、オプション、デフォルト: 5MB）

### 例
#### 基本的な使用法
```bash
python twitter-log-splitter.py twitter_archive.json output_directory
```

#### ファイルサイズを10MBに指定
```bash
python twitter-log-splitter.py twitter_archive.json output_directory 10
```

## 出力
スクリプトは指定された出力ディレクトリに以下の形式でファイルを生成します：

`YYYY-MM_part_N.json`
- YYYY-MM: 年と月（例: 2023-01）
- N: パート番号

## 対応フォーマット
このスクリプトは以下の日時フォーマットを自動的に検出します：

- Twitter API形式: %a %b %d %H:%M:%S +0000 %Y
- ISO形式: %Y-%m-%dT%H:%M:%S.%fZ
- 標準形式: %Y-%m-%d %H:%M:%S

## 必要環境
- Python 3.6以上
- 標準ライブラリのみ使用（追加パッケージ不要）

## ライセンス
MITライセンスの下で公開されています。詳細はLICENSEファイルを参照してください。
