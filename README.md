# Twitter Log Splitter

A Python script that splits Twitter post logs (JSON files) chronologically. It organizes large Twitter data into smaller, more manageable files.

## Features

- Splits Twitter post logs (JSON format) chronologically
- Organizes tweets by year and month
- Divides into multiple files according to file size limits
- Supports various Twitter export formats
  - Standard Twitter API format
  - Twitter archive export (.json and .js formats)
  - Custom JSON formats
- Robust encoding detection and handling
- Nested data structure support
- Flexible grouping options to minimize file count

## Usage

Run from the command line as follows:

```
python twitter-log-splitter.py <input_file> <output_directory> [max_file_size(MB)] [options]
```

### Arguments
- `<input_file>`: Path to the input JSON file (required)
- `<output_directory>`: Path to the output directory (required)
- `[max_file_size(MB)]`: Maximum size for each output file in MB (optional, default: 5MB)

### Options
- `--text-only`: Save only text data in the output files
- `--group-by=<month|year|all>`: Specify how to group tweets
  - `month`: Group by year and month (default)
  - `year`: Group by year only
  - `all`: Group all tweets together (minimizes file count)

### Examples
#### Basic usage
```bash
python twitter-log-splitter.py twitter_archive.json output_directory
```

#### Specify file size as 10MB
```bash
python twitter-log-splitter.py twitter_archive.json output_directory 10
```

#### Process Twitter export .js file
```bash
python twitter-log-splitter.py tweets.js output_directory
```

#### Save only text data
```bash
python twitter-log-splitter.py twitter_archive.json output_directory --text-only
```

#### Group by year to reduce file count
```bash
python twitter-log-splitter.py twitter_archive.json output_directory --group-by=year
```

#### Minimize file count (all tweets in as few files as possible)
```bash
python twitter-log-splitter.py twitter_archive.json output_directory --group-by=all
```

## Output
The script generates files in the specified output directory with the following format:

- When grouped by month (default): `YYYY-MM_part_N.txt`
- When grouped by year: `YYYY_part_N.txt`
- When grouped as all: `all_tweets_part_N.txt`

Where:
- YYYY-MM: Year and month (e.g., 2023-01)
- YYYY: Year (e.g., 2023)
- N: Part number

If a file with the same name already exists, a sequential number will be automatically appended (e.g., `2023-01_part_1_1.txt`).

## Supported Formats
This script automatically detects the following datetime formats:

- Twitter API format: %a %b %d %H:%M:%S +0000 %Y
- ISO format: %Y-%m-%dT%H:%M:%S.%fZ
- Standard format: %Y-%m-%d %H:%M:%S

## Requirements
- Python 3.6 or higher
- Optional dependencies:
  - `chardet`: For automatic encoding detection (recommended)
    - Install with: `pip install chardet`

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
  - Twitterアーカイブエクスポート（.jsonと.js形式）
  - カスタムJSON形式
- 堅牢なエンコーディング検出と処理
- ネストされたデータ構造のサポート
- 柔軟なグループ化オプションによるファイル数の最小化

## 使用方法

コマンドラインから以下のように実行します：

```
python twitter-log-splitter.py <入力ファイル> <出力ディレクトリ> [最大ファイルサイズ(MB)] [オプション]
```

### 引数
- `<入力ファイル>`: 入力JSONファイルのパス（必須）
- `<出力ディレクトリ>`: 出力ディレクトリのパス（必須）
- `[最大ファイルサイズ(MB)]`: 各出力ファイルの最大サイズ（MB単位、オプション、デフォルト: 5MB）

### オプション
- `--text-only`: 出力ファイルにテキストデータのみを保存する
- `--group-by=<month|year|all>`: ツイートのグループ化方法を指定
  - `month`: 年月ごとにグループ化（デフォルト）
  - `year`: 年ごとにグループ化
  - `all`: すべてのツイートを一つにグループ化（ファイル数を最小化）

### 例
#### 基本的な使用法
```bash
python twitter-log-splitter.py twitter_archive.json output_directory
```

#### ファイルサイズを10MBに指定
```bash
python twitter-log-splitter.py twitter_archive.json output_directory 10
```

#### Twitterエクスポートの.jsファイルを処理
```bash
python twitter-log-splitter.py tweets.js output_directory
```

#### テキストデータのみを保存
```bash
python twitter-log-splitter.py twitter_archive.json output_directory --text-only
```

#### 年ごとにグループ化してファイル数を減らす
```bash
python twitter-log-splitter.py twitter_archive.json output_directory --group-by=year
```

#### ファイル数を最小化（すべてのツイートをできるだけ少ないファイルに）
```bash
python twitter-log-splitter.py twitter_archive.json output_directory --group-by=all
```

## 出力
スクリプトは指定された出力ディレクトリに以下の形式でファイルを生成します：

- 月ごとのグループ化（デフォルト）: `YYYY-MM_part_N.txt`
- 年ごとのグループ化: `YYYY_part_N.txt`
- すべてをグループ化: `all_tweets_part_N.txt`

ここで：
- YYYY-MM: 年と月（例: 2023-01）
- YYYY: 年（例: 2023）
- N: パート番号

同名のファイルが既に存在する場合は、自動的に連番が付加されます（例: `2023-01_part_1_1.txt`）。

## 対応フォーマット
このスクリプトは以下の日時フォーマットを自動的に検出します：

- Twitter API形式: %a %b %d %H:%M:%S +0000 %Y
- ISO形式: %Y-%m-%dT%H:%M:%S.%fZ
- 標準形式: %Y-%m-%d %H:%M:%S

## 必要環境
- Python 3.6以上
- オプションの依存ライブラリ：
  - `chardet`: エンコーディング自動検出用（推奨）
    - インストール方法: `pip install chardet`

## ライセンス
MITライセンスの下で公開されています。詳細はLICENSEファイルを参照してください。
