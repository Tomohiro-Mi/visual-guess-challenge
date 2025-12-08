"""
Visual Guess Challenge - メインアプリケーション
PyQtを使用したGUIアプリケーションのメインウィンドウ
"""
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
    QFileDialog,
    QDesktopWidget,
    QStackedWidget,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QFont
import os

from game_engine import GameEngine
from timer_controller import TimerController
from dataset_loader import DatasetLoader
from progress_bar import ProgressBar
from label_loader import LabelLoader


class HomeScreen(QWidget):
    """ホーム画面"""
    
    start_game_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # タイトル
        title_label = QLabel("タイムアタック画像クイズ")
        title_font = QFont()
        title_font.setPointSize(36)  # 34-38ptの中間値
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        
        # サブタイトル（キャッチコピー）
        subtitle_label = QLabel(
            "ぼやけた画像やズーム画像が少しずつクリアに。\n"
            "素早く答えを当てて高スコアを狙おう！"
        )
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(15)  # 14-16ptの中間値
        subtitle_label.setFont(subtitle_font)
        
        # 説明文（ゲームのルール）
        description_label = QLabel(
            "最初はぼやけた画像やズームされた画像からスタートします。\n"
            "時間とともに画像が徐々に鮮明になります。\n"
            "できるだけ早い段階で当てて、高スコアを目指しましょう！"
        )
        description_label.setAlignment(Qt.AlignCenter)
        description_font = QFont()
        description_font.setPointSize(13)  # 12-13ptの中間値
        description_label.setFont(description_font)
        
        # 行間を調整するためのスタイルシート
        description_label.setStyleSheet(
            "line-height: 1.4;"  # 行間1.4倍
        )
        
        # スタートボタン
        start_button = QPushButton("ゲームをはじめる")
        start_button.setMinimumSize(220, 60)
        start_button_font = QFont()
        start_button_font.setPointSize(18)
        start_button.setFont(start_button_font)
        start_button.clicked.connect(self.start_game_signal.emit)
        
        # ボタンのスタイルシート（角丸とホバー効果）
        start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 11px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        layout.addStretch()
        layout.addWidget(title_label)
        layout.addSpacing(12)  # タイトル下余白 10-15pxの中間
        layout.addWidget(subtitle_label)
        layout.addSpacing(15)  # タイトルとの間隔
        layout.addWidget(description_label)
        layout.addSpacing(22)  # サブタイトルとの間隔 20-25pxの中間
        layout.addWidget(start_button, alignment=Qt.AlignCenter)
        layout.addSpacing(40)  # 説明文との間隔 35-45pxの中間
        layout.addStretch()
        
        self.setLayout(layout)


