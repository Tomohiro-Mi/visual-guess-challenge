"""
ImageProcessor - 画像処理クラス
ぼかし処理、ズーム処理、ハイブリッド処理を担当
"""

import cv2
import numpy as np


class ImageProcessor:
    """画像プロセッサークラス"""

    def __init__(self):
        """初期化"""
        pass

    def apply_blur(self, image, progress):
        """
        progress: 0.0 (開始) -> 1.0 (クリア)
        """
        if image is None:
            return None

        # 進行度を 0.0-1.0 にクリップ
        progress = max(0.0, min(1.0, progress))

        # 最大ぼかし強度 (sigma)
        max_sigma = 30.0

        # 進行度に応じてsigmaを減少 (1.0のとき0になる)
        sigma = max_sigma * (1.0 - progress)

        if sigma <= 0.1:  # ほぼ0なら処理しない
            return image.copy()

        # カーネルサイズをsigmaから計算 (奇数にする必要がある)
        ksize = int(sigma * 6) + 1
        if ksize % 2 == 0:
            ksize += 1

        return cv2.GaussianBlur(image, (ksize, ksize), sigma)

    def apply_zoom(self, image, progress):
        """
        progress: 0.0 (開始) -> 1.0 (クリア)
        アフィン変換を使用してサブピクセル精度で滑らかにズームアウト
        """
        if image is None:
            return None

        height, width = image.shape[:2]
        progress = max(0.0, min(1.0, progress))

        # 最小表示割合 (例: 12.5% = 1/8)
        min_ratio = 0.125

        # 線形補間: min_ratio から 1.0 へ変化
        current_ratio = min_ratio + (1.0 - min_ratio) * progress

        # 中心座標（浮動小数点精度）
        cx = width / 2.0
        cy = height / 2.0

        # アフィン変換を使用して滑らかにズームアウト
        # スケール係数: current_ratioが小さいほど拡大（ズームイン）、大きいほど縮小（ズームアウト）
        # 目標は元画像の中心部分をcurrent_ratioのサイズで切り出して、元サイズに拡大すること
        scale = 1.0 / current_ratio
        
        # アフィン変換行列: 中心を基準に拡大し、出力画像の中心に配置
        # M = [[scale, 0, tx],
        #      [0, scale, ty]]
        # 変換式: dst(x,y) = src(scale*x + tx, scale*y + ty)
        # 中心(cx, cy)が常に出力画像の中心(width/2, height/2)に対応するように設定
        tx = (width / 2.0) - (cx * scale)
        ty = (height / 2.0) - (cy * scale)
        
        M = np.array([[scale, 0, tx],
                      [0, scale, ty]], dtype=np.float32)

        # アフィン変換を適用（サブピクセル精度で滑らかに処理）
        result = cv2.warpAffine(
            image, 
            M, 
            (width, height), 
            flags=cv2.INTER_CUBIC,  # より滑らかな補間
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0)  # はみ出した部分は黒で塗りつぶし
        )
        
        return result

    def apply_hybrid(self, image, progress):
        # ズームとぼかしを組み合わせる
        # 例: ズームは線形に，ぼかしは後半早めに消えるように調整
        zoomed = self.apply_zoom(image, progress)

        # ぼかし用の進行度を少し早める (例: progress 0.8でぼかしゼロ)
        blur_progress = min(1.0, progress * 1.25)
        return self.apply_blur(zoomed, blur_progress)

    def resize_image(self, image, target_width, target_height):
        """
        画像をリサイズ

        Args:
            image: 入力画像
            target_width: 目標幅
            target_height: 目標高さ

        Returns:
            リサイズされた画像
        """
        if image is None:
            return None

        return cv2.resize(
            image, (target_width, target_height), interpolation=cv2.INTER_LINEAR
        )
