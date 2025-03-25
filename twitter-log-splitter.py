import json
import os
import sys
from datetime import datetime
import time

def split_twitter_log_by_time(input_file, output_dir, max_size_bytes=5*1024*1024, time_format=None):
    """
    Twitter投稿ログを時系列順に分割する関数
    
    Parameters:
    - input_file: 入力JSONファイルのパス
    - output_dir: 出力ディレクトリのパス
    - max_size_bytes: 各出力ファイルの最大サイズ（バイト）
    - time_format: 日時情報のフォーマット（Noneの場合は自動検出）
    """
    # 開始時間を記録
    start_time = time.time()
    
    # 出力ディレクトリの作成
    os.makedirs(output_dir, exist_ok=True)
    
    # ファイルを開いて構造を確認
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                print(f"ファイル読み込み完了: {os.path.getsize(input_file)/1024/1024:.2f} MB")
            except json.JSONDecodeError as e:
                print(f"JSONデコードエラー: {e}")
                # 別のエンコーディングを試みる
                try:
                    with open(input_file, 'r', encoding='utf-8-sig') as f2:
                        data = json.load(f2)
                        print("UTF-8 with BOMエンコーディングで読み込み成功")
                except Exception:
                    try:
                        with open(input_file, 'r', encoding='cp932') as f3:
                            data = json.load(f3)
                            print("CP932エンコーディングで読み込み成功")
                    except Exception as e2:
                        raise ValueError(f"ファイルを読み込めませんでした。エンコーディングエラー: {e2}")
    except FileNotFoundError:
        raise FileNotFoundError(f"ファイルが見つかりません: {input_file}")
    except PermissionError:
        raise PermissionError(f"ファイルを開く権限がありません: {input_file}")
    
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
    
    # 空のツイートリストの処理
    if len(tweets) == 0:
        print("警告: ツイートリストが空です。処理するデータがありません。")
        return 0
    
    print(f"処理対象ツイート数: {len(tweets)}")
    
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
    print("ツイートを時系列順にソート中...")
    try:
        tweets.sort(key=lambda x: parse_date(x[date_key]))
        print("ソート完了")
    except Exception as e:
        print(f"警告: 時系列順のソートに失敗しました: {e}")
    
    # 時間単位でグループ化
    print("ツイートを年月ごとにグループ化中...")
    grouped_tweets = {}
    for i, tweet in enumerate(tweets):
        # 進捗表示（10%ごと）
        if i % max(1, len(tweets) // 10) == 0:
            print(f"進捗: {i}/{len(tweets)} ツイート処理中... ({i/len(tweets)*100:.1f}%)")
            
        try:
            dt = parse_date(tweet[date_key])
            # 年月をキーとして使用
            key = dt.strftime('%Y-%m')
            if key not in grouped_tweets:
                grouped_tweets[key] = []
            grouped_tweets[key].append(tweet)
        except Exception as e:
            print(f"警告: 日時パースエラー {tweet[date_key]}: {e}")
    
    print(f"グループ化完了: {len(grouped_tweets)} 期間に分類")
    
    # 各時間グループをファイルサイズ制限に従って分割
    file_count = 1
    total_processed = 0
    
    print("ファイル分割処理を開始...")
    for period, period_tweets in sorted(grouped_tweets.items()):
        print(f"期間 {period} の処理中... ({len(period_tweets)} ツイート)")
        current_batch = []
        current_size = 2  # '[]' の初期サイズ
        
        # 最適化: バッチ全体のJSONサイズを一度に計算
        for i, tweet in enumerate(period_tweets):
            # 投稿のサイズを計算（メモリ効率のため文字列に変換せずにサイズを推定）
            # 完全な精度は必要ないため、オブジェクトの大きさを推定
            tweet_size = sys.getsizeof(str(tweet)) * 1.1  # 10%のバッファを追加
            
            # サイズ超過チェック
            if current_size + tweet_size + 1 > max_size_bytes and current_batch:
                # 現在のバッチを保存
                output_file = os.path.join(output_dir, f"{period}_part_{file_count}.json")
                with open(output_file, 'w', encoding='utf-8') as out:
                    json.dump(current_batch, out, ensure_ascii=False, indent=None)
                
                actual_size = os.path.getsize(output_file)
                print(f"{period} パート {file_count} 作成: {len(current_batch)} 投稿, {actual_size/1024/1024:.2f} MB")
                
                total_processed += len(current_batch)
                current_batch = []
                current_size = 2
                file_count += 1
            
            # 投稿を追加
            if current_batch:
                current_size += 1  # カンマのサイズ
            current_batch.append(tweet)
            current_size += tweet_size
        
        # 残りの投稿を保存
        if current_batch:
            output_file = os.path.join(output_dir, f"{period}_part_{file_count}.json")
            with open(output_file, 'w', encoding='utf-8') as out:
                json.dump(current_batch, out, ensure_ascii=False, indent=None)
            
            actual_size = os.path.getsize(output_file)
            print(f"{period} パート {file_count} 作成: {len(current_batch)} 投稿, {actual_size/1024/1024:.2f} MB")
            
            total_processed += len(current_batch)
            file_count += 1
    
    # 処理時間を計算
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"処理完了: {len(tweets)} ツイートを処理しました (処理時間: {elapsed_time:.2f}秒)")
    return file_count - 1

def main():
    if len(sys.argv) < 3:
        print(f"使用方法: {sys.argv[0]} <入力ファイル> <出力ディレクトリ> [最大ファイルサイズ(MB)]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    max_size_mb = 5  # デフォルト5MB
    if len(sys.argv) > 3:
        try:
            max_size_mb = float(sys.argv[3])
        except ValueError:
            print(f"警告: 無効なサイズ指定です。デフォルトの {max_size_mb}MB を使用します。")
    
    max_size_bytes = int(max_size_mb * 1024 * 1024)
    
    try:
        file_count = split_twitter_log_by_time(input_file, output_dir, max_size_bytes)
        print(f"合計 {file_count} ファイルを作成しました")
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
