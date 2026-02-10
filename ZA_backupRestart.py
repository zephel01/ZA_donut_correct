#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ポケモン レジェンズ Z-A　M次元ラッシュ ドーナツ厳選
→ リセット＆復帰操作のみの単独スクリプト
"""

import time
from datetime import datetime
from Commands.PythonCommandBase import ImageProcPythonCommand
from Commands.Keys import Button, Hat

class ZA_ResetOnly(ImageProcPythonCommand):
    NAME = "ZA_BackupRestart"

    def __init__(self, cam, preview=None):
        super().__init__(cam)

    def log(self, msg):
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] {msg}")

    def backupRestart(self):
        self.log("リセット＆復帰開始")
        self.press(Button.HOME, 0.1, 1.5)          # HOMEメニューを開く
        self.press(Button.Y, 0.1, 1.0)             # 「ソフトを終了」選択
        self.press(Button.A, 0.1, 3.0)             # 終了確認
        self.pressRep(Button.A, repeat=6, duration=0.1, interval=0.5)  # 起動時の注意画面など連打
        self.wait(10.0)                            # タイトル画面まで待機
        self.press([Hat.TOP, Button.X, Button.B], 0.2, 1.0)  # セーブデータ選択（上＋X＋B同時押し）
        self.pressRep(Button.A, repeat=12, duration=0.2, interval=0.4)  # ロード完了まで連打
        self.wait(10.0)                            # ゲーム内復帰待機
        self.log("復帰完了")

    def do(self):
        self.log("=== ZA リセット＆復帰スクリプト 開始 ===")
        self.backupRestart()
        self.log("=== 操作完了 ===")
        self.finish()
