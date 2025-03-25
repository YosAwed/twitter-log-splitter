import json
import os
import sys
from datetime import datetime

def split_twitter_log_by_time(input_file, output_dir, max_size_bytes=5*1024*1024, time_format=None):
    """
    Twitter投稿ログを時系列順に分割する関数
    
    Parameters:
    - input_file: 入力JSONファイルのパス
    - output_dir: 出力ディレクトリのパス
    - max_size_bytes: 各出力ファイルの最大サイズ（バイト）
    - time_format: 日時情報のフォーマット（Noneの場合は自動検出）
    """
    # 出力ディレクトリの作成
    os.makedirs(output_dir, exist_ok=True)
    
    # ファイルを開いて構造を確認
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Twitterログの主要な構造を特定
    tweets = []
    if isinstance(data, list):
        tweets = data  # データが直接投稿の配列である場合
    elif isinstance(data, dict):
        # 一般的なTwitterエクスポート形式を検索
        for key in ['tweet', 'tweets', 'data']:
            if key in data and isinstance(data[key], list):
                tweets = data[key]
                break
    
    if not tweets:
        raise ValueError("入力ファイル内にTwitter投稿の配列が見つかりません")
    
    # 日時のキーを特定（異なる形式に対応）
    date_keys = ['created_at', 'timestamp', 'time', 'date']
    date_key = None
    
    for key in date_keys:
        if tweets and key in tweets[0]:
            date_key = key
            break
    
    if not date_key:
        raise ValueError("投稿内に日時情報が見つかりません")
    
    # 日時形式の検出とパース
    def parse_date(date_str):
        # Twitter APIの一般的な形式
        formats = [
            '%a %b %d %H:%M:%S +0000 %Y',  # Twitter API形式
            '%Y-%m-%dT%H:%M:%S.%fZ',       # ISO形式
            '%Y-%m-%d %H:%M:%S',           # 標準形式
        ]
        
        if time_format:
            formats.insert(0, time_format)
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"日付形式を認識できません: {date_str}")
    
    # 投稿を日時でソート
    try:
        tweets.sort(key=lambda x: parse_date(x[date_key]))
    except Exception as e:
        print(f"警告: 時系列順のソートに失敗しました: {e}")
    
    # 時間単位でグループ化
    grouped_tweets = {}
    for tweet in tweets:
        try:
            dt = parse_date(tweet[date_key])
            # 年月をキーとして使用
            key = dt.strftime('%Y-%m')
            if key not in grouped_tweets:
                grouped_tweets[key] = []
            grouped_tweets[key].append(tweet)
        except Exception as e:
            print(f"警告: 日時パースエラー {tweet[date_key]}: {e}")
    
    # 各時間グループをファイルサイズ制限に従って分割
    file_count = 1
    
    for period, period_tweets in sorted(grouped_tweets.items()):
        current_batch = []
        current_size = 2  # '[]' の初期サイズ
        
        for tweet in period_tweets:
            # 投稿のサイズを計算
            tweet_json = json.dumps(tweet, ensure_ascii=False)
            tweet_size = len(tweet_json.encode('utf-8'))  # 正確なバイトサイズを取得
            
            # サイズ超過チェック
            if current_size + tweet_size + 1 > max_size_bytes and current_batch:
                # 現在のバッチを保存
                output_file = os.path.join(output_dir, f"{period}_part_{file_count}.json")
                with open(output_file, 'w', encoding='utf-8') as out:
                    json.dump(current_batch, out, ensure_ascii=False)
                print(f"{period} パート {file_count} 作成: {len(current_batch)} 投稿, {current_size/1024/1024:.2f} MB")
                file_count += 1
                current_batch = []
                current_size = 2
            
            # 投稿を追加
            current_batch.append(tweet)
            current_size += tweet_size + 1  # カンマを含むサイズ
        
        # 残りの投稿を保存
        if current_batch:
            output_file = os.path.join(output_dir, f"{period}_part_{file_count}.json")
            with open(output_file, 'w', encoding='utf-8') as out:
                json.dump(current_batch, out, ensure_ascii=False)
            print(f"{period} パート {file_count} 作成: {len(current_batch)} 投稿, {current_size/1024/1024:.2f} MB")
            file_count += 1

# 使用例
split_twitter_log_by_time("twitter_archive.json", "time_sorted_tweets")git add .