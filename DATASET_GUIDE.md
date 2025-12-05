# 画像データセットとラベル管理ガイド

## 著作権フリー画像の使用について

✅ **著作権フリーの画像を使用して手動でラベルを作成することは全く問題ありません！**

### 注意点

1. **ライセンスの確認**
   - **Public Domain (CC0)**: 商用・非商用問わず自由に使用可能
   - **Creative Commons (CC)**: ライセンス条件を確認（CC-BY、CC-BY-SAなど）
   - **Unsplash License**: 基本的に自由使用可能（クレジット不要）
   - **Pixabay License**: 商用・非商用問わず自由使用可能

2. **クレジット表記**
   - 多くのライセンスではクレジット表記は任意ですが、尊重することを推奨
   - 研究・教育用途であれば通常問題なし

3. **推奨される画像ソース**
   - **Unsplash** (https://unsplash.com/) - 高品質な写真、完全無料
   - **Pixabay** (https://pixabay.com/) - 写真・イラスト・ベクター、無料
   - **Pexels** (https://www.pexels.com/) - 無料の高品質写真
   - **Wikimedia Commons** (https://commons.wikimedia.org/) - 公共領域の画像
   - **Flickr Commons** (https://www.flickr.com/commons) - 公共領域の画像

## 現在のシステムの動作

### ファイル名から自動抽出（現在の方式）

現在のシステムは、**ファイル名の最初の部分を正解キーワードとして自動抽出**します。

#### ファイル名規則

```
{正解キーワード}_{任意の文字列}.{拡張子}
または
{正解キーワード}-{任意の文字列}.{拡張子}
```

#### 例

- `cat_photo.jpg` → 正解は "cat"
- `dog-image.png` → 正解は "dog"
- `apple_red.jpg` → 正解は "apple"
- `airplane_0.png` → 正解は "airplane"

**処理ロジック**（`game_engine.py` より）:
```python
filename = "cat_image.jpg"
name_without_ext = "cat_image"  # 拡張子を除去
correct_answer = name_without_ext.split("_")[0].split("-")[0].lower()
# → "cat"
```

## 手動ラベル付けの方法

### 方法1: ファイル名で管理（推奨・簡単）

1. **画像をダウンロード**
   - 著作権フリーの画像をダウンロード

2. **ファイル名を変更**
   - 正解キーワードを最初に配置
   - 例: `apple.jpg` → `apple_red.jpg`
   - 例: `ネコの写真.jpg` → `cat_japanese.jpg`

3. **imagesフォルダに配置**
   - `images/` フォルダに画像を保存
   - システムが自動的に正解を抽出

**メリット**:
- 簡単で直感的
- ファイル名から正解が一目瞭然
- 追加の設定ファイル不要

### 方法2: JSONファイルで管理（柔軟性重視）

より柔軟にラベルを管理したい場合、JSONファイルでラベルを定義することも可能です。

#### 実装例（オプション機能として追加可能）

```json
{
  "labels.json": {
    "image_001.jpg": "猫",
    "image_002.jpg": "dog",
    "image_003.jpg": "apple"
  }
}
```

現在はファイル名方式が実装されていますが、必要であればJSON方式も追加できます。

## 推奨される作業フロー

### 1. 画像の収集
```
1. 著作権フリー画像サイトで検索
2. 目的に合った画像をダウンロード
3. 画像のライセンス情報を記録（任意）
```

### 2. ファイル名の変更
```
ダウンロード: "photo_12345.jpg"
変更後: "cat_indoor.jpg"

規則:
- 正解キーワードを最初に
- アンダースコア(_)またはハイフン(-)で区切る
- 小文字推奨（自動的に小文字変換されるが統一感のため）
```

### 3. 画像フォルダへの配置
```
visual-guess-challenge/
  └── images/
      ├── cat_indoor.jpg
      ├── cat_outdoor.jpg
      ├── dog_golden.jpg
      ├── apple_red.jpg
      └── ...
```

### 4. 動作確認
- プログラムを実行してランダム画像を表示
- 正解が正しく抽出されているか確認

## ラベル付けのベストプラクティス

### ✅ 良い例

- `cat.jpg` - シンプル
- `dog_golden_retriever.jpg` - 詳細情報も含む
- `apple_red_fruit.jpg` - 説明的
- `bird_sparrow.jpg` - 具体的

### ❌ 避けるべき例

- `IMG_1234.jpg` - 正解キーワードがない
- `photo.jpg` - 正解キーワードがない
- `cat and dog.jpg` - スペースは使わない（アンダースコアやハイフンを使用）

## カテゴリ別の整理

同じカテゴリの画像は、同じ正解キーワードを使うことで自動的に分類されます：

```
images/
  ├── cat_0.jpg
  ├── cat_1.jpg
  ├── cat_2.jpg
  ├── dog_0.jpg
  ├── dog_1.jpg
  └── ...
```

システムが自動的に `get_images_by_category()` で分類してくれます。

## まとめ

- ✅ 著作権フリー画像の使用は問題なし
- ✅ 手動でラベル付けする方法は問題なし
- ✅ ファイル名で管理する方法が最も簡単
- ✅ 必要に応じてより柔軟な方式も追加可能

質問があれば気軽に聞いてください！


