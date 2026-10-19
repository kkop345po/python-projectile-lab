"""斜向拋射計算模組，保留原本的求HRT介面。"""
from math import cos, isfinite, radians, sin


def calculate_projectile(velocity: float, angle: float,
                         gravity: float = 9.81) -> tuple[float, float, float]:
    """回傳最大高度（m）、水平射程（m）、飛行時間（s）。"""
    # 檢查數值範圍，排除無限大及無效數值。
    if not isfinite(velocity) or velocity <= 0:
        raise ValueError("初速度必須是大於 0 的有限數值。")
    if not isfinite(angle) or not 0 <= angle <= 90:
        raise ValueError("仰角必須是 0 到 90 度之間的有限數值。")
    if not isfinite(gravity) or gravity <= 0:
        raise ValueError("重力加速度必須是大於 0 的有限數值。")
    theta = radians(angle)  # 三角函數使用弧度，先把角度轉換過去。
    # 將初速度拆成垂直與水平兩個方向。
    vertical = velocity * sin(theta)
    # 90 度是垂直向上，水平速度設為 0，避免浮點誤差。
    horizontal = 0.0 if angle == 90 else velocity * cos(theta)
    # 依序計算飛行時間、最大高度與水平射程。
    duration = (vertical / gravity) * 2
    height = (vertical / gravity) * (vertical / 2)
    distance = horizontal * duration
    # 數值過大時，提醒使用者調整輸入。
    if not all(isfinite(value) for value in (height, distance, duration)):
        raise ValueError("結果超出數值範圍，請縮小初速度或調整重力加速度。")
    return height, distance, duration


def 求HRT(v0, theta):
    """相容原本的呼叫方式：求HRT(30, 45)。"""
    return calculate_projectile(v0, theta)
