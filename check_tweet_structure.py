import json
import re

# ファイルを読み込み
with open('tweets.js', 'r', encoding='utf-8') as f:
    content = f.read()

# JavaScript変数宣言部分を削除
js_var_pattern = r'^\s*window\.YTD\.[^=]+=\s*'
match = re.search(js_var_pattern, content)
if match:
    json_start = match.end()
    # 最初の'['を探す
    bracket_pos = content.find('[', json_start)
    if bracket_pos != -1:
        # '['から始まる部分を抽出
        json_content = content[bracket_pos:].strip()
        # 最後の';'を削除
        if json_content.endswith(';'):
            json_content = json_content[:-1]

        # JSONとしてパース
        data = json.loads(json_content)
        
        # 最初のツイートの構造を確認
        if data and len(data) > 0:
            first_tweet = data[0]
            print("最初のツイートの構造:")
            print(json.dumps(first_tweet, indent=2, ensure_ascii=False)[0:1000])
            
            # テキストフィールドを探す
            if 'tweet' in first_tweet and isinstance(first_tweet['tweet'], dict):
                tweet_data = first_tweet['tweet']
                print("\nテキストフィールド:")
                if 'full_text' in tweet_data:
                    print(f"full_text: {tweet_data['full_text']}")
                elif 'text' in tweet_data:
                    print(f"text: {tweet_data['text']}")
                else:
                    # 再帰的にテキストフィールドを探す
                    def find_text_fields(obj, path=""):
                        if isinstance(obj, dict):
                            for k, v in obj.items():
                                if k in ['full_text', 'text'] and isinstance(v, str):
                                    print(f"{path}.{k}: {v}")
                                if isinstance(v, (dict, list)):
                                    find_text_fields(v, f"{path}.{k}" if path else k)
                        elif isinstance(obj, list) and obj:
                            for i, item in enumerate(obj):
                                find_text_fields(item, f"{path}[{i}]")
                    
                    find_text_fields(tweet_data, "tweet")
            else:
                print("\n'tweet'キーが見つからないか、辞書型ではありません")
        else:
            print("データが空です")
    else:
        print("JSONの開始ブラケットが見つかりません")
else:
    print("JavaScript変数宣言が見つかりません")
