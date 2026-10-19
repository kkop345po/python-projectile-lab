"""斜向拋射 CLI：python main.py --help。"""
import argparse
import json
import sys
from test import calculate_projectile
#CLI command line interface 打指令的意思
#GUI 有個畫面可以點點點的意思

def main(argv=None):
    # 建立指令說明，使用 --help 就能查看。
    parser = argparse.ArgumentParser(
        prog="projectile",
        description="計算斜向拋射的最大高度、水平射程與飛行時間。",
        epilog="假設：忽略空氣阻力，起點與落點等高。範例：python main.py -v 30 -a 45",
    )
    # 設定參數：-v 初速度、-a 角度、-g 重力加速度。
    parser.add_argument("-v", "--velocity", type=float, required=True,
                        metavar="M/S", help="初速度，必須大於 0（m/s）")
    parser.add_argument("-a", "--angle", type=float, required=True,
                        metavar="DEG", help="仰角，範圍 0 到 90 度")
    parser.add_argument("-g", "--gravity", type=float, default=9.81,
                        help="重力加速度，預設 9.81（m/s^2）")
    parser.add_argument("--json", action="store_true", help="輸出 JSON，供其他程式使用")
    parser.add_argument("--version", action="version", version="projectile 1.0.0")
    args = parser.parse_args(argv)  # 讀取使用者輸入的參數。
    # 呼叫計算模組；輸入不合理時顯示錯誤訊息。
    try:
        height, distance, duration = calculate_projectile(args.velocity, args.angle, args.gravity)
    except ValueError as error:
        parser.error(str(error))
    if args.json:
        # JSON 格式方便其他程式讀取。
        print(json.dumps({
            "velocity_m_s": args.velocity, "angle_deg": args.angle,
            "gravity_m_s2": args.gravity, "max_height_m": height,
            "range_m": distance, "flight_time_s": duration,
        }, allow_nan=False, indent=2))
    else:
        # 一般輸出：對齊數字，保留三位小數。
        print("斜向拋射計算結果")
        print("─" * 36)
        print(f"初速度       {args.velocity:>12.3f} m/s")
        print(f"發射仰角     {args.angle:>12.3f} °")
        print(f"重力加速度   {args.gravity:>12.3f} m/s^2")
        print("─" * 36)
        print(f"最大高度 H   {height:>12.3f} m")
        print(f"水平射程 R   {distance:>12.3f} m")
        print(f"飛行時間 T   {duration:>12.3f} s")
        print("\n假設：忽略空氣阻力，起點與落點等高。")
    return 0  # 0 表示程式正常結束。


if __name__ == "__main__":
    # 直接執行此檔案時，才啟動主程式。
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        # 使用者按 Ctrl+C 時結束程式。
        sys.exit(130)

