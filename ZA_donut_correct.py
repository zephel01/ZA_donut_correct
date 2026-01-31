#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZA ドーナツ厳選 v1.8.13 (Custom Updated)
・Switch1(低速/旧型)/Switch2(高速/有機EL)のタイミング切り替え機能
・サイズ相互互換(CrossSize)機能
・Ball/Kinomi 相互互換(CrossMatch)機能
・「オヤブンLv3」かつ「かがやき(Type不問)Lv3」停止オプション
・画像認識スコアのログ出力機能
・デバッグログによる進行状況の可視化
・固定待機を廃止し、画像認識(result_text.png)による動的待機を実装
・レインボードーナツ（どうぐパワー節約）レシピを追加 (rainbow1/2/3)
・どうぐパワー単独終了オプションを追加 (どっさり不問)
・複数タイプの指定に対応 (例: 'Ghost, Dark')
・ログ表示を整形（複数タイプ指定時の結果をスマートに表示）
・ほかくパワー検知の実装、shiny3レシピ追加
・移動処理の変更(New)
・shiny4レシピを追加 (Update)
・recipe3レシピを追加 (Update)
・デバック機能の修正
"""

import os
import cv2
import numpy as np
import time
from datetime import datetime
from Commands.PythonCommandBase import ImageProcPythonCommand
from Commands.Keys import Button, Hat, Direction

# =============================================================================
# ★★★ [ユーザー設定エリア] 実行前にここを書き換えてください ★★★
# =============================================================================

# 【0. バージョン管理】
VERSION = '1.8.13'

# 【1. レベル/レシピ指定】
#   'shiny1'   : 色違い厳選レシピ1 (節約版)
#   'shiny2'   : 色違い厳選レシピ2 (タンガのみｘ8)
#   'shiny3'   : 色違い厳選レシピ3 (ほかくパワー付与レシピ)
#   'shiny4'   : 色違い厳選レシピ4 (ほかくパワー付与レシピ2 New)
#   'recipe1'  : どうぐパワー節約レシピ
#   'recipe2'  : どうぐパワー重視レシピ/カシブx8
#   'recipe3'  : 節約レシピ recipe3
#   'rainbow1' : バコウ1,ウタン1,ナモ4,ロゼル2
#   'rainbow2' : バコウ1,ヨロギ1,ハバン1,ロゼル5
#   'rainbow3' : ウタン1,ヨロギ1,ナモ4,ロゼル2
SETTING_RECIPE = 'recipe1'

# 【2. ポケモンのタイプ】(shiny系用)
#   ★ 複数指定が可能。カンマ区切りで入力してください。
#   [一覧]: Normal, Fire, Water, Grass, Electric, Ice, Fighting, Poison, Ground,
#           Flying, Psychic, Bug, Rock, Ghost, Dragon, Dark, Steel, Fairy, All
#   例: 'Ghost'
#   例: 'Ghost, Dark, Dragon'
# -----------------------------------------------------------------------------
SETTING_TYPE = 'Dradon'

# 【3. 道具の種類 (クラス)】(recipe/rainbow系用)
#   [一覧]: kinomi, ball, coin, treasure, special, candy
# -----------------------------------------------------------------------------
SETTING_ITEM_CLASS = 'ball'

# 【4. サイズの種類】(shiny系用)
#   [一覧]: oyabun, big, small
# -----------------------------------------------------------------------------
SETTING_SIZE = 'small'

# 【5. パワーの許容レベル】(3=厳選 / 2=妥協)
SETTING_LEVEL_SIZE = 3  # サイズ系 (ちびちび/オヤブン/どっさり)
SETTING_LEVEL_EXTRA = 3 # その他 (かがやき/どうぐ)

# 【6. 詳細設定 (感度・回数・ログ)】
# -----------------------------------------------------------------------------
# 画像認識のしきい値 (0.00 〜 1.00)
SETTING_THRESHOLD_LABEL = 0.75
SETTING_THRESHOLD_ICON  = 0.75
SETTING_THRESHOLD_LEVEL = 0.89
SETTING_THRESHOLD_RESULT = 0.80 # 結果画面検知のしきい値

# 動作設定
SETTING_MAX_LOOP    = 999999
SETTING_RETRY_LIMIT = 2
SETTING_DEBUG_LOG   = True # デバッグログをデフォルトで有効化

# 【7. クロス判定設定 (互換/妥協機能)】
# -----------------------------------------------------------------------------
# (A) Ball <-> Kinomi 相互互換 (recipeモード用)
# どっさりLv2以上指定時に、サブパワーがLv3なら相互互換で妥協採用する機能
SETTING_CROSS_MATCH = True

# (B) サイズ相互互換 (shinyモード用)
# 指定のタイプ(かがやきLv3)が出た時、サイズが違っても以下の設定がTrueなら採用(Lv3限定)
# True/False
SETTING_CROSS_SIZE_OYABUN = False  # オヤブンを許容するか
SETTING_CROSS_SIZE_BIG    = False   # でかでか(Big)を許容するか
SETTING_CROSS_SIZE_SMALL  = True  # ちびちび(Small)を許容するか

# (C) タイプ不問オヤブン終了オプション
# ターゲットのタイプと違っても、「オヤブンLv3」かつ「かがやき(タイプ不問)Lv3」なら終了する
# True/False
SETTING_STOP_ON_ANY_TYPE_OYABUN = False

# (D) どうぐパワー単独終了オプション (どっさり不問)
# 指定したどうぐパワー(きのみ等)が条件(Lv3/Lv2)を満たせば、どっさりパワーの結果に関わらず終了する
# recipe/rainbowモードでのみ有効
# True/False
SETTING_STOP_ON_TOOL_ONLY = False

# 【8. 動作タイミング設定 (switch1/switch2)】
# switch1: 旧型/Liteなど読み込みが遅い場合 (待機長め・ボタン連打多め)
# switch2: 有機ELなど読み込みが速い場合 (待機短め・最適化)
SETTING_TIMING_MODE = 'switch2'

# 【9. ほかくパワー検知オプション】(shiny系モードでのみ有効)
# -----------------------------------------------------------------------------
# ほかくパワー検知を利用するか
SETTING_ENABLE_CAPTURE_POWER = False

# ほかくパワーの目標レベル (3=厳選 / 2=妥協 / 1=さらに妥協)
# かがやきパワーと同じレベル指定でOK（共通利用）
SETTING_LEVEL_CAPTURE = 1  # 1, 2, 3 のいずれか

# ほかくパワー妥協オプション
# Trueの場合：かがやきパワーが「ぜんぶ」(Type_All)かつ指定Lv以上で、
#            ほかくパワーのタイプが「かがやきターゲットタイプ」に含まれていれば採用
SETTING_CAPTURE_COMPROMISE = True

# =============================================================================
# ▲▲▲ 設定エリアここまで ▲▲▲
# =============================================================================

# --- 設定値の読み込み処理 ---
ENV_RECIPE = os.environ.get('RECIPE', os.environ.get('MODE', SETTING_RECIPE)).lower()
INPUT_TYPE_RAW = os.environ.get('TYPE', SETTING_TYPE)

# 複数タイプ対応：カンマ区切りをリスト化し、空白除去・Capitalize
TARGET_TYPES = [t.strip().capitalize() for t in INPUT_TYPE_RAW.split(',') if t.strip()]
TARGET_TYPE_Display = "/".join(TARGET_TYPES)

SIZE = os.environ.get('SIZE', SETTING_SIZE).lower()
INPUT_ITEM_CLASS = os.environ.get('ITEM_CLASS', SETTING_ITEM_CLASS).lower()

# タイミングモード設定
TIMING_MODE = os.environ.get('TIMING_MODE', SETTING_TIMING_MODE).lower()
if TIMING_MODE not in ['switch1', 'switch2']:
    print(f"[Warning] Unknown TIMING_MODE '{TIMING_MODE}'. Fallback to 'switch2'.")
    TIMING_MODE = 'switch2'

# レベル設定
try:
    SIZE_LEVEL_REQ = int(os.environ.get('SIZE_LEVEL', str(SETTING_LEVEL_SIZE)))
except:
    SIZE_LEVEL_REQ = 3

try:
    EXTRA_LEVEL_REQ = int(os.environ.get('EXTRA_LEVEL', str(SETTING_LEVEL_EXTRA)))
except:
    EXTRA_LEVEL_REQ = 3

# 詳細設定
THRESHOLD_LABEL = float(os.environ.get('THRESHOLD_LABEL', SETTING_THRESHOLD_LABEL))
THRESHOLD_ICON  = float(os.environ.get('THRESHOLD_ICON', SETTING_THRESHOLD_ICON))
THRESHOLD_LEVEL = float(os.environ.get('THRESHOLD_LEVEL', SETTING_THRESHOLD_LEVEL))
THRESHOLD_RESULT = float(os.environ.get('THRESHOLD_RESULT', SETTING_THRESHOLD_RESULT))

MAX_LOOP    = int(os.environ.get('MAX_LOOP', SETTING_MAX_LOOP))
RETRY_LIMIT = int(os.environ.get('RETRY_LIMIT', SETTING_RETRY_LIMIT))
DEBUG_LOG_STR = os.environ.get('DEBUG_LOG', str(SETTING_DEBUG_LOG)).lower()
DEBUG_LOG   = True if DEBUG_LOG_STR == 'true' else False

# --- クロス機能の設定読み込み ---
ENABLE_CROSS_MATCH = True if os.environ.get('ENABLE_CROSS_MATCH', str(SETTING_CROSS_MATCH)).lower() == 'true' else False
ENABLE_CROSS_OYABUN = True if os.environ.get('ENABLE_CROSS_SIZE_OYABUN', str(SETTING_CROSS_SIZE_OYABUN)).lower() == 'true' else False
ENABLE_CROSS_BIG = True if os.environ.get('ENABLE_CROSS_SIZE_BIG', str(SETTING_CROSS_SIZE_BIG)).lower() == 'true' else False
ENABLE_CROSS_SMALL = True if os.environ.get('ENABLE_CROSS_SIZE_SMALL', str(SETTING_CROSS_SIZE_SMALL)).lower() == 'true' else False
ENABLE_ANY_TYPE_OYABUN = True if os.environ.get('ENABLE_ANY_TYPE_OYABUN', str(SETTING_STOP_ON_ANY_TYPE_OYABUN)).lower() == 'true' else False
ENABLE_TOOL_ONLY_STOP = True if os.environ.get('ENABLE_TOOL_ONLY', str(SETTING_STOP_ON_TOOL_ONLY)).lower() == 'true' else False

# --- ほかくパワー設定読み込み ---
ENABLE_CAPTURE_POWER = True if os.environ.get('ENABLE_CAPTURE_POWER', str(SETTING_ENABLE_CAPTURE_POWER)).lower() == 'true' else False

try:
    CAPTURE_LEVEL_REQ = int(os.environ.get('CAPTURE_LEVEL', str(SETTING_LEVEL_CAPTURE)))
except:
    CAPTURE_LEVEL_REQ = 3

ENABLE_CAPTURE_COMPROMISE = True if os.environ.get('ENABLE_CAPTURE_COMPROMISE', str(SETTING_CAPTURE_COMPROMISE)).lower() == 'true' else False

# 有効性チェック
valid_recipes = ['recipe1', 'recipe2', 'recipe3', 'shiny1', 'shiny2', 'shiny3', 'shiny4', 'rainbow1', 'rainbow2', 'rainbow3']
if ENV_RECIPE not in valid_recipes:
    if 'shiny' in ENV_RECIPE:
        if '4' in ENV_RECIPE: ENV_RECIPE = 'shiny4'
        elif '3' in ENV_RECIPE: ENV_RECIPE = 'shiny3'
        elif '1' in ENV_RECIPE: ENV_RECIPE = 'shiny1'
        else: ENV_RECIPE = 'shiny2'
    elif 'rainbow' in ENV_RECIPE:
        if '2' in ENV_RECIPE: ENV_RECIPE = 'rainbow2'
        elif '3' in ENV_RECIPE: ENV_RECIPE = 'rainbow3'
        else: ENV_RECIPE = 'rainbow1'
    elif '2' in ENV_RECIPE:
        ENV_RECIPE = 'recipe2'
    else:
        ENV_RECIPE = 'recipe1'
    print(f"[System] Mode Adjusted -> {ENV_RECIPE}")

valid_sizes = ['oyabun', 'big', 'small']
if SIZE not in valid_sizes:
    SIZE = 'oyabun'

# 判定用リスト生成関数
def get_target_levels(req_lvl):
    targets = []
    if req_lvl <= 3: targets.append('lv3')
    if req_lvl <= 2: targets.append('lv2')
    if req_lvl <= 1: targets.append('lv1')
    return targets

TARGETS_SIZE = get_target_levels(SIZE_LEVEL_REQ)
TARGETS_EXTRA = get_target_levels(EXTRA_LEVEL_REQ)
TARGETS_CAPTURE = get_target_levels(CAPTURE_LEVEL_REQ)

CAPTURE_DIR = "debug_captures"
os.makedirs(CAPTURE_DIR, exist_ok=True)

# --- コマンド名(NAME)の動的生成 ---
if 'shiny' in ENV_RECIPE:
    CMD_NAME_SUFFIX = f"({ENV_RECIPE.capitalize()}/Type=[{TARGET_TYPE_Display}]/{SIZE})"
else:
    CMD_NAME_SUFFIX = f"({ENV_RECIPE.capitalize()}/{INPUT_ITEM_CLASS})"

class ZA_DonutV188(ImageProcPythonCommand):
    NAME = f"ZA ドーナツ厳選 {CMD_NAME_SUFFIX} v{VERSION}"

    THRESHOLD_LABEL = THRESHOLD_LABEL
    THRESHOLD_ICON  = THRESHOLD_ICON
    THRESHOLD_LEVEL = THRESHOLD_LEVEL
    THRESHOLD_RESULT = THRESHOLD_RESULT
    
    MAX_LOOP = MAX_LOOP
    RETRY_LIMIT = RETRY_LIMIT
    DEBUG_LOG = DEBUG_LOG

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    FOLDER = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../Template/LegendsZA'))

    def __init__(self, cam, preview=None):
        super().__init__(cam)
        self.count = 0
        self.templates = {}
        self.cross_icon_key = None 
        self._load_templates()

    def log(self, msg):
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] [{self.count:05d}] {msg}")

    def debug_log(self, msg):
        if self.DEBUG_LOG:
            self.log(f"[CMD] {msg}")

    def press(self, buttons, duration=0.1, wait=0.1):
        self.debug_log(f"Press: {buttons} (dur={duration}, wait={wait})")
        super().press(buttons, duration, wait)

    def pressRep(self, buttons, repeat=1, duration=0.1, interval=0.1, wait=0.1):
        self.debug_log(f"PressRep: {buttons} x{repeat} (dur={duration}, interval={interval}, wait={wait})")
        super().pressRep(buttons, repeat, duration, interval, wait)

    def wait(self, duration):
        self.debug_log(f"Wait: {duration}s")
        super().wait(duration)

    def _load_templates(self):
        # テンプレート読み込み処理
        files = {
            'dosari_label':   'dosari_label.png',
            'lv2': 'lv2.png',
            'lv3': 'lv3.png',
            'result_text': 'result_text.png'
        }
        if 'shiny' in ENV_RECIPE:
            files['shiny_label'] = 'shiny_label.png'
            files['type_all'] = 'Type_All.png'
            files['lbl_oyabun'] = 'oyabun_label.png'
            files['lbl_big']    = 'big2_label.png'
            files['lbl_small']  = 'small2_label.png'
            
            # --- 複数タイプのアイコン読み込み ---
            for t_name in TARGET_TYPES:
                key = f"target_icon_{t_name}"
                files[key] = f"Type_{t_name}.png"

            if SIZE == 'big':     files['size_label'] = 'big2_label.png'
            elif SIZE == 'small': files['size_label'] = 'small2_label.png'
            else:                 files['size_label'] = 'oyabun_label.png'
            
            # ほかくパワー関連テンプレート
            if ENABLE_CAPTURE_POWER:
                files['capture_label'] = 'capture_label.png'
                files['type_all2'] = 'Type_All2.png'  # 「すべて」のアイコン
        else:
            files['tool_label'] = 'tool_label.png'
            files['target_icon'] = f"class_{INPUT_ITEM_CLASS}.png"

        print(f"[System] Version: {VERSION}")
        print(f"[System] Recipe: {ENV_RECIPE}")
        print(f"[System] Timing Mode: {TIMING_MODE}")
        
        if 'shiny' in ENV_RECIPE:
            print(f"[System] Target: {ENV_RECIPE} + Type=[{TARGET_TYPE_Display}] + {SIZE}")
            print(f"[System] AnyTypeOyabunStop: {ENABLE_ANY_TYPE_OYABUN}")
            if ENABLE_CAPTURE_POWER:
                print(f"[System] CapturePower: Enabled (Lv={CAPTURE_LEVEL_REQ}, Compromise={ENABLE_CAPTURE_COMPROMISE})")
        else:
            print(f"[System] Target: Tool({INPUT_ITEM_CLASS}) + Dosari")
            print(f"[System] ToolOnlyStop: {ENABLE_TOOL_ONLY_STOP}")
            
        for key, filename in files.items():
            path = os.path.join(self.FOLDER, filename)
            if os.path.exists(path):
                self.templates[key] = cv2.imread(path, 0)
            else:
                self.templates[key] = None
        
        if self.templates.get('result_text') is None:
            print("[Warning] 'result_text.png' not found. Fallback to fixed timing.")

        if ENABLE_CROSS_MATCH and 'shiny' not in ENV_RECIPE:
            c_fname = None
            if INPUT_ITEM_CLASS == 'ball':
                c_fname = 'class_kinomi.png'
                self.cross_icon_key = 'cross_kinomi'
            elif INPUT_ITEM_CLASS == 'kinomi':
                c_fname = 'class_ball.png'
                self.cross_icon_key = 'cross_ball'
            if c_fname:
                path = os.path.join(self.FOLDER, c_fname)
                if os.path.exists(path):
                    self.templates[self.cross_icon_key] = cv2.imread(path, 0)

    def save_capture(self, prefix="check"):
        filename = f"{CAPTURE_DIR}/{prefix}_{self.count:05d}_{int(time.time())}.png"
        try:
            frame = self.camera.readFrame()
            if frame is not None:
                cv2.imwrite(filename, frame)
        except:
            pass

    def wait_for_result_screen(self, timeout=5.0):
        if self.templates.get('result_text') is None:
            self.debug_log("Result template missing. Using fixed wait (1.0s).")
            self.wait(1.0)
            return

        self.debug_log("Waiting for result screen (Image Detection)...")
        start_time = time.time()
        max_score_seen = 0.0
        
        while time.time() - start_time < timeout:
            frame = self.camera.readFrame()
            if frame is not None:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                res = cv2.matchTemplate(gray, self.templates['result_text'], cv2.TM_CCOEFF_NORMED)
                _, score, _, _ = cv2.minMaxLoc(res)
                
                if score > max_score_seen:
                    max_score_seen = score
                
                if score > self.THRESHOLD_RESULT:
                    self.debug_log(f"Result screen detected! Score: {score:.2f}")
                    return
            
            self.wait(0.2)
            
        self.log(f"Warning: Result detection timed out. Max score: {max_score_seen:.2f}")

    def detect_power_level(self, gray_screen, label_key, target_levels, roi_width_override=None):
        label_tmpl = self.templates.get(label_key)
        if label_tmpl is None: return None, 0.0
        res = cv2.matchTemplate(gray_screen, label_tmpl, cv2.TM_CCOEFF_NORMED)
        _, score, _, loc = cv2.minMaxLoc(res)
        if score < self.THRESHOLD_LABEL: return None, score
        h, w = gray_screen.shape[:2]
        tw, th = label_tmpl.shape[::-1]
        roi_w = roi_width_override if roi_width_override else 180
        roi_y_start = max(0, loc[1] - 10)
        roi_y_end   = min(h, loc[1] + th + 10)
        roi_x_start = loc[0] + tw
        roi_x_end   = min(w, roi_x_start + roi_w)
        roi_img = gray_screen[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
        best_lvl, best_score = self._detect_level_in_roi(roi_img, target_levels)
        return best_lvl, best_score

    def detect_power_icon_level(self, gray_screen, label_key, icon_key, target_levels, backup_icon_key=None):
        label_tmpl = self.templates.get(label_key)
        if label_tmpl is None: return None, 0.0
        res = cv2.matchTemplate(gray_screen, label_tmpl, cv2.TM_CCOEFF_NORMED)
        _, l_score, _, loc = cv2.minMaxLoc(res)
        if l_score < self.THRESHOLD_LABEL: return None, l_score
        h, w = gray_screen.shape[:2]
        tw, th = label_tmpl.shape[::-1]
        roi_y_start = max(0, loc[1] - 10)
        roi_y_end   = min(h, loc[1] + th + 10)
        roi_x_start = loc[0] + tw
        roi_x_end   = min(w, roi_x_start + 250)
        roi_img = gray_screen[roi_y_start:roi_y_end, roi_x_start:roi_x_end]
        icon_matched = False
        t_score = 0.0
        icon_tmpl = self.templates.get(icon_key)
        if icon_tmpl is not None:
            res_t = cv2.matchTemplate(roi_img, icon_tmpl, cv2.TM_CCOEFF_NORMED)
            _, t_score, _, _ = cv2.minMaxLoc(res_t)
            if t_score >= self.THRESHOLD_ICON: icon_matched = True
        
        if not icon_matched and backup_icon_key:
            backup_tmpl = self.templates.get(backup_icon_key)
            if backup_tmpl is not None:
                res_b = cv2.matchTemplate(roi_img, backup_tmpl, cv2.TM_CCOEFF_NORMED)
                _, b_score, _, _ = cv2.minMaxLoc(res_b)
                if b_score >= self.THRESHOLD_ICON:
                    icon_matched = True
                    t_score = b_score
        
        if not icon_matched: return None, t_score
        best_lvl, best_lvl_score = self._detect_level_in_roi(roi_img, target_levels)
        return best_lvl, best_lvl_score

    def _detect_level_in_roi(self, roi_img, target_levels):
        rh, rw = roi_img.shape[:2]
        best_lvl = None
        best_lvl_score = 0.0
        for lvl_key in target_levels:
            lvl_tmpl = self.templates.get(lvl_key)
            if lvl_tmpl is None: continue
            lth, ltw = lvl_tmpl.shape[:2]
            if rh < lth or rw < ltw: continue
            res_l = cv2.matchTemplate(roi_img, lvl_tmpl, cv2.TM_CCOEFF_NORMED)
            _, l_score, _, _ = cv2.minMaxLoc(res_l)
            if l_score > best_lvl_score:
                best_lvl_score = l_score
                if l_score > self.THRESHOLD_LEVEL: best_lvl = lvl_key
        return best_lvl, best_lvl_score

    def makeDonut(self):
        self.log(f"ドーナツ作成開始 ({TIMING_MODE})")

        if TIMING_MODE == 'switch1':
            self.debug_log("Step1: Open Picnic Menu (Switch1)")
            self.press(Button.PLUS, 0.2, 0.5)
            self.wait(1.0)
            self.press(Button.Y, 0.2, 0.4)
            self.pressRep(Hat.BTM, repeat=3, duration=0.1, interval=0.1)
            self.press(Button.A, 0.2, 0.4)
            self.press(Button.A, 0.2, 0.6)
            self.press(Button.A, 0.2, 0.4)
            self.press(Button.A, 0.2, 0.6)
            
            self.debug_log("Step2: Loading Ingredients...")
            self.wait(8.0)
    
            self.debug_log("Step3: Selecting Ingredients")
            self.press(Direction.UP, 2.0)
            self.wait(1.5)
            self.press(Button.A, 0.2, 0.4)
            self.wait(7.0)
            self.press(Direction.UP, 2.5)
            self.press(Direction.LEFT, 0.5)
            self.wait(1.6)
            self.press(Button.A, 0.2, 0.5)
            self.press(Button.A, 0.2, 0.5)
            self.press(Button.A, 0.2, 0.5)
            self.wait(3.0)

        else:
            self.debug_log("Step1: Open Picnic Menu (Switch2)")
            self.press(Button.PLUS, 0.2, 0.5)
            self.wait(1.0)
            self.press(Button.Y, 0.2, 0.4)
            self.pressRep(Hat.BTM, repeat=3, duration=0.1, interval=0.1)
            self.press(Button.A, 0.2, 0.4)
            self.press(Button.A, 0.2, 0.6)
            
            self.debug_log("Step2: Loading Ingredients...")
            self.wait(2.6)
            
            self.debug_log("Step3: Selecting Ingredients")
            self.press(Button.Y, 0.2, 0.5)
            self.wait(0.5)
            self.press(Button.A, 0.2, 0.5)
            self.wait(3.6)
            self.pressRep(Button.Y, repeat=2, duration=0.1, interval=0.7)
            self.wait(0.2)
            self.press(Direction.LEFT, 0.5)
            self.wait(0.6)
            self.press(Button.A, 0.2, 0.5)
            self.press(Button.A, 0.2, 0.5)
            self.press(Button.A, 0.2, 0.5)


        self.debug_log("Step4: Input Recipe")
        self._input_recipe()

        self.debug_log("Step5: Start Cooking")
        self.press(Button.PLUS, 0.2, 0.5)

        self.debug_log("Step6: Skipping Movie...")
        self.pressRep(Button.A, repeat=4, duration=0.1, interval=0.5)

        self.debug_log("Step7: Wait 3.0s (Result)")
        self.wait(3.0)
        self.debug_log("Step8: Button.A")
        self.press(Button.A, 0.2, 0.5)

        self.debug_log("Step9: Waiting for Result Screen...")
        self.wait_for_result_screen(timeout=5.0)

        self.wait(2.0)

    def _input_recipe(self):
        if ENV_RECIPE == 'shiny1':
            self.log(f"レシピ入力: {ENV_RECIPE}")
            self.pressRep(Hat.TOP, repeat=5, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=4, duration=0.1, interval=0.1)
            self.pressRep(Hat.TOP, repeat=3, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=4, duration=0.1, interval=0.1)

        elif ENV_RECIPE == 'shiny2':
            self.log(f"レシピ入力: {ENV_RECIPE}")
            self.pressRep(Hat.TOP, repeat=8, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=8, duration=0.1, interval=0.1)

        elif ENV_RECIPE == 'shiny3':
            self.log(f"レシピ入力: {ENV_RECIPE}")
            self.pressRep(Hat.TOP, repeat=5, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=6, duration=0.1, interval=0.1)
            self.pressRep(Hat.TOP, repeat=3, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=2, duration=0.1, interval=0.1)

        elif ENV_RECIPE == 'shiny4':
            self.log(f"レシピ入力: {ENV_RECIPE}")
            self.pressRep(Hat.TOP, repeat=5, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=6, duration=0.1, interval=0.1)
            self.pressRep(Hat.TOP, repeat=4, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=1, duration=0.1, interval=0.1)
            self.pressRep(Hat.TOP, repeat=5, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=1, duration=0.1, interval=0.1)

        elif ENV_RECIPE == 'recipe1':
            self.log(f"レシピ入力: {ENV_RECIPE}")
            self.pressRep(Hat.TOP, repeat=1, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=3, duration=0.1, interval=0.1)
            self.pressRep(Hat.TOP, repeat=2, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=1, duration=0.1, interval=0.1)
            self.pressRep(Hat.TOP, repeat=3, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=4, duration=0.1, interval=0.1)

        elif ENV_RECIPE == 'recipe2':
            self.log(f"レシピ入力: {ENV_RECIPE}")
            self.pressRep(Hat.TOP, repeat=6, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=8, duration=0.1, interval=0.1)

        elif ENV_RECIPE == 'recipe3':
            self.log(f"レシピ入力: {ENV_RECIPE}")
            self.pressRep(Hat.TOP, repeat=1, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=1, duration=0.1, interval=0.1)
            self.pressRep(Hat.TOP, repeat=2, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=4, duration=0.1, interval=0.1)
            self.pressRep(Hat.TOP, repeat=1, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=3, duration=0.1, interval=0.1)

        elif ENV_RECIPE == 'rainbow1':
            self.log(f"レシピ入力: {ENV_RECIPE}")
            self.pressRep(Hat.TOP, repeat=1, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=2, duration=0.1, interval=0.1)
            self.pressRep(Hat.TOP, repeat=3, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=4, duration=0.1, interval=0.1)
            self.pressRep(Hat.TOP, repeat=5, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=1, duration=0.1, interval=0.1)
            self.pressRep(Hat.TOP, repeat=1, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=1, duration=0.1, interval=0.1)

        elif ENV_RECIPE == 'rainbow2':
            self.log(f"レシピ入力: {ENV_RECIPE}")
            self.pressRep(Hat.TOP, repeat=1, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=5, duration=0.1, interval=0.1)
            self.pressRep(Hat.TOP, repeat=4, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=1, duration=0.1, interval=0.1)
            self.pressRep(Hat.TOP, repeat=2, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=1, duration=0.1, interval=0.1)
            self.pressRep(Hat.TOP, repeat=3, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=1, duration=0.1, interval=0.1)

        elif ENV_RECIPE == 'rainbow3':
            self.log(f"レシピ入力: {ENV_RECIPE}")
            self.pressRep(Hat.TOP, repeat=1, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=2, duration=0.1, interval=0.1)
            self.pressRep(Hat.TOP, repeat=3, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=4, duration=0.1, interval=0.1)
            self.pressRep(Hat.TOP, repeat=3, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=1, duration=0.1, interval=0.1)
            self.pressRep(Hat.TOP, repeat=2, duration=0.05, interval=0.1)
            self.pressRep(Button.A, repeat=1, duration=0.1, interval=0.1)

    def retry_creation(self):
        self.log(f"リトライ操作実行 ({TIMING_MODE})")
        self.press(Button.A, 0.2, 0.5)
        
        if TIMING_MODE == 'switch1':
            self.wait(1.0)
            self.press(Hat.BTM, 0.1, 0.1)
            self.press(Button.A, 0.2, 0.5)
            self.debug_log("Wait 6.0s (Refresh)")
            self.wait(6.0)
        else:
            self.wait(0.5)
            self.press(Hat.BTM, 0.1, 0.1)
            self.press(Button.A, 0.2, 0.5)
            self.debug_log("Wait 4.0s (Refresh)")
            self.wait(4.0)

    def backupRestart(self):
        self.log(f"リセットシーケンス ({TIMING_MODE})")
        
        self.press(Button.HOME, 0.1, 1.5)
        self.press(Button.Y, 0.1, 1.0)
        self.press(Button.A, 0.1, 3.0)
        self.pressRep(Button.A, repeat=6, interval=0.5)
        
        if TIMING_MODE == 'switch1':
            self.wait(17.0)
        else:
            self.wait(10.0)

        self.press([Hat.TOP, Button.X, Button.B], 0.2, 1.0)
        self.pressRep(Button.A, repeat=12, interval=0.4)
        
        if TIMING_MODE == 'switch1':
            self.wait(15.0)
        else:
            self.wait(10.0)

    def checkDonutResult(self):
        self.save_capture("BEFORE")
        frame = self.camera.readFrame()
        if frame is None:
            self.log("エラー: 画面取得不可")
            return False
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        l1_n = "Power1"
        res1_lvl = None
        s1 = 0.0

        if 'shiny' in ENV_RECIPE:
            l1_n = f"Size({SIZE})"
            res1_lvl, s1 = self.detect_power_level(gray, 'size_label', TARGETS_SIZE)
        else:
            l1_n = "どっさり"
            res1_lvl, s1 = self.detect_power_level(gray, 'dosari_label', TARGETS_SIZE)

        str1 = res1_lvl if res1_lvl else "なし"

        l2_n = "Power2"
        res2_lvl = None
        s2 = 0.0
        matched_type_name = None
        
        if 'shiny' in ENV_RECIPE:
            # 複数タイプ対応ロジック
            max_fail_score = 0.0
            
            # 1. 指定リストのタイプを走査
            for t_name in TARGET_TYPES:
                key = f"target_icon_{t_name}"
                lvl, score = self.detect_power_icon_level(gray, 'shiny_label', key, TARGETS_EXTRA)
                
                if score > max_fail_score:
                    max_fail_score = score

                if lvl is not None:
                    res2_lvl = lvl
                    s2 = score
                    matched_type_name = t_name
                    break
            
            # 2. 指定タイプでヒットしなければ「Type_All」をチェック
            if res2_lvl is None:
                lvl, score = self.detect_power_icon_level(gray, 'shiny_label', 'type_all', TARGETS_EXTRA)
                if score > max_fail_score:
                    max_fail_score = score
                    
                if lvl is not None:
                    res2_lvl = lvl
                    s2 = score
                    matched_type_name = "All"

            # ログ表示名の生成
            if matched_type_name:
                # ヒット時: そのタイプだけ表示
                l2_n = f"かがやき({matched_type_name})"
            else:
                # 失敗時: ターゲット一覧を表示 (スコアは最大のもの)
                l2_n = f"かがやき({TARGET_TYPE_Display})"
                s2 = max_fail_score
            
        else:
            l2_n = f"どうぐ({INPUT_ITEM_CLASS})"
            res2_lvl, s2 = self.detect_power_icon_level(
                gray, 'tool_label', 'target_icon', TARGETS_EXTRA
            )

        if ENABLE_CROSS_MATCH and ('shiny' not in ENV_RECIPE) and \
           (res1_lvl is not None) and (res2_lvl is None) and (self.cross_icon_key is not None):
            cross_targets = ['lv3']
            l2_cross_n = f"Cross({self.cross_icon_key})"
            self.debug_log(f"Checking ItemCross: {l2_cross_n}...")
            c_lvl, c_score = self.detect_power_icon_level(
                gray, 'tool_label', self.cross_icon_key, cross_targets
            )
            if c_lvl is not None:
                self.log(f"★ ItemCross成功: {l2_cross_n} {c_lvl} ({c_score:.2f})")
                res2_lvl = c_lvl
                s2 = c_score
                l2_n += f" -> {l2_cross_n}"

        if 'shiny' in ENV_RECIPE and (res2_lvl is not None) and (res1_lvl is None):
            cross_size_candidates = []
            if ENABLE_CROSS_OYABUN: cross_size_candidates.append(('lbl_oyabun', 'Oyabun'))
            if ENABLE_CROSS_BIG:    cross_size_candidates.append(('lbl_big',    'Big'))
            if ENABLE_CROSS_SMALL:  cross_size_candidates.append(('lbl_small',  'Small'))
            
            if cross_size_candidates:
                self.debug_log(f"Checking SizeCross candidates...")
                cross_targets = ['lv3']
                for lbl_key, lbl_name in cross_size_candidates:
                    cs_lvl, cs_score = self.detect_power_level(gray, lbl_key, cross_targets)
                    if cs_lvl is not None:
                        self.log(f"★ SizeCross成功: {lbl_name} {cs_lvl} ({cs_score:.2f})")
                        res1_lvl = cs_lvl
                        s1 = cs_score
                        l1_n += f" -> Cross({lbl_name})"
                        break

        any_type_success = False
        if ENABLE_ANY_TYPE_OYABUN and 'shiny' in ENV_RECIPE:
            if (res1_lvl is None or res2_lvl is None):
                self.debug_log("Checking AnyType + Oyabun Lv3 condition...")
                oya_lvl, oya_score = self.detect_power_level(gray, 'lbl_oyabun', ['lv3'])
                if oya_lvl == 'lv3':
                    sparkle_any_lvl, spa_score = self.detect_power_level(
                        gray, 'shiny_label', ['lv3'], roi_width_override=280
                    )
                    if sparkle_any_lvl == 'lv3':
                        self.log(f"★ 特別終了条件: オヤブンLv3({oya_score:.2f}) & かがやき(Type不問)Lv3({spa_score:.2f}) を検知しました")
                        any_type_success = True
                        res1_lvl = 'lv3'
                        res2_lvl = 'lv3'
                        l1_n = "オヤブン"
                        l2_n = "かがやき(Any)"

        # === ほかくパワー検知（shinyモードかつ有効時のみ）===
        res3_lvl = None
        s3 = 0.0
        l3_n = "ほかく"
        capture_matched_type = None

        if 'shiny' in ENV_RECIPE and ENABLE_CAPTURE_POWER:
            # まず「すべて」(Type_All2)をチェック
            res3_lvl, s3 = self.detect_power_icon_level(gray, 'capture_label', 'type_all2', TARGETS_CAPTURE)
            if res3_lvl is not None:
                capture_matched_type = "All2"  # 「すべて」
                l3_n = "ほかく(すべて)"

            # 「すべて」でなければ個別タイプをチェック
            if res3_lvl is None:
                for t_name in TARGET_TYPES:
                    key = f"target_icon_{t_name}"
                    lvl, score = self.detect_power_icon_level(gray, 'capture_label', key, TARGETS_CAPTURE)
                    if lvl is not None:
                        res3_lvl = lvl
                        s3 = score
                        capture_matched_type = t_name
                        l3_n = f"ほかく({t_name})"
                        break

            str3 = res3_lvl if res3_lvl else "なし"
            self.log(f"判定: {l3_n}[{str3}]({s3:.2f})")

        # === ほかくパワー妥協ロジック ===
        capture_compromise_success = False
        if ENABLE_CAPTURE_COMPROMISE and 'shiny' in ENV_RECIPE and ENABLE_CAPTURE_POWER:
            # 条件：かがやきが「ぜんぶ」(All)かつ目標レベル以上
            if matched_type_name == "All" and res2_lvl in [t.upper() for t in TARGETS_EXTRA]:  # 'lv2' -> 'LV2' など調整が必要なら
                # ほかくパワーがターゲットタイプのいずれかに該当すればOK
                if capture_matched_type in TARGET_TYPES:
                    self.log(f"★ ほかくパワー妥協成功: かがやき(ぜんぶ){res2_lvl} + ほかく({capture_matched_type}){res3_lvl}")
                    capture_compromise_success = True

        str2 = res2_lvl if res2_lvl else "なし"
        str1 = res1_lvl if res1_lvl else "なし"

        self.log(f"判定: {l1_n}[{str1}]({s1:.2f}) / {l2_n}[{str2}]({s2:.2f})")

        if ('shiny' not in ENV_RECIPE) and ENABLE_TOOL_ONLY_STOP and (res2_lvl is not None):
            self.log(f"★ 特別終了条件: どうぐパワー単独条件クリア ({l2_n}: {res2_lvl})")
            return True
        
        # 最終成功判定
        base_success = (res1_lvl is not None and res2_lvl is not None) or any_type_success
        capture_success = res3_lvl is not None if ENABLE_CAPTURE_POWER else True
        compromise_success = capture_compromise_success

        if (base_success and capture_success) or compromise_success:
            return True
        return False

    def do(self):
        self.log(f"=== ZA ドーナツ v{VERSION} ({ENV_RECIPE}) ===")
        if 'shiny' in ENV_RECIPE:
            self.log(f"Target: {ENV_RECIPE} + Type=[{TARGET_TYPE_Display}] & {SIZE}")
        else:
            self.log(f"Target: Tool/{INPUT_ITEM_CLASS} & Dosari")
        self.log(f"Timing Mode: {TIMING_MODE}")
        
        while self.count < self.MAX_LOOP:
            self.count += 1
            self.makeDonut()
            
            if self.checkDonutResult():
                self.log("★★★ 目標達成！(初回) ★★★")
                self.save_capture("SUCCESS")
                self.finish()
                break
            
            retry_success = False
            for i in range(self.RETRY_LIMIT):
                self.log(f"--- Retry {i+1}/{self.RETRY_LIMIT} ---")
                self.retry_creation()
                if self.checkDonutResult():
                    self.log(f"★★★ 目標達成！(Retry {i+1}) ★★★")
                    self.save_capture("SUCCESS")
                    retry_success = True
                    break
            
            if retry_success:
                self.finish()
                break
            else:
                self.backupRestart()
        self.finish()