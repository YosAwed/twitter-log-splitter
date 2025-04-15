import json
import os
import sys
import re
from datetime import datetime
import time
import unicodedata  # Unicode正規化のためのモジュールを追加
from tqdm import tqdm

# chardetライブラリがインストールされているか確認し、なければ警告を表示
try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False
    print("警告: chardetライブラリがインストールされていません。エンコーディング自動検出機能が制限されます。")
    print("pip install chardet でインストールすることをお勧めします。")

def split_twitter_log_by_time(input_file, output_dir, max_size_bytes=5*1024*1024, time_format=None, text_only=False, group_by='month'):
    """
    Twitter投稿ログを時系列順に分割する関数
    
    Parameters:
    - input_file: 入力JSONファイルのパス
    - output_dir: 出力ディレクトリのパス
    - max_size_bytes: 各出力ファイルの最大サイズ（バイト）
    - time_format: 日時情報のフォーマット（Noneの場合は自動検出）
    - text_only: Trueの場合、ツイートのテキストのみを抽出
    - group_by: グループ化の単位（'month': 年月ごと、'year': 年ごと、'all': 全期間）
    """
    # 開始時間を記録
    start_time = time.time()
    
    # 出力ディレクトリの作成
    os.makedirs(output_dir, exist_ok=True)
    
    # ファイルを開いて構造を確認
    try:
        # 試行するエンコーディングのリスト
        encodings = ['utf-8', 'utf-8-sig', 'cp932', 'shift_jis', 'euc_jp', 'iso-2022-jp']
        data = None
        last_error = None
        raw_content = None
        
        # まずchardetでエンコーディングを自動検出
        if HAS_CHARDET:
            try:
                with open(input_file, 'rb') as f_detect:
                    raw_data = f_detect.read(1024*1024)  # 最初の1MBを読み込み
                    result = chardet.detect(raw_data)
                    detected_encoding = result['encoding']
                    confidence = result['confidence']
                    if detected_encoding and confidence > 0.7:
                        print(f"検出されたエンコーディング: {detected_encoding} (信頼度: {confidence:.2f})")
                        if detected_encoding.lower() not in [e.lower() for e in encodings]:
                            encodings.insert(0, detected_encoding)
            except Exception as e:
                print(f"エンコーディング自動検出中にエラーが発生しました: {e}")
        
        # 入力ファイルが.jsファイルかどうかを確認
        is_js_file = input_file.lower().endswith('.js')
        
        # 各エンコーディングを試行
        for encoding in encodings:
            try:
                # ファイルを読み込み
                with open(input_file, 'r', encoding=encoding) as f:
                    raw_content = f.read()
                    
                    # .jsファイルの場合、JavaScript変数宣言部分を削除
                    if is_js_file:
                        # JavaScript変数宣言部分を削除（window.YTD.tweets.part0 = ...）
                        js_var_pattern = r'^\s*window\.YTD\.[^=]+=\s*'
                        match = re.search(js_var_pattern, raw_content)
                        if match:
                            # 変数宣言部分を削除してJSON配列部分を抽出
                            print("Twitter投稿ログ（JavaScript形式）を処理中...（変数宣言部分を削除）")
                            json_start = match.end()
                            # 最初の'['を探す
                            bracket_pos = raw_content.find('[', json_start)
                            if bracket_pos != -1:
                                # '['から始まる部分を抽出
                                raw_content = raw_content[bracket_pos:].strip()
                                # 最後の';'を削除
                                if raw_content.endswith(';'):
                                    raw_content = raw_content[:-1]
                    
                    # JSONとしてパース
                    try:
                        data = json.loads(raw_content)
                        print(f"ファイル読み込み完了: {os.path.getsize(input_file)/1024/1024:.2f} MB (エンコーディング: {encoding})")
                        break  # 成功したらループを抜ける
                    except json.JSONDecodeError as json_err:
                        last_error = json_err
                        print(f"{encoding}エンコーディングでJSONデコードエラー: {json_err}")
            except Exception as e:
                last_error = e
                print(f"{encoding}エンコーディングで読み込み失敗: {e}")
        
        # すべてのエンコーディングが失敗した場合、バイナリモードで読み込みを試行
        if data is None and raw_content is not None:
            # JavaScript形式の場合、別の方法でJSON部分を抽出
            if is_js_file:
                try:
                    # ブラケット内を抽出
                    print("別の方法でJavaScript形式のJSON部分を抽出中...")
                    # 最初の'['と最後の']'を探す
                    bracket_start = raw_content.find('[')
                    bracket_end = raw_content.rfind(']')
                    
                    if bracket_start != -1 and bracket_end != -1 and bracket_end > bracket_start:
                        json_content = raw_content[bracket_start:bracket_end+1]
                        try:
                            data = json.loads(json_content)
                            print("ブラケット内を抽出してJSONとしてパース成功")
                        except json.JSONDecodeError:
                            # 別の方法を試す
                            pass
                except Exception as e:
                    print(f"別の方法でJSON抽出中にエラーが発生しました: {e}")
        
        # それでも失敗した場合、バイナリモードで読み込みを試行
        if data is None:
            try:
                with open(input_file, 'rb') as f_bin:
                    raw_data = f_bin.read()
                    # BOMを確認
                    if raw_data.startswith(b'\xef\xbb\xbf'):  # UTF-8 with BOM
                        raw_data = raw_data[3:]
                    
                    # .jsファイルの場合、JavaScript変数宣言部分を削除
                    if is_js_file:
                        # バイナリデータをテキストにデコード
                        for encoding in ['utf-8', 'cp932', 'shift_jis', 'euc_jp']:
                            try:
                                text_data = raw_data.decode(encoding)
                                # ブラケット内を抽出
                                bracket_start = text_data.find('[')
                                bracket_end = text_data.rfind(']')
                                
                                if bracket_start != -1 and bracket_end != -1 and bracket_end > bracket_start:
                                    json_content = text_data[bracket_start:bracket_end+1]
                                    try:
                                        data = json.loads(json_content)
                                        print(f"バイナリモードで読み込み成功: {encoding}")
                                        break
                                    except json.JSONDecodeError:
                                        continue
                            except UnicodeDecodeError:
                                continue
                    else:
                        # 通常のJSONファイルの場合
                        try:
                            # 様々なエンコーディングでデコードを試行
                            for encoding in ['utf-8', 'cp932', 'shift_jis', 'euc_jp']:
                                try:
                                    decoded_data = raw_data.decode(encoding)
                                    data = json.loads(decoded_data)
                                    print(f"バイナリモードで読み込み成功: {encoding}")
                                    break
                                except (UnicodeDecodeError, json.JSONDecodeError):
                                    continue
                        except Exception as e:
                            last_error = e
            except Exception as e:
                last_error = e
                print(f"バイナリモードでの読み込みに失敗しました: {e}")
        
        # それでも失敗した場合、エラーを発生
        if data is None:
            raise ValueError(f"ファイルを読み込めませんでした。すべてのエンコーディングが失敗しました。最後のエラー: {last_error}")
    except FileNotFoundError:
        raise FileNotFoundError(f"ファイルが見つかりません: {input_file}")
    except PermissionError:
        raise PermissionError(f"ファイルを開く権限がありません: {input_file}")
    
    # Twitterログの主要な構造を特定
    tweets = []
    if isinstance(data, list):
        # データが直接投稿の配列である場合
        # Twitterエクスポートデータの場合、各要素が {"tweet": {...}} 形式になっている
        if len(data) > 0 and isinstance(data[0], dict):
            if 'tweet' in data[0]:
                # {"tweet": {...}} 形式の場合、tweet内のデータを使用
                print("Twitterエクスポート形式（{\"tweet\": {...}}）を検出しました")
                tweets = [item['tweet'] for item in data if 'tweet' in item]
            else:
                tweets = data  # 通常の配列形式
        else:
            tweets = data
    elif isinstance(data, dict):
        # 一般的なTwitterエクスポート形式を検索
        for key in ['tweet', 'tweets', 'data']:
            if key in data and isinstance(data[key], list):
                tweets = data[key]
                break
        
        # さらに深い階層も検索
        if not tweets and 'data' in data:
            data_obj = data['data']
            if isinstance(data_obj, dict):
                for key in ['tweet', 'tweets']:
                    if key in data_obj and isinstance(data_obj[key], list):
                        tweets = data_obj[key]
                        break
    
    if not tweets:
        raise ValueError("入力ファイル内にTwitter投稿の配列が見つかりません")
    
    # 空のツイートリストの処理
    if len(tweets) == 0:
        print("警告: ツイートリストが空です。処理するデータがありません。")
        return 0
    
    print(f"処理対象ツイート数: {len(tweets)}")
    
    # tqdmで進捗バーを表示
    tweet_iter = tqdm(tweets, desc="グループ化処理", unit="tweet")
    
    # 日時のキーを特定（異なる形式に対応）
    date_keys = ['created_at', 'timestamp', 'time', 'date']
    date_key = None
    
    # まず直接のキーを確認
    for key in date_keys:
        if tweets and key in tweets[0]:
            date_key = key
            break
    
    # ネストされた構造も確認
    if not date_key:
        # ネストされた構造を探索する関数
        def find_nested_key(obj, target_keys, path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_path = f"{path}.{k}" if path else k
                    if k in target_keys:
                        return k, new_path, v
                    if isinstance(v, (dict, list)):
                        result = find_nested_key(v, target_keys, new_path)
                        if result:
                            return result
            elif isinstance(obj, list) and obj:
                return find_nested_key(obj[0], target_keys, f"{path}[0]")
            return None
        
        # ネストされたキーを検索
        nested_result = find_nested_key(tweets[0], date_keys)
        if nested_result:
            key_name, full_path, value = nested_result
            print(f"ネストされた日時情報を検出しました: {full_path} = {value}")
            
            # ネストされたキーへのアクセス関数を定義
            def get_nested_value(obj, path):
                parts = path.split('.')
                current = obj
                for part in parts:
                    if part.endswith(']'):
                        # リスト要素へのアクセス（例: items[0]）
                        list_name, idx = part[:-1].split('[')  
                        current = current[list_name][int(idx)]
                    else:
                        current = current[part]
                return current
            
            # 元の日時キーとパスを保存
            date_key = key_name
            date_key_path = full_path
            
            # 元のツイートオブジェクトを変更せずに日時情報を取得するラムダ関数を定義
            original_tweets = tweets
            date_key_parts = date_key_path.split('.')
            if len(date_key_parts) > 1:
                # ネストされた場合は、最初の部分がキー名
                date_container_key = date_key_parts[0]
                # ラムダ関数を使用してネストされた値を取得
                get_date_value = lambda x: get_nested_value(x, date_key_path[len(date_container_key)+1:])
            else:
                # ネストされていない場合は直接アクセス
                get_date_value = lambda x: x[date_key]
    
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
        # ネストされた日時情報がある場合は、get_date_value関数を使用
        if 'get_date_value' in locals():
            tweets.sort(key=lambda x: parse_date(get_date_value(x)))
        else:
            tweets.sort(key=lambda x: parse_date(x[date_key]))
        print("ソート完了")
    except Exception as e:
        print(f"警告: 時系列順のソートに失敗しました: {e}")
    
    # 時間単位でグループ化
    print("ツイートを時間単位でグループ化中...")
    grouped_tweets = {}
    # tqdmで進捗バーを表示
    for tweet in tqdm(tweets, desc="グループ化", unit="tweet"):
        try:
            # ネストされた日時情報がある場合は、get_date_value関数を使用
            if 'get_date_value' in locals():
                dt = parse_date(get_date_value(tweet))
            else:
                dt = parse_date(tweet[date_key])
            
            # グループ化の単位に応じてキーを生成
            if group_by == 'month':
                key = dt.strftime('%Y-%m')  # 年月をキーとして使用
            elif group_by == 'year':
                key = dt.strftime('%Y')     # 年をキーとして使用
            else:  # 'all'
                key = 'all_tweets'          # すべてのツイートを一つのグループに
            
            if key not in grouped_tweets:
                grouped_tweets[key] = []
            grouped_tweets[key].append(tweet)
        except Exception as e:
            date_value = get_date_value(tweet) if 'get_date_value' in locals() else tweet.get(date_key, 'キーなし')
            print(f"警告: 日時パースエラー {date_value}: {e}")
    print(f"グループ化完了: {len(grouped_tweets)} 期間に分類")
    
    # 各時間グループをファイルサイズ制限に従って分割
    file_count = 1
    total_processed = 0
    print("ファイル分割処理を開始...")
    # tqdmで進捗バーを表示
    for period, period_tweets in tqdm(sorted(grouped_tweets.items()), desc="ファイル分割", unit="期間"):
        print(f"期間 {period} の処理中... ({len(period_tweets)} ツイート)")
        current_batch = []
        file_count_in_period = 1
        i = 0
        with tqdm(total=len(period_tweets), desc=f"{period} ツイート分割", unit="tweet") as pbar:
            while i < len(period_tweets):
                current_batch = []
                current_size = 2  # '[]' の初期サイズ
                while i < len(period_tweets):
                    tweet = period_tweets[i]
                    # バッチにツイートを追加してシリアライズ後のサイズを計算
                    temp_batch = current_batch + [tweet]
                    if text_only:
                        # テキスト抽出モード
                        all_text_content = []
                        for t in temp_batch:
                            tweet_data = t
                            if 'tweet' in t and isinstance(t['tweet'], dict):
                                tweet_data = t['tweet']
                            text_content = tweet_data.get('full_text') or tweet_data.get('text')
                            if text_content:
                                text_content = unicodedata.normalize('NFKC', text_content)
                                text_content = text_content.replace('\n', ' ').replace('\r', ' ')
                                text_content = ' '.join(text_content.split())
                                text_content = ''.join(ch for ch in text_content if unicodedata.category(ch)[0] != 'C' or ch in (' ', '\t', '\n'))
                                text_content = remove_emojis(text_content)
                                all_text_content.append(text_content)
                        combined_text = '\n'.join(all_text_content) + '\n'
                        batch_bytes = len(combined_text.encode('utf-8'))
                    else:
                        # JSONモード
                        try:
                            batch_bytes = len(json.dumps(temp_batch, ensure_ascii=False, separators=(",", ":")).encode('utf-8'))
                        except Exception:
                            batch_bytes = sys.getsizeof(str(temp_batch))
                    if batch_bytes > max_size_bytes and current_batch:
                        break  # 直前のバッチで出力
                    current_batch.append(tweet)
                    i += 1
                if not current_batch:
                    # 1ツイートだけでサイズ超過する場合は強制的に1件で出力
                    current_batch = [period_tweets[i]]
                    i += 1
                output_filename = f"{period}_part_{file_count_in_period}.txt"
                output_path = os.path.join(output_dir, output_filename)
                counter = 1
                while os.path.exists(output_path):
                    output_filename = f"{period}_part_{file_count_in_period}_{counter}.txt"
                    output_path = os.path.join(output_dir, output_filename)
                    counter += 1
                if text_only:
                    all_text_content = []
                    for tweet in current_batch:
                        tweet_data = tweet
                        if 'tweet' in tweet and isinstance(tweet['tweet'], dict):
                            tweet_data = tweet['tweet']
                        text_content = tweet_data.get('full_text') or tweet_data.get('text')
                        if text_content:
                            text_content = unicodedata.normalize('NFKC', text_content)
                            text_content = text_content.replace('\n', ' ').replace('\r', ' ')
                            text_content = ' '.join(text_content.split())
                            text_content = ''.join(ch for ch in text_content if unicodedata.category(ch)[0] != 'C' or ch in (' ', '\t', '\n'))
                            text_content = remove_emojis(text_content)
                            all_text_content.append(text_content)
                    combined_text = '\n'.join(all_text_content) + '\n'
                    write_success = write_to_file(output_path, combined_text, is_text=True)
                    if not write_success:
                        print(f"警告: {output_path} への書き込みに失敗しました")
                else:
                    write_success = write_to_file(output_path, current_batch)
                    if not write_success:
                        print(f"警告: {output_path} への書き込みに失敗しました")
                file_count_in_period += 1
                file_count += 1
                total_processed += len(current_batch)
                pbar.update(len(current_batch))
    # 処理時間を計算
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"処理完了: {len(tweets)} ツイートを処理しました (処理時間: {elapsed_time:.2f}秒)")
    return file_count - 1