class GameSetupScreen(QWidget):
    """ゲーム設定画面（モード選択と回数選択を統合）"""
    
    session_started_signal = pyqtSignal(str, int)  # モードと問題数を送信
    back_to_home_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.selected_mode = None
        self.selected_question_count = 5  # デフォルトは5問
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(40)
        
        # タイトル
        title_label = QLabel("ゲーム設定")
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        
        # 上部：モード選択エリア
        mode_section = QVBoxLayout()
        mode_section.setSpacing(15)
        mode_label = QLabel("モードを選択してください")
        mode_label_font = QFont()
        mode_label_font.setPointSize(18)
        mode_label_font.setBold(True)
        mode_label.setFont(mode_label_font)
        mode_label.setAlignment(Qt.AlignCenter)
        
        # モードボタン（横並び）
        mode_button_layout = QHBoxLayout()
        mode_button_layout.setSpacing(30)
        
        self.mode_buttons = {}
        modes = [
            ("blur", "Blur"),
            ("zoom", "Zoom"),
            ("hybrid", "Hybrid")
        ]
        
        # 中央揃えのため、最初にストレッチを追加
        mode_button_layout.addStretch()
        
        for mode_key, mode_name in modes:
            btn = QPushButton(f"{mode_name}\nモード")
            btn.setMinimumSize(200, 100)
            btn.setCheckable(True)
            btn_font = QFont()
            btn_font.setPointSize(16)
            btn.setFont(btn_font)
            btn.clicked.connect(lambda checked, m=mode_key: self.select_mode(m))
            self.mode_buttons[mode_key] = btn
            mode_button_layout.addWidget(btn)
        
        # 中央揃えのため、最後にもストレッチを追加
        mode_button_layout.addStretch()
        
        mode_section.addWidget(mode_label)
        mode_section.addLayout(mode_button_layout)
        
        # 下部：回数選択エリア
        question_section = QVBoxLayout()
        question_section.setSpacing(15)
        question_label = QLabel("問題数を選択してください")
        question_label_font = QFont()
        question_label_font.setPointSize(18)
        question_label_font.setBold(True)
        question_label.setFont(question_label_font)
        question_label.setAlignment(Qt.AlignCenter)
        
        # 問題数ボタン（横並び）
        question_button_layout = QHBoxLayout()
        question_button_layout.setSpacing(30)
        
        self.question_buttons = {}
        question_counts = [5, 10, 20]
        
        # 中央揃えのため、最初にストレッチを追加
        question_button_layout.addStretch()
        
        for count in question_counts:
            btn = QPushButton(f"{count}問")
            btn.setMinimumSize(200, 100)
            btn.setCheckable(True)
            if count == 5:  # デフォルトで5問を選択
                btn.setChecked(True)
            btn_font = QFont()
            btn_font.setPointSize(16)
            btn.setFont(btn_font)
            btn.clicked.connect(lambda checked, c=count: self.select_question_count(c))
            self.question_buttons[count] = btn
            question_button_layout.addWidget(btn)
        
        # 中央揃えのため、最後にもストレッチを追加
        question_button_layout.addStretch()
        
        question_section.addWidget(question_label)
        question_section.addLayout(question_button_layout)
        
        # ボタン
        button_layout = QHBoxLayout()
        start_button = QPushButton("ゲーム開始")
        start_button.setMinimumSize(250, 70)
        start_button_font = QFont()
        start_button_font.setPointSize(18)
        start_button.setFont(start_button_font)
        start_button.clicked.connect(self.start_session)
        
        back_button = QPushButton("戻る")
        back_button.setMaximumWidth(150)
        back_button.clicked.connect(self.back_to_home_signal.emit)
        
        button_layout.addStretch()
        button_layout.addWidget(back_button)
        button_layout.addWidget(start_button)
        button_layout.addStretch()
        
        # レイアウトの組み立て
        layout.addStretch()
        layout.addWidget(title_label)
        layout.addSpacing(40)
        layout.addLayout(mode_section)
        layout.addSpacing(60)
        layout.addLayout(question_section)
        layout.addSpacing(60)
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def select_mode(self, mode):
        """モードを選択"""
        self.selected_mode = mode
        # 他のボタンのチェックを外す
        for mode_key, btn in self.mode_buttons.items():
            if mode_key != mode:
                btn.setChecked(False)
    
    def select_question_count(self, count):
        """問題数を選択"""
        self.selected_question_count = count
        # 他のボタンのチェックを外す
        for btn_count, btn in self.question_buttons.items():
            if btn_count != count:
                btn.setChecked(False)
    
    def start_session(self):
        """セッションを開始"""
        if self.selected_mode:
            self.session_started_signal.emit(self.selected_mode, self.selected_question_count)
        else:
            QMessageBox.warning(self, "警告", "モードを選択してください")


class ResultScreen(QWidget):
    """結果画面"""
    
    back_to_home_signal = pyqtSignal()
    restart_signal = pyqtSignal(str)  # モードを送信して再開
    
    def __init__(self):
        super().__init__()
        self.session_mode = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(30)
        
        # タイトル
        self.title_label = QLabel("セッション終了")
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        
        # 結果表示エリア
        self.result_label = QLabel()
        self.result_label.setAlignment(Qt.AlignCenter)
        result_font = QFont()
        result_font.setPointSize(14)
        self.result_label.setFont(result_font)
        
        # ボタン
        button_layout = QHBoxLayout()
        home_button = QPushButton("ホームに戻る")
        home_button.setMinimumSize(180, 50)
        home_button.clicked.connect(self.back_to_home_signal.emit)
        
        restart_button = QPushButton("もう一度プレイ")
        restart_button.setMinimumSize(180, 50)
        restart_button.clicked.connect(self.restart_game)
        
        button_layout.addStretch()
        button_layout.addWidget(home_button)
        button_layout.addWidget(restart_button)
        button_layout.addStretch()
        
        layout.addStretch()
        layout.addWidget(self.title_label)
        layout.addSpacing(20)
        layout.addWidget(self.result_label)
        layout.addSpacing(40)
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def display_results(self, session_stats):
        """結果を表示"""
        total_questions = session_stats['total_questions']
        correct_count = session_stats['correct_count']
        total_score = session_stats['total_score']
        average_score = session_stats['average_score']
        accuracy = session_stats['accuracy']
        self.session_mode = session_stats['mode']
        
        result_text = (
            f"問題数: {total_questions}問\n\n"
            f"正解数: {correct_count}問\n"
            f"正答率: {accuracy:.1f}%\n\n"
            f"総合スコア: {total_score:.1f}点\n"
            f"平均スコア: {average_score:.1f}点"
        )
        
        self.result_label.setText(result_text)
    
    def restart_game(self):
        """ゲームを再開"""
        if self.session_mode:
            self.restart_signal.emit(self.session_mode)


