#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ポケモン レジェンズ Z-A 昼夜切り替え確認スクリプト
→ イベールセンターへ移動して昼夜切り替えを確認
"""

import os
import cv2
import time
from datetime import datetime
from Commands.PythonCommandBase import ImageProcPythonCommand
from Commands.Keys import Button, Hat, Direction

FIELD_ENTER_WAIT = 2.5
USE_IMAGE_CHECK = True

class ZA_DayNightCheck(ImageProcPythonCommand):
    NAME = "ZA_DayNightCheck"

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    FOLDER = os.path.abspath(os.path.join(SCRIPT_DIR, 'LegendsZA'))

    def __init__(self, cam, preview=None):
        super().__init__(cam)

    def log(self, msg):
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] {msg}")

    def debug_log(self, msg):
        self.log(f"[DEBUG] {msg}")

    def press(self, buttons, duration=0.1, wait=0.1):
        self.debug_log(f"Press: {buttons} (dur={duration}, wait={wait})")
        super().press(buttons, duration, wait)

    def pressRep(self, buttons, repeat=1, duration=0.1, interval=0.1, wait=0.1):
        self.debug_log(f"PressRep: {buttons} x{repeat} (dur={duration}, interval={interval}, wait={wait})")
        super().pressRep(buttons, repeat, duration, interval, wait)

    def wait(self, duration):
        self.debug_log(f"Wait: {duration}s")
        super().wait(duration)

    def move_to_ibeeru_center(self):
        """イベールセンターへ移動して椅子に座る"""
        self.log("イベールセンターへ移動")
        self.press(Button.PLUS, 0.2, 0.5)
        self.wait(1.0)
        self.press(Button.Y, 0.2, 0.4)
        self.press(Button.MINUS, 0.2, 1.0)
        for _ in range(2): self.press(Hat.BTM, 0.1, 0.25)
        self.press(Button.A, 0.2, 0.5)
        self.press(Hat.TOP, 0.2, 0.5)
        self.press(Button.A, 0.2, 0.5)
        self.press(Button.A, 0.2, 0.5)
        self.wait(FIELD_ENTER_WAIT)
        self.press(Direction.LEFT, 0.65, 0.5)
        self.press(Direction.UP, 0.25, 0.5)
        for _ in range(6): self.press(Button.A, 0.1, 0.5)
        self.wait(3.0)
        for _ in range(6): self.press(Button.B, 0.1, 0.1)
        self.log("イベールセンター着席完了")
        return True

    def check_current_time(self):
        """現在の時間帯（昼/夜）を確認"""
        day_t = 'LegendsZA/time_day.png'
        night_t = 'LegendsZA/time_night.png'

        self.log("現在の時間帯を確認中...")

        # カメラフレーム取得（リトライ付き）
        max_retries = 5
        frame = None
        for retry in range(max_retries):
            frame = self.camera.readFrame()
            if frame is not None:
                break
            self.log(f"フレーム取得リトライ {retry + 1}/{max_retries}")
            time.sleep(0.5)

        if frame is None:
            self.log("エラー: 画面取得不可")
            return None

        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        except Exception as e:
            self.log(f"エラー: 画像変換失敗 - {e}")
            return None

        # 昼のテンプレートを確認
        day_path = os.path.join(self.FOLDER, day_t)
        day_tmpl = None
        if os.path.exists(day_path):
            try:
                day_tmpl = cv2.imread(day_path, 0)
            except Exception as e:
                self.log(f"エラー: 昼テンプレート読み込み失敗 - {e}")

        # 夜のテンプレートを確認
        night_path = os.path.join(self.FOLDER, night_t)
        night_tmpl = None
        if os.path.exists(night_path):
            try:
                night_tmpl = cv2.imread(night_path, 0)
            except Exception as e:
                self.log(f"エラー: 夜テンプレート読み込み失敗 - {e}")

        # 昼を判定
        day_score = 0.0
        if day_tmpl is not None:
            try:
                res_day = cv2.matchTemplate(gray, day_tmpl, cv2.TM_CCOEFF_NORMED)
                _, day_score, _, _ = cv2.minMaxLoc(res_day)
                self.log(f"昼スコア: {day_score:.3f}")
            except Exception as e:
                self.log(f"エラー: 昼判定失敗 - {e}")

        # 夜を判定
        night_score = 0.0
        if night_tmpl is not None:
            try:
                res_night = cv2.matchTemplate(gray, night_tmpl, cv2.TM_CCOEFF_NORMED)
                _, night_score, _, _ = cv2.minMaxLoc(res_night)
                self.log(f"夜スコア: {night_score:.3f}")
            except Exception as e:
                self.log(f"エラー: 夜判定失敗 - {e}")

        # より高いスコアの方を現在の時間帯とする
        self.log(f"判定結果: 昼={day_score:.3f}, 夜={night_score:.3f}")
        
        if day_score >= night_score:
            self.log("★★★ 昼と判定しました")
            return "day"
        elif night_score > day_score:
            self.log("★★★ 夜と判定しました")
            return "night"
        else:
            self.log("⚠️ 判定不能（スコアが同じか、両方0.0）")
            return None

    def smooth_day_night_change(self, target_time):
        """昼夜切り替えを実行"""
        self.log(f"【昼夜切り替え】目標: {'昼' if target_time=='day' else '夜'}")
        if not self.move_to_ibeeru_center(): return False

        day_t = 'LegendsZA/time_day.png'
        night_t = 'LegendsZA/time_night.png'

        # テンプレートを事前に読み込む
        day_path = os.path.join(self.FOLDER, day_t)
        day_tmpl = None
        if os.path.exists(day_path):
            try:
                day_tmpl = cv2.imread(day_path, 0)
                self.log(f"昼テンプレート読み込み成功: {day_path}")
            except Exception as e:
                self.log(f"エラー: 昼テンプレート読み込み失敗 - {e}")
        else:
            self.log(f"警告: 昼テンプレートが存在しません: {day_path}")

        night_path = os.path.join(self.FOLDER, night_t)
        night_tmpl = None
        if os.path.exists(night_path):
            try:
                night_tmpl = cv2.imread(night_path, 0)
                self.log(f"夜テンプレート読み込み成功: {night_path}")
            except Exception as e:
                self.log(f"エラー: 夜テンプレート読み込み失敗 - {e}")
        else:
            self.log(f"警告: 夜テンプレートが存在しません: {night_path}")

        for attempt in range(6):
            self.press(Direction.DOWN, 0.2); self.wait(0.5)
            for a in range(6):
                self.press(Button.A, 0.1); self.wait(0.65)
                if USE_IMAGE_CHECK:
                    try:
                        # カメラフレーム取得
                        frame = self.camera.readFrame()
                        if frame is None:
                            self.log("  フレーム取得失敗 - リトライ")
                            continue

                        try:
                            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        except Exception as e:
                            self.log(f"  エラー: 画像変換失敗 - {e}")
                            continue

                        # 昼判定
                        day_score = 0.0
                        if day_tmpl is not None:
                            try:
                                res_day = cv2.matchTemplate(gray, day_tmpl, cv2.TM_CCOEFF_NORMED)
                                _, day_score, _, _ = cv2.minMaxLoc(res_day)
                            except Exception as e:
                                self.log(f"  エラー: 昼マッチング失敗 - {e}")

                        # 夜判定
                        night_score = 0.0
                        if night_tmpl is not None:
                            try:
                                res_night = cv2.matchTemplate(gray, night_tmpl, cv2.TM_CCOEFF_NORMED)
                                _, night_score, _, _ = cv2.minMaxLoc(res_night)
                            except Exception as e:
                                self.log(f"  エラー: 夜マッチング失敗 - {e}")

                        self.log(f"  スコア - 昼:{day_score:.3f}, 夜:{night_score:.3f}")
                        
                        if (target_time == "day" and day_score >= 0.98) or (target_time == "night" and night_score >= 0.98):
                            self.log("目標時間帯到達")
                            for _ in range(8): self.press(Button.B, wait=0.68)
                            self.wait(1.8)
                            return True
                    except Exception as e:
                        self.log(f"画像判定エラー: {e}")
                        pass
            self.wait(7.0)
            for _ in range(6): self.press(Button.B, wait=0.8)
        self.wait(20.0)
        for _ in range(8): self.press(Button.B, wait=0.7)
        self.log("昼夜切り替え完了")
        return True

    def do(self):
        self.log("=== ZA 昼夜切り替え確認スクリプト 開始 ===")

        # 1. 現在時刻を表示
        now = datetime.now()
        current_hour = now.hour
        self.log(f"現在時刻: {now.strftime('%H:%M:%S')}")

        # 2. 昼夜判定（6:00-18:00は昼、それ以外は夜）
        target_time = "day" if 6 <= current_hour < 18 else "night"
        self.log(f"判定結果: {'昼' if target_time=='day' else '夜'} を目標にします")

        # 3. 現在の時間帯を確認
        current_time = self.check_current_time()
        if current_time:
            self.log(f"現在の時間帯: {'昼' if current_time=='day' else '夜'}")
            if current_time == target_time:
                self.log("既に目標の時間帯です。切り替え不要です。")
                self.log("=== 操作完了 ===")
                self.finish()
                return
        else:
            self.log("時間帯の判定に失敗しました。切り替えを試みます。")

        # 4. 昼夜切り替えを実行
        self.smooth_day_night_change(target_time)

        # 5. 切り替え後の確認
        self.wait(2.0)
        final_time = self.check_current_time()
        if final_time:
            self.log(f"切り替え後の時間帯: {'昼' if final_time=='day' else '夜'}")
            if final_time == target_time:
                self.log("★★★ 切り替え成功！★★★")
            else:
                self.log("⚠️ 切り替え失敗？目標の時間帯と異なります")
        else:
            self.log("時間帯の判定に失敗しました")

        self.log("=== 操作完了 ===")
        self.finish()
