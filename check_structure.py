import json
import re
import sys

def check_twitter_export_structure(file_path):
    """Twitterエクスポートデータの構造を確認する関数"""
    try:
        # ファイルを読み込み
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # JavaScript変数宣言を削除
        if file_path.lower().endswith('.js'):
            js_var_pattern = r'^\s*window\.YTD\.[^=]+=\s*'
            match = re.search(js_var_pattern, content)
            if match:
                json_start = match.end()
                bracket_pos = content.find('[', json_start)
                if bracket_pos != -1:
                    content = content[bracket_pos:].strip()
                    if content.endswith(';'):
                        content = content[:-1]
        
        # JSONとしてパース
        data = json.loads(content)
        
        # 配列かどうかを確認
        if isinstance(data, list):
            print(f"データは配列です。要素数: {len(data)}")
            
            # 最初の要素の構造を確認
            if len(data) > 0:
                first_item = data[0]
                print("\n最初の要素の構造:")
                print_structure(first_item)
                
                # 日時情報を探す
                print("\n日時情報の候補:")
                find_date_fields(first_item)
        else:
            print("データは配列ではありません。")
            print("\nルート要素の構造:")
            print_structure(data)
    except Exception as e:
        print(f"エラー: {e}")

def print_structure(obj, indent=0, max_depth=3, current_depth=0, path=""):
    """オブジェクトの構造を再帰的に表示する関数"""
    if current_depth > max_depth:
        print("  " * indent + "...")
        return
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key
            value_type = type(value).__name__
            if isinstance(value, (dict, list)):
                print("  " * indent + f"{key} ({value_type}):")
                print_structure(value, indent + 1, max_depth, current_depth + 1, current_path)
            else:
                print("  " * indent + f"{key} ({value_type}): {str(value)[:50]}")
    elif isinstance(obj, list):
        if len(obj) > 0:
            print("  " * indent + f"配列 (要素数: {len(obj)})")
            print_structure(obj[0], indent + 1, max_depth, current_depth + 1, f"{path}[0]")
        else:
            print("  " * indent + "空の配列")
    else:
        print("  " * indent + str(obj))

def find_date_fields(obj, path="", found_dates=None):
    """オブジェクト内の日時情報の可能性があるフィールドを探す関数"""
    if found_dates is None:
        found_dates = []
    
    date_keywords = ["date", "time", "created", "timestamp"]
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key
            
            # キー名に日時関連のキーワードが含まれているか確認
            if any(keyword in key.lower() for keyword in date_keywords):
                print(f"{current_path} = {str(value)[:50]}")
                found_dates.append((current_path, value))
            
            # 再帰的に探索
            if isinstance(value, (dict, list)):
                find_date_fields(value, current_path, found_dates)
    elif isinstance(obj, list) and len(obj) > 0:
        find_date_fields(obj[0], f"{path}[0]", found_dates)
    
    return found_dates

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python check_structure.py <ファイルパス>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    check_twitter_export_structure(file_path)