class GameScreen(QWidget):
    """ゲーム画面"""
    
    back_to_home_signal = pyqtSignal()
    session_complete_signal = pyqtSignal(dict)  # セッション結果を送信
    
    def __init__(self):
        super().__init__()
        # ゲーム関連のインスタンス
        self.game_engine = None
        self.timer_controller = TimerController()
        self.dataset_loader = DatasetLoader()
        self.progress_bar = ProgressBar()
        self.label_loader = LabelLoader()

        # UIコンポーネント
        self.image_label = None
        self.answer_input = None
        self.submit_button = None
        self.time_label = None
        self.score_label = None
        self.question_counter_label = None
        self.next_button_visible = False

        # タイマー
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        
        # セッション管理
        self.current_mode = None
        self.session_question_count = 0  # セッションの問題数
        self.session_current_question = 0  # 現在の問題番号
        self.session_scores = []  # 各問題のスコア
        self.session_correct_count = 0  # 正解数
        self.session_is_active = False  # セッションが有効か
        self.session_used_images = set()  # セッション中に使用した画像のパスを記録

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # ヘッダー（ホームに戻るボタン）
        header_layout = QHBoxLayout()
        back_button = QPushButton("ホームに戻る")
        back_button.clicked.connect(self.back_to_home_signal.emit)
        header_layout.addWidget(back_button)
        header_layout.addStretch()

        # 操作ボタンエリア
        control_layout = QHBoxLayout()
        self.load_button = QPushButton("画像読み込み")
        self.random_button = QPushButton("ランダム画像")
        self.next_button = QPushButton("次へ")
        self.next_button.setVisible(False)
        reset_button = QPushButton("リセット")

        self.load_button.clicked.connect(self.load_image)
        self.random_button.clicked.connect(self.load_random_image)
        self.next_button.clicked.connect(self.next_question)
        reset_button.clicked.connect(self.reset_game)

        control_layout.addWidget(self.load_button)
        control_layout.addWidget(self.random_button)
        control_layout.addWidget(self.next_button)
        control_layout.addWidget(reset_button)
        control_layout.addStretch()

        # 情報表示エリア
        info_layout = QHBoxLayout()
        self.time_label = QLabel("経過時間：00.0s")
        self.time_label.setFixedWidth(160)  # 固定幅を設定して揺れを防止
        
        self.score_label = QLabel("スコア：---")
        self.score_label.setFixedWidth(180)  # 固定幅を設定して揺れを防止
        
        self.question_counter_label = QLabel("問題：---")
        self.question_counter_label.setFixedWidth(120)  # 固定幅を設定して揺れを防止
        
        info_layout.addWidget(self.question_counter_label)
        info_layout.addWidget(self.time_label)
        info_layout.addWidget(self.score_label)
        info_layout.addWidget(self.progress_bar)
        info_layout.addStretch()
        
        # ヒント表示エリア
        hint_container = QWidget()
        hint_container.setMaximumHeight(35)  # ヒント表示領域の最大高さを制限
        hint_layout = QHBoxLayout(hint_container)
        hint_layout.setContentsMargins(5, 2, 5, 2)  # 上下のマージンを小さく
        self.hint_label = QLabel("")
        self.hint_label.setStyleSheet("color: #666; font-style: italic; padding: 2px;")
        self.category_label = QLabel("")
        self.category_label.setStyleSheet("color: #0066cc; font-weight: bold; padding: 2px;")
        hint_layout.addWidget(self.category_label)
        hint_layout.addStretch()
        hint_layout.addWidget(self.hint_label)

        # 画像表示エリア
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(450)  # 画像表示領域を拡大
        self.image_label.setStyleSheet(
            "border: 2px solid gray; background-color: #f0f0f0;"
        )
        self.image_label.setText("画像がここに表示されます")

        # 回答入力エリア
        answer_layout = QHBoxLayout()
        answer_label = QLabel("回答入力：")
        answer_label_font = QFont()
        answer_label_font.setPointSize(14)
        answer_label.setFont(answer_label_font)
        
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("ここに回答を入力してください")
        self.answer_input.setMinimumHeight(50)  # 高さを大きく
        input_font = QFont()
        input_font.setPointSize(16)  # フォントサイズを大きく
        self.answer_input.setFont(input_font)
        
        self.submit_button = QPushButton("回答する")
        self.submit_button.setMinimumHeight(50)  # ボタンの高さも合わせる
        submit_font = QFont()
        submit_font.setPointSize(14)
        self.submit_button.setFont(submit_font)
        self.submit_button.clicked.connect(self.submit_answer)
        self.answer_input.returnPressed.connect(self.submit_answer)

        answer_layout.addWidget(answer_label)
        answer_layout.addWidget(self.answer_input)
        answer_layout.addWidget(self.submit_button)

        # レイアウトの組み立て
        main_layout.addLayout(header_layout)
        main_layout.addLayout(control_layout)
        main_layout.addLayout(info_layout)
        main_layout.addWidget(hint_container)  # hint_containerを使用
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(answer_layout)
        
        self.setLayout(main_layout)
    
    def start_session(self, mode, question_count):
        """セッションを開始"""
        self.current_mode = mode
        self.session_question_count = question_count
        self.session_current_question = 1  # 最初の問題を1から開始
        self.session_scores = []
        self.session_correct_count = 0
        self.session_is_active = True
        self.session_used_images = set()  # 出題済み画像をリセット
        
        # UI更新
        self.question_counter_label.setText(f"問題：1/{question_count}")
        self.score_label.setText("セッションスコア：0.0点")
        
        # 最初の問題を自動的に読み込む
        self.load_random_image()
    
    def set_mode(self, mode):
        """モードを設定（後方互換性のため）"""
        self.current_mode = mode
        self.session_is_active = False

    def load_image(self):
        """画像を読み込む"""
        if not self.current_mode:
            QMessageBox.warning(self, "警告", "先にモードを選択してください")
            return
        
        # デフォルトでimagesフォルダを開く
        default_dir = os.path.join(os.path.dirname(__file__), "images")
        if not os.path.exists(default_dir):
            default_dir = os.path.dirname(__file__)

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "画像を選択",
            default_dir,
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)",
        )

        if file_path:
            # ゲームエンジンの初期化
            self.game_engine = GameEngine(file_path, self.current_mode, label_loader=self.label_loader)
            self.timer_controller.start()
            self.update_display()
            self.update_timer.start(100)  # 100msごとに更新

    def update_display(self):
        """画面の更新"""
        if not self.game_engine:
            return

        # タイマー更新
        elapsed = self.timer_controller.get_elapsed_time()
        self.time_label.setText(f"経過時間：{elapsed:.1f}s")

        # 画像表示
        processed_image = self.game_engine.get_processed_image(elapsed)
        if processed_image is not None:
            self.display_image(processed_image)

        # 進行度表示
        time_limit = self.game_engine.time_limit
        if time_limit > 0:
            progress = min(1.0, elapsed / time_limit)
        else:
            progress = 1.0

        # プログレスバーで進行度を表示
        self.progress_bar.update_progress(progress)
        
        # ヒント表示を更新（進行度50%を超えた場合のみ表示）
        self.update_hint_display(progress)
    
    def update_hint_display(self, progress=0.0):
        """
        ヒント情報を表示（進行度が50%を超えた場合のみ）
        
        Args:
            progress: 進行度（0.0-1.0）
        """
        if not self.game_engine:
            self.category_label.setText("")
            self.hint_label.setText("")
            return
        
        # 進行度が50%を超えている場合のみヒントを表示
        if progress > 0.5:
            category = self.game_engine.get_category()
            hint = self.game_engine.get_hint()
            
            if category:
                self.category_label.setText(f"カテゴリ: {category}")
            else:
                self.category_label.setText("")
            
            if hint:
                self.hint_label.setText(f"💡 {hint}")
            else:
                self.hint_label.setText("")
        else:
            # 進行度が50%以下の場合はヒントを非表示
            self.category_label.setText("")
            self.hint_label.setText("")

    def display_image(self, image):
        """画像を表示する"""
        if image is None:
            return

        # 念のためメモリの連続性を確保
        if not image.flags["C_CONTIGUOUS"]:
            image = image.copy()

        height, width, channel = image.shape
        bytes_per_line = 3 * width

        q_image = QImage(
            image.data, width, height, bytes_per_line, QImage.Format_RGB888
        )

        # QPixmapに変換して表示
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            self.image_label.contentsRect().size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

    def submit_answer(self):
        """回答を提出"""
        if not self.game_engine:
            QMessageBox.warning(self, "警告", "先に画像を読み込んでください")
            return

        answer = self.answer_input.text().strip()
        if not answer:
            QMessageBox.warning(self, "警告", "回答を入力してください")
            return

        # 経過時間を取得（タイマー停止前に取得する必要がある）
        elapsed = self.timer_controller.get_elapsed_time()
        
        # タイマー停止
        self.timer_controller.stop()
        self.update_timer.stop()

        # 正答判定
        is_correct, correct_answer = self.game_engine.check_answer(answer)

        score = 0.0
        if is_correct:
            score = self.game_engine.calculate_score(elapsed)
            self.session_correct_count += 1
        
        # セッション中の処理
        if self.session_is_active:
            self.session_scores.append(score)
            total_score = sum(self.session_scores)
            
            if is_correct:
                self.score_label.setText(f"セッションスコア：{total_score:.1f}点")
                QMessageBox.information(
                    self, 
                    "正解！", 
                    f"正解です！\nこの問題のスコア：{score:.1f}点\n"
                    f"セッション累計：{total_score:.1f}点"
                )
            else:
                QMessageBox.warning(
                    self, 
                    "不正解", 
                    f"残念！正解は「{correct_answer}」でした。\n"
                    f"セッション累計：{total_score:.1f}点"
                )
            
            # 次の問題へボタンを表示
            if self.session_current_question < self.session_question_count:
                self.next_button.setVisible(True)
                self.load_button.setEnabled(False)
                self.random_button.setEnabled(False)
                self.submit_button.setEnabled(False)
                self.answer_input.setEnabled(False)
            else:
                # セッション終了
                self.end_session()
        else:
            # 通常モード（セッション外）
            if is_correct:
                self.score_label.setText(f"スコア：{score:.1f}点")
                QMessageBox.information(
                    self, "正解！", f"正解です！\nスコア：{score:.1f}点"
                )
            else:
                QMessageBox.warning(
                    self, "不正解", f"残念！正解は「{correct_answer}」でした。"
                )

    def end_session(self):
        """セッションを終了"""
        total_questions = self.session_question_count
        correct_count = self.session_correct_count
        total_score = sum(self.session_scores)
        average_score = total_score / total_questions if total_questions > 0 else 0.0
        accuracy = (correct_count / total_questions * 100) if total_questions > 0 else 0.0
        
        session_stats = {
            'mode': self.current_mode,
            'total_questions': total_questions,
            'correct_count': correct_count,
            'total_score': total_score,
            'average_score': average_score,
            'accuracy': accuracy,
            'scores': self.session_scores
        }
        
        # 結果画面へ遷移
        self.session_complete_signal.emit(session_stats)
    
    def next_question(self):
        """次の問題へ"""
        # ボタンを非表示にして入力可能にする
        self.next_button.setVisible(False)
        self.load_button.setEnabled(True)
        self.random_button.setEnabled(True)
        self.submit_button.setEnabled(True)
        self.answer_input.setEnabled(True)
        
        # セッション中の場合は自動で次の問題を読み込む
        if self.session_is_active and self.session_current_question < self.session_question_count:
            # 次の問題番号に進む
            self.session_current_question += 1
            self.reset_current_question()
            self.load_random_image()
        else:
            # 通常モード
            self.reset_game()
            if self.current_mode:
                self.load_random_image()
    
    def reset_current_question(self):
        """現在の問題をリセット（次の問題用）"""
        self.game_engine = None
        self.timer_controller.reset()
        self.update_timer.stop()
        self.image_label.clear()
        self.image_label.setText("画像がここに表示されます")
        self.answer_input.clear()
        self.time_label.setText("経過時間：00.0s")
        self.progress_bar.setValue(0)
        self.category_label.setText("")
        self.hint_label.setText("")
    
    def reset_game(self):
        """ゲームをリセット"""
        self.game_engine = None
        self.timer_controller.reset()
        self.update_timer.stop()
        self.image_label.clear()
        self.image_label.setText("画像がここに表示されます")
        self.answer_input.clear()
        self.time_label.setText("経過時間：00.0s")
        self.score_label.setText("スコア：---")
        self.progress_bar.setValue(0)
        self.category_label.setText("")
        self.hint_label.setText("")
        
        # セッション情報をリセット
        self.session_is_active = False
        self.session_question_count = 0
        self.session_current_question = 0
        self.session_scores = []
        self.session_correct_count = 0
        self.session_used_images = set()  # 使用済み画像もリセット
        self.question_counter_label.setText("問題：---")
        self.next_button.setVisible(False)
        self.load_button.setEnabled(True)
        self.random_button.setEnabled(True)
        self.submit_button.setEnabled(True)
        self.answer_input.setEnabled(True)

    def load_random_image(self):
        """ランダムに画像を読み込む"""
        if not self.current_mode:
            QMessageBox.warning(self, "警告", "先にモードを選択してください")
            return

        # セッション中の場合は、使用済み画像を除外
        if self.session_is_active:
            all_images = self.dataset_loader.get_all_images()
            available_images = [img for img in all_images if img not in self.session_used_images]
            
            if not available_images:
                # 使用可能な画像がない場合（すべて使用済み）
                QMessageBox.warning(
                    self,
                    "警告",
                    "すべての画像を使用済みです。\n"
                    "セッションをリセットしてください。",
                )
                return
            
            # 使用可能な画像からランダムに選択
            import random
            image_path = random.choice(available_images)
            self.session_used_images.add(image_path)  # 使用済みに追加
        else:
            # セッション外の場合は通常通りランダム選択
            image_path = self.dataset_loader.get_random_image()

        if image_path is None:
            QMessageBox.warning(
                self,
                "警告",
                "imagesフォルダに画像がありません。\n"
                "imagesフォルダに画像ファイルを配置してください。",
            )
            return

        # ゲームエンジンの初期化
        self.game_engine = GameEngine(image_path, self.current_mode, label_loader=self.label_loader)
        self.timer_controller.start()
        self.update_display()
        self.update_timer.start(100)  # 100msごとに更新
        
        # セッション中の場合は問題番号を更新
        if self.session_is_active:
            self.question_counter_label.setText(
                f"問題：{self.session_current_question}/{self.session_question_count}"
            )
    