# 顔文字を削除する関数
def remove_emojis(text):
    """
    顔文字を削除する関数
    
    Parameters:
    - text: 顔文字を含むテキスト
    
    Returns:
    - 顔文字を削除したテキスト
    """
    # 顔文字を削除するための正規表現パターン
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # 顔文字: 笑顔
        "\U0001F300-\U0001F5FF"  # 顔文字: その他
        "\U0001F680-\U0001F6FF"  # 顔文字: 交通機関
        "\U0001F700-\U0001F77F"  # 顔文字: その他
        "\U0001F780-\U0001F7FF"  # 顔文字: その他
        "\U0001F800-\U0001F8FF"  # 顔文字: その他
        "\U0001F900-\U0001F9FF"  # 顔文字: その他
        "\U0001FA00-\U0001FA6F"  # 顔文字: その他
        "\U0001FA70-\U0001FAFF"  # 顔文字: その他
        "\U00002702-\U000027B0"  # 顔文字: Dingbats
        "\U000024C2-\U0000257F"  # 顔文字: その他
        "\U00002600-\U000026FF"  # 顔文字: その他
        "\U00002700-\U000027BF"  # 顔文字: Dingbats
        "\U0000FE00-\U0000FE0F"  # 顔文字: その他
        "\U0001F000-\U0001F02F"  # 顔文字: その他
        "\U0001F0A0-\U0001F0FF"  # 顔文字: トランプ
        "\U0001F100-\U0001F1FF"  # 顔文字: その他
        "\U0001F200-\U0001F2FF"  # 顔文字: その他
        "\U0001F300-\U0001F5FF"  # 顔文字: その他
        "\U0001F600-\U0001F64F"  # 顔文字: 笑顔
        "\U0001F680-\U0001F6FF"  # 顔文字: 交通機関
        "\U0001F700-\U0001F77F"  # 顔文字: その他
        "\U000020D0-\U000020FF"  # 顔文字: その他
        "\U0000FE00-\U0000FE0F"  # 顔文字: その他
        "\U0001F900-\U0001F9FF"  # 顔文字: その他
        "\U00002600-\U000027BF"  # 顔文字: その他
        "\U00002B50"            # 顔文字: ↑
        "\U00002B55"            # 顔文字: ↓
        "\U00003030"            # 顔文字: 〰
        "\U00003297"            # 顔文字: ㊗
        "\U00003299"            # 顔文字: ㊙
        "\U0001F201"            # 顔文字: →
        "\U0001F202"            # 顔文字: ←
        "\U0001F21A"            # 顔文字: ↩
        "\U0001F22F"            # 顔文字: ↪
        "\U0001F232-\U0001F23A"  # 顔文字: その他
        "\U0001F250-\U0001F251"  # 顔文字: その他
        "\U0001F300-\U0001F320"  # 顔文字: その他
        "\U0001F330-\U0001F335"  # 顔文字: その他
        "\U0001F337-\U0001F37C"  # 顔文字: その他
        "\U0001F380-\U0001F393"  # 顔文字: その他
        "\U0001F3A0-\U0001F3C4"  # 顔文字: その他
        "\U0001F3C6-\U0001F3CA"  # 顔文字: その他
        "\U0001F3E0-\U0001F3F0"  # 顔文字: その他
        "\U0001F400-\U0001F43E"  # 顔文字: その他
        "\U0001F440"            # 顔文字: 顔文字
        "\U0001F442-\U0001F4F7"  # 顔文字: その他
        "\U0001F4F9-\U0001F4FC"  # 顔文字: その他
        "\U0001F500-\U0001F53D"  # 顔文字: その他
        "\U0001F550-\U0001F567"  # 顔文字: その他
        "\U0001F5FB-\U0001F5FF"  # 顔文字: その他
        "\U0001F601-\U0001F610"  # 顔文字: 笑顔
        "\U0001F612-\U0001F614"  # 顔文字: 笑顔
        "\U0001F616"            # 顔文字: 笑顔
        "\U0001F618"            # 顔文字: 笑顔
        "\U0001F61A"            # 顔文字: 笑顔
        "\U0001F61C-\U0001F61E"  # 顔文字: 笑顔
        "\U0001F620-\U0001F625"  # 顔文字: 笑顔
        "\U0001F628-\U0001F62B"  # 顔文字: 笑顔
        "\U0001F62D"            # 顔文字: 笑顔
        "\U0001F630-\U0001F633"  # 顔文字: 笑顔
        "\U0001F635-\U0001F640"  # 顔文字: 笑顔
        "\U0001F645-\U0001F64F"  # 顔文字: 笑顔
        "\U0001F680-\U0001F6C5"  # 顔文字: 交通機関
        "\U0001F6CC"            # 顔文字: 交通機関
        "\U0001F6D0-\U0001F6D2"  # 顔文字: その他
        "\U0001F6D5-\U0001F6D7"  # 顔文字: その他
        "\U0001F6EB-\U0001F6EC"  # 顔文字: その他
        "\U0001F6F4-\U0001F6FC"  # 顔文字: 交通機関
        "\U0001F7E0-\U0001F7EB"  # 顔文字: その他
        "\U0001F90C-\U0001F93A"  # 顔文字: その他
        "\U0001F93C-\U0001F945"  # 顔文字: その他
        "\U0001F947-\U0001F978"  # 顔文字: その他
        "\U0001F97A-\U0001F9CB"  # 顔文字: その他
        "\U0001F9CD-\U0001F9FF"  # 顔文字: その他
        "\U0001FA70-\U0001FA74"  # 顔文字: その他
        "\U0001FA78-\U0001FA7A"  # 顔文字: その他
        "\U0001FA80-\U0001FA86"  # 顔文字: その他
        "\U0001FA90-\U0001FAA8"  # 顔文字: その他
        "\U0001FAB0-\U0001FAB6"  # 顔文字: その他
        "\U0001FAC0-\U0001FAC2"  # 顔文字: その他
        "\U0001FAD0-\U0001FAD6"  # 顔文字: その他
        "]", 
        flags=re.UNICODE
    )
    
    # 顔文字を削除
    return emoji_pattern.sub(' ', text)

