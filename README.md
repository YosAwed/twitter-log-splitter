# Twitter Log Splitter

Twitterの投稿ログ（JSON/.jsファイル）を時系列・サイズ・グループ単位で分割・整理するPythonスクリプトです。
大量のTwitterデータを扱いやすい小さなファイルに整理します。

---

## 主な機能

- Twitter投稿ログ（JSON/.js形式）を時系列順に分割
- 年月・年・全期間でのグループ化オプション
- ファイルサイズ上限ごとに自動分割（デフォルト5MB、指定可）
- テキスト抽出モード（`--text-only`）対応
  - `full_text`優先、なければ`text`フィールド
  - ネスト構造（{"tweet": {...}}形式）にも対応
  - 改行→スペース置換、連続スペース削除で整形
- 進捗表示（tqdm）、処理時間表示
- 複数エンコーディング自動判別（chardet推奨）
- 既存ファイル重複時は自動連番付与
- エンコーディングエラー時の自動リカバリ
- 顔文字・絵文字削除（オプション関数）

---

## 使い方

コマンドラインから実行してください：

```bash
python twitter-log-splitter.py <入力ファイル> <出力ディレクトリ> [最大ファイルサイズ(MB)] [オプション]
```

### 引数

- `<入力ファイル>`: TwitterエクスポートJSONまたは.jsファイル（必須）
- `<出力ディレクトリ>`: 分割ファイルの出力先ディレクトリ（必須）
- `[最大ファイルサイズ(MB)]`: 各出力ファイルの最大サイズ（MB、デフォルト5MB）

### オプション

- `--text-only`  
  ツイートのテキスト部分のみ抽出・保存（整形済み）
- `--group-by=month|year|all`  
  グループ化単位を指定  
  - `month`: 年月ごと（デフォルト）
  - `year`: 年ごと
  - `all`: 全期間をまとめて最小ファイル数に

---

## 出力ファイルの命名規則

- 月ごと: `YYYY-MM_part_N.txt`
- 年ごと: `YYYY_part_N.txt`
- 全期間: `all_tweets_part_N.txt`

同名ファイルが既に存在する場合は自動的に連番（例: `2023-01_part_1_1.txt`）を付与します。

---

## 進捗表示・処理時間

- tqdmによる進捗バー表示
- 全処理の所要時間（秒）を最後に自動表示

---

## 対応フォーマット・エンコーディング

- Twitter API形式 / アーカイブエクスポート（.json, .js）
- ネスト構造（{"tweet": {...}}形式）対応
- 日時自動判別（API/ISO/標準形式）
- chardetによるエンコーディング自動検出＋複数エンコーディング試行

---

## 必要環境

- Python 3.6以上
- tqdm（進捗バー表示）
- chardet（エンコーディング自動検出、推奨）

### インストール例

```bash
pip install tqdm chardet
```

---

## エラー処理

- エンコーディングエラー時は自動的に他方式で再試行
- ファイル書き込みエラー時は警告表示し処理継続
- 入力ファイルが空・不正な場合も明確な警告

---

## ライセンス

MITライセンス  
詳細はLICENSEファイルを参照

---

## English Summary

A Python script to split Twitter log files (.json/.js) by time and size.  
Supports flexible grouping, robust encoding detection, progress bar, and text-only extraction.  
See Japanese section above for full details.

---
