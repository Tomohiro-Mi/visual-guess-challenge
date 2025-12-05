"""
GameEngine - ゲームロジック管理クラス
時間経過に応じた画像処理（線形変換）とスコア計算を担当
"""

import cv2
import os
from image_processor import ImageProcessor
from label_loader import LabelLoader


class GameEngine:
    """ゲームエンジンクラス"""

    def __init__(self, image_path, mode="blur", time_limit=30.0, label_loader=None):
        """
        初期化

        Args:
            image_path: 画像ファイルのパス
            mode: ゲームモード ('blur', 'zoom', 'hybrid')
            time_limit: 画像が完全にクリアになるまでの時間（秒）
            label_loader: LabelLoaderインスタンス（Noneの場合は新規作成）
        """
        self.image_path = image_path
        self.mode = mode
        self.time_limit = time_limit
        self.original_image = None
        self.correct_answers = []  # 複数の正解キーワードを保持
        self.category = None
        self.hint = None

        # 画像プロセッサのインスタンス
        self.image_processor = ImageProcessor()

        # ラベルローダーの初期化
        if label_loader is None:
            self.label_loader = LabelLoader()
        else:
            self.label_loader = label_loader

        # 画像の読み込み
        self.load_image()

        # ラベルから正解キーワードを読み込む
        self.load_answers_from_label()

    def load_image(self):
        """画像を読み込む"""
        if os.path.exists(self.image_path):
            self.original_image = cv2.imread(self.image_path)
            if self.original_image is None:
                raise ValueError(f"画像の読み込みに失敗しました: {self.image_path}")
            # BGRからRGBに変換
            self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        else:
            raise FileNotFoundError(f"画像ファイルが見つかりません: {self.image_path}")

    def load_answers_from_label(self):
        """ラベルファイルから正解キーワードを読み込む"""
        self.correct_answers = self.label_loader.get_answers(self.image_path)
        self.category = self.label_loader.get_category(self.image_path)
        self.hint = self.label_loader.get_hint(self.image_path)
        
        # ラベルが見つからない場合のフォールバック（後方互換性のため）
        if not self.correct_answers:
            # ファイル名から推測（旧方式との互換性）
            filename = os.path.basename(self.image_path)
            name_without_ext = os.path.splitext(filename)[0]
            # ハイフンやアンダースコアで分割して、2番目の部分を正解とする
            parts = name_without_ext.replace("_", "-").split("-")
            if len(parts) >= 2:
                # 数字を除去して正解とする（例: "bird1" -> "bird"）
                answer = parts[1]
                # 末尾の数字を除去
                answer = ''.join([c for c in answer if not c.isdigit()])
                if answer:
                    self.correct_answers = [answer.lower()]
            else:
                # フォールバック: 最初の部分
                self.correct_answers = [parts[0].lower()]

    def set_answers(self, answers):
        """
        正解を手動で設定（複数可）

        Args:
            answers: 正解キーワードのリスト（または単一の文字列）
        """
        if isinstance(answers, list):
            self.correct_answers = [str(a).lower() for a in answers]
        else:
            self.correct_answers = [str(answers).lower()]

    def get_processed_image(self, elapsed_time):
        """
        経過時間に応じた現在の画像を取得

        Args:
            elapsed_time: 経過時間（秒）

        Returns:
            処理された画像
        """
        if self.original_image is None:
            return None

        # 進行度を計算 (0.0:開始直後 -> 1.0:完了)
        if self.time_limit > 0:
            progress = elapsed_time / self.time_limit
        else:
            progress = 1.0

        # 0.0〜1.0の範囲にクリップ
        progress = max(0.0, min(1.0, progress))

        # ImageProcessorには progress (0.0-1.0) を渡す
        if self.mode == "blur":
            return self.image_processor.apply_blur(self.original_image, progress)
        elif self.mode == "zoom":
            return self.image_processor.apply_zoom(self.original_image, progress)
        elif self.mode == "hybrid":
            return self.image_processor.apply_hybrid(self.original_image, progress)
        else:
            return self.original_image.copy()

    def check_answer(self, user_answer):
        """
        回答をチェック（複数の正解キーワードに対応）

        Args:
            user_answer: ユーザーの回答

        Returns:
            (is_correct, display_answer) のタプル
        """
        if not self.correct_answers:
            return False, ""

        user_answer_lower = user_answer.lower().strip()

        # すべての正解キーワードに対してチェック
        for correct_answer in self.correct_answers:
            correct_answer_lower = str(correct_answer).lower().strip()
            
            # 完全一致
            if user_answer_lower == correct_answer_lower:
                return True, self.get_display_answer()
            
            # 部分一致（正解がユーザーの回答に含まれる、またはその逆）
            if (correct_answer_lower in user_answer_lower or 
                user_answer_lower in correct_answer_lower):
                return True, self.get_display_answer()

        return False, self.get_display_answer()
    
    def get_display_answer(self):
        """
        表示用の正解（最初の正解）を取得

        Returns:
            表示用の正解文字列
        """
        if self.correct_answers:
            return self.correct_answers[0]
        return ""

    def calculate_score(self, elapsed_seconds):
        """
        スコアを計算

        Args:
            elapsed_seconds: 経過時間（秒）

        Returns:
            スコア（0-100点）
        """
        # 制限時間を超えていたら0点
        if elapsed_seconds >= self.time_limit:
            return 0

        if self.time_limit <= 0:
            return 0

        # 残り時間の割合をスコアとする (100点満点)
        # 時間経過とともに 100 -> 0 に線形で減少
        ratio_remaining = 1.0 - (elapsed_seconds / self.time_limit)
        score = 100 * ratio_remaining

        return max(0, score)

    def get_mode(self):
        """現在のモードを取得"""
        return self.mode

    def get_correct_answer(self):
        """
        正解を取得（後方互換性のため、最初の正解を返す）

        Returns:
            最初の正解キーワード
        """
        return self.get_display_answer()
    
    def get_correct_answers(self):
        """すべての正解キーワードのリストを取得"""
        return self.correct_answers.copy()
    
    def get_category(self):
        """カテゴリを取得"""
        return self.category
    
    def get_hint(self):
        """ヒント情報を取得"""
        return self.hint
