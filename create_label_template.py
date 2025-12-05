"""
ラベルファイルのテンプレート生成スクリプト
imagesフォルダ内の画像ファイルから、labels.jsonのテンプレートを生成
"""

import os
import json
from pathlib import Path


def create_label_template(images_dir="images", labels_file="labels.json"):
    """
    画像ファイルからラベルファイルのテンプレートを生成
    
    Args:
        images_dir: 画像フォルダのパス
        labels_file: 出力するラベルファイルのパス
    """
    supported_formats = {".png", ".jpg", ".jpeg", ".bmp", ".gif"}
    
    # 既存のラベルファイルを読み込む（存在する場合）
    existing_labels = {}
    if os.path.exists(labels_file):
        try:
            with open(labels_file, 'r', encoding='utf-8') as f:
                existing_labels = json.load(f)
            print(f"既存のラベルファイルを読み込みました: {labels_file}")
        except json.JSONDecodeError as e:
            print(f"警告: 既存のラベルファイルの読み込みに失敗しました: {e}")
            existing_labels = {}
    
    # 画像ファイルを取得
    if not os.path.exists(images_dir):
        print(f"エラー: 画像フォルダが見つかりません: {images_dir}")
        return
    
    image_files = [
        f for f in os.listdir(images_dir)
        if os.path.isfile(os.path.join(images_dir, f))
        and Path(f).suffix.lower() in supported_formats
    ]
    
    if not image_files:
        print(f"画像ファイルが見つかりません: {images_dir}")
        return
    
    # 新しいラベル情報を作成（既存のものを保持）
    labels = existing_labels.copy()
    new_count = 0
    updated_count = 0
    
    for image_file in sorted(image_files):
        if image_file not in labels:
            # 新しいエントリを追加
            labels[image_file] = {
                "answers": [],  # 空のリスト（手動で編集が必要）
                "category": "",  # 空の文字列（オプション）
                "hint": ""  # 空の文字列（オプション）
            }
            new_count += 1
        else:
            # 既存のエントリがある場合は更新（不足しているフィールドを追加）
            if "answers" not in labels[image_file]:
                labels[image_file]["answers"] = []
            if "category" not in labels[image_file]:
                labels[image_file]["category"] = ""
            if "hint" not in labels[image_file]:
                labels[image_file]["hint"] = ""
            updated_count += 1
    
    # ラベルファイルを保存
    try:
        with open(labels_file, 'w', encoding='utf-8') as f:
            json.dump(labels, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ ラベルファイルを生成しました: {labels_file}")
        print(f"   - 総画像数: {len(image_files)}")
        print(f"   - 新規追加: {new_count}件")
        print(f"   - 更新: {updated_count}件")
        print(f"\n⚠️  注意: answersフィールドが空のエントリがあります。")
        print(f"   labels.json を編集して、正解キーワードを手動で設定してください。")
        
    except Exception as e:
        print(f"エラー: ラベルファイルの保存に失敗しました: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("ラベルファイルテンプレート生成ツール")
    print("=" * 60)
    create_label_template()