# ファイル出力時のエンコーディング処理を強化
def write_to_file(file_path, content, is_text=False):
    """
    ファイルへの書き込みを安全に行う関数
    
    Parameters:
    - file_path: 出力ファイルのパス
    - content: 書き込む内容（テキストまたはJSON）
    - is_text: Trueの場合はテキストモード、Falseの場合はJSONモード
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as out:
            if is_text:
                out.write(content)
            else:
                json.dump(content, out, ensure_ascii=False, indent=None)
        return True
    except UnicodeEncodeError:
        # UTF-8でエンコードできない場合、置換モードで再試行
        try:
            with open(file_path, 'w', encoding='utf-8', errors='replace') as out:
                if is_text:
                    out.write(content)
                else:
                    json.dump(content, out, ensure_ascii=False, indent=None)
            print(f"警告: {file_path} の書き込み時にUnicodeエンコードエラーが発生しました。一部の文字が置換されています。")
            return True
        except Exception as e:
            print(f"エラー: {file_path} への書き込みに失敗しました: {e}")
            return False
    except Exception as e:
        print(f"エラー: {file_path} への書き込みに失敗しました: {e}")
        return False

def main():
    if len(sys.argv) < 3:
        print(f"使用方法: {sys.argv[0]} <入力ファイル> <出力ディレクトリ> [最大ファイルサイズ(MB)] [オプション]")
        print("オプション:")
        print("  --text-only: ツイートのテキスト部分のみを抽出して保存")
        print("  --group-by=<month|year|all>: ツイートのグループ化単位を指定")
        print("    month: 年月ごとに分割（デフォルト）")
        print("    year: 年ごとに分割")
        print("    all: 全期間を一つにまとめる（ファイル数を最小化）")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    max_size_mb = 5  # デフォルト5MB
    text_only = False
    group_by = 'month'  # デフォルトは月単位
    
    # 残りの引数を処理
    for i in range(3, len(sys.argv)):
        arg = sys.argv[i]
        if arg == "--text-only":
            text_only = True
        elif arg.startswith("--group-by="):
            group_option = arg.split("=")[1].lower()
            if group_option in ['month', 'year', 'all']:
                group_by = group_option
            else:
                print(f"警告: 無効なグループ化オプションです。デフォルトの {group_by} を使用します。")
        elif i == 3 and not arg.startswith("--"):  # 3番目の引数がオプションでなければサイズと解釈
            try:
                max_size_mb = float(arg)
            except ValueError:
                print(f"警告: 無効なサイズ指定です。デフォルトの {max_size_mb}MB を使用します。")
    
    max_size_bytes = int(max_size_mb * 1024 * 1024)
    
    try:
        file_count = split_twitter_log_by_time(input_file, output_dir, max_size_bytes, text_only=text_only, group_by=group_by)
        print(f"合計 {file_count} ファイルを作成しました")
        if text_only:
            print("テキスト抽出モード: ツイートのテキスト部分のみが保存されました")
        print(f"グループ化単位: {group_by}")
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