class MainWindow(QMainWindow):
    """メインウィンドウクラス"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visual Guess Challenge")
        self.resize(1200, 900)  # 1.5倍のサイズ（800×600 → 1200×900）
        self.center_window()

        # 画面遷移用のスタックウィジェット
        self.stacked_widget = QStackedWidget()
        
        # 各画面の作成
        self.home_screen = HomeScreen()
        self.game_setup_screen = GameSetupScreen()
        self.game_screen = GameScreen()
        self.result_screen = ResultScreen()
        
        # スタックに追加
        self.stacked_widget.addWidget(self.home_screen)
        self.stacked_widget.addWidget(self.game_setup_screen)
        self.stacked_widget.addWidget(self.game_screen)
        self.stacked_widget.addWidget(self.result_screen)
        
        # 画面遷移のシグナル接続
        self.home_screen.start_game_signal.connect(self.show_game_setup)
        self.game_setup_screen.session_started_signal.connect(self.start_session)
        self.game_setup_screen.back_to_home_signal.connect(self.show_home)
        self.game_screen.back_to_home_signal.connect(self.show_home)
        self.game_screen.session_complete_signal.connect(self.show_result)
        self.result_screen.back_to_home_signal.connect(self.show_home)
        self.result_screen.restart_signal.connect(self.restart_session)
        
        # 中央ウィジェットに設定
        self.setCentralWidget(self.stacked_widget)
        
        # 初期画面はホーム画面
        self.stacked_widget.setCurrentWidget(self.home_screen)
    
    def show_home(self):
        """ホーム画面を表示"""
        self.stacked_widget.setCurrentWidget(self.home_screen)
        # ゲーム画面をリセット
        self.game_screen.reset_game()
    
    def show_game_setup(self):
        """ゲーム設定画面を表示"""
        self.stacked_widget.setCurrentWidget(self.game_setup_screen)
    
    def start_session(self, mode, question_count):
        """セッションを開始"""
        self.game_screen.start_session(mode, question_count)
        self.stacked_widget.setCurrentWidget(self.game_screen)
    
    def start_game(self, mode):
        """ゲームを開始（後方互換性のため）"""
        self.game_screen.set_mode(mode)
        self.stacked_widget.setCurrentWidget(self.game_screen)
    
    def show_result(self, session_stats):
        """結果画面を表示"""
        self.result_screen.display_results(session_stats)
        self.stacked_widget.setCurrentWidget(self.result_screen)
    
    def restart_session(self, mode):
        """セッションを再開"""
        self.show_game_setup()

    def center_window(self):
        """ウィンドウを画面中央に配置"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


def main():
    """メイン関数"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
