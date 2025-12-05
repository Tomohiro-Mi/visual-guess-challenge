"""
ラベルローダー
画像ファイル名と正解キーワード（複数可）、カテゴリ、ヒント情報を管理
"""

import json
import os
from pathlib import Path


class LabelLoader:
    """ラベル管理クラス"""

    def __init__(self, labels_file="labels.json"):
        """
        初期化

        Args:
            labels_file: ラベルファイルのパス
        """
        self.labels_file = labels_file
        self.labels = {}
        self.load_labels()

    def load_labels(self):
        """ラベルファイルを読み込む"""
        if os.path.exists(self.labels_file):
            try:
                with open(self.labels_file, 'r', encoding='utf-8') as f:
                    self.labels = json.load(f)
            except json.JSONDecodeError as e:
                print(f"ラベルファイルの読み込みエラー: {e}")
                self.labels = {}
        else:
            # ラベルファイルが存在しない場合は空の辞書
            self.labels = {}
            print(f"ラベルファイルが見つかりません: {self.labels_file}")

    def get_answers(self, image_filename):
        """
        画像ファイル名から正解キーワードのリストを取得

        Args:
            image_filename: 画像ファイル名（パスを含む場合はbasenameを使用）

        Returns:
            正解キーワードのリスト。見つからない場合は空リスト
        """
        filename = os.path.basename(image_filename)
        if filename in self.labels:
            answers = self.labels[filename].get('answers', [])
            if isinstance(answers, list):
                return answers
            elif isinstance(answers, str):
                return [answers]
            else:
                return []
        return []

    def get_category(self, image_filename):
        """
        画像ファイル名からカテゴリを取得

        Args:
            image_filename: 画像ファイル名

        Returns:
            カテゴリ名。見つからない場合はNone
        """
        filename = os.path.basename(image_filename)
        if filename in self.labels:
            return self.labels[filename].get('category', None)
        return None

    def get_hint(self, image_filename):
        """
        画像ファイル名からヒント情報を取得

        Args:
            image_filename: 画像ファイル名

        Returns:
            ヒントテキスト。見つからない場合はNone
        """
        filename = os.path.basename(image_filename)
        if filename in self.labels:
            return self.labels[filename].get('hint', None)
        return None

    def get_display_answer(self, image_filename):
        """
        画像ファイル名から表示用の正解（最初の正解）を取得

        Args:
            image_filename: 画像ファイル名

        Returns:
            表示用の正解文字列。見つからない場合は空文字列
        """
        answers = self.get_answers(image_filename)
        if answers:
            return answers[0]
        return ""

    def save_labels(self):
        """ラベルファイルを保存"""
        try:
            with open(self.labels_file, 'w', encoding='utf-8') as f:
                json.dump(self.labels, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"ラベルファイルの保存エラー: {e}")
            return False

    def set_label(self, image_filename, answers, category=None, hint=None):
        """
        画像のラベルを設定

        Args:
            image_filename: 画像ファイル名
            answers: 正解キーワードのリスト（または単一の文字列）
            category: カテゴリ名（オプション）
            hint: ヒントテキスト（オプション）
        """
        filename = os.path.basename(image_filename)
        if not isinstance(answers, list):
            answers = [answers] if answers else []
        
        self.labels[filename] = {
            'answers': answers
        }
        if category:
            self.labels[filename]['category'] = category
        if hint:
            self.labels[filename]['hint'] = hint

    def has_label(self, image_filename):
        """画像にラベルが設定されているかチェック"""
        filename = os.path.basename(image_filename)
        return filename in self.labels

    def get_all_labels(self):
        """すべてのラベル情報を取得"""
        return self.labels.copy()

