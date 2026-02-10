#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZA ドーナツ厳選 v2.0.0 (Major Update)
・設定をconfig.jsonに外部化し、メインロジック修正時の設定上書きを防止 (Update v2.0.0)
・昼夜切り替え機能の追加（設定間隔でイベールセンターに移動して昼夜変更、backup_restart後に再開）(Update v2.0.0)
・設定ガイド（USER_CONFIG_GUIDE.md）を新規追加 (Update v2.0.0)
・レシピを外部ファイル化（recipes/ディレクトリ内の.pyファイルから読み込み）(Update v1.9.0)
・ユーザーが独自レシピを作成できる機能を追加 (Update v1.9.0)
・レシピの動的検出機能を実装 (Update v1.9.0)
・TARGETSフィールドを追加して、レシピが対象とするもの（色違い・どうぐパワー）を明確化 (Update v1.9.0)
・カスタム条件ファイルによる特別終了機能を追加 (Update v1.9.1)
・モード別条件対応（shinyモード：かがやき×サイズ、toolモード：どうぐ×どっさり）(Update v1.9.1)
・複数タイプ指定に対応（配列形式 ["Fire", "Ground"]）(Update v1.9.1)
・カスタム条件のバグ修正（attribute: null時にType_Allを優先チェック）(Update v1.9.2)
・複数の「かがやきパワー」がある場合、全てのマッチング位置をチェックするように修正 (Update v1.9.2)
・目標達成後ループ機能を追加 (Update v1.9.3)
・重複機能の削除 (Update v1.9.4)
・テンプレートの追加(donut_conditions.json) (Update v1.9.5)
・連続マッチなし時のバックアップ再開機能を追加 (Update v1.9.6)
"""

import os
import importlib.util
import json
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
VERSION = '2.0.0'

# 【外部設定ファイルのパス】
# config.json に詳細設定を記述してください
# ここで指定したファイルから設定を読み込みます
CONFIG_FILE = 'config.json'

# =============================================================================
# ▲▲▲ 設定エリアここまで ▲▲▲
# =============================================================================

# --- 設定ファイル読み込み関数 ---
def load_config_file(config_path):
    """
    外部設定ファイルから設定値を読み込む関数

    Args:
        config_path: 設定ファイルのパス

    Returns:
        dict: 設定値の辞書
    """
    default_config = {
        'recipe': 'recipe1',
        'type': 'Dradon',
        'item_class': 'kinomi',
        'size': 'small',
        'level_size': 3,
        'level_extra': 3,
        'threshold_label': 0.75,
        'threshold_icon': 0.75,
        'threshold_level': 0.89,
        'threshold_result': 0.80,
        'max_loop': 999999,
        'retry_limit': 2,
        'debug_log': True,
        'no_match_timeout_seconds': 60,
        'day_night_interval': 60,
        'enable_loop_after_success': False,
        'loop_after_success_max': 1,
        'use_custom_conditions': False,
        'conditions_file': 'donut_conditions.json',
        'timing_mode': 'switch2',
        'enable_capture_power': False,
        'level_capture': 1,
        'capture_compromise': True
    }

    # スクリプトディレクトリを取得
    script_dir = os.path.dirname(os.path.abspath(__file__))
    abs_config_path = os.path.join(script_dir, config_path)

    # 設定ファイルが存在する場合は読み込み
    if os.path.exists(abs_config_path):
        try:
            with open(abs_config_path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                # デフォルト設定とマージ（ファイルの設定を優先）
                default_config.update(file_config)
                print(f"[System] Config loaded from: {abs_config_path}")
        except Exception as e:
            print(f"[Warning] Failed to load config file: {e}")
            print(f"[System] Using default config")
    else:
        print(f"[Warning] Config file not found: {abs_config_path}")
        print(f"[System] Using default config")

    return default_config


# --- 設定値の読み込み処理 ---
# 設定ファイルから読み込み
config = load_config_file(CONFIG_FILE)

# 各設定値を環境変数 > 設定ファイル > デフォルト値 の順で決定
SETTING_RECIPE = os.environ.get('RECIPE', os.environ.get('MODE', config['recipe'])).lower()
INPUT_TYPE_RAW = os.environ.get('TYPE', config['type'])

# 残りの設定値をロード
SETTING_ITEM_CLASS = config['item_class']
SETTING_SIZE = config['size']
SETTING_LEVEL_SIZE = config['level_size']
SETTING_LEVEL_EXTRA = config['level_extra']
SETTING_THRESHOLD_LABEL = config['threshold_label']
SETTING_THRESHOLD_ICON = config['threshold_icon']
SETTING_THRESHOLD_LEVEL = config['threshold_level']
SETTING_THRESHOLD_RESULT = config['threshold_result']
SETTING_MAX_LOOP = config['max_loop']
SETTING_RETRY_LIMIT = config['retry_limit']
SETTING_DEBUG_LOG = config['debug_log']
SETTING_NO_MATCH_TIMEOUT_SECONDS = config['no_match_timeout_seconds']
SETTING_DAY_NIGHT_INTERVAL = config['day_night_interval']
SETTING_ENABLE_LOOP_AFTER_SUCCESS = config['enable_loop_after_success']
SETTING_LOOP_AFTER_SUCCESS_MAX = config['loop_after_success_max']
SETTING_USE_CUSTOM_CONDITIONS = config['use_custom_conditions']
SETTING_CONDITIONS_FILE = config['conditions_file']
SETTING_TIMING_MODE = config['timing_mode']
SETTING_ENABLE_CAPTURE_POWER = config['enable_capture_power']
SETTING_LEVEL_CAPTURE = config['level_capture']
SETTING_CAPTURE_COMPROMISE = config['capture_compromise']

# --- 設定値の読み込み処理 ---
ENV_RECIPE = os.environ.get('RECIPE', os.environ.get('MODE', SETTING_RECIPE)).lower()
# INPUT_TYPE_RAW は既に114行目で定義されている

# 複数タイプ対応：カンマ区切りをリスト化し、空白除去・Capitalize
TARGET_TYPES = [t.strip().capitalize() for t in INPUT_TYPE_RAW.split(',') if t.strip()]
TARGET_TYPE_Display = "/".join(TARGET_TYPES)

# 環境変数で上書き可能な設定値の読み込み（環境変数 > 設定ファイル）
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

# 目標達成後ループ設定の読み込み
ENABLE_LOOP_AFTER_SUCCESS = True if os.environ.get('ENABLE_LOOP_AFTER_SUCCESS', str(SETTING_ENABLE_LOOP_AFTER_SUCCESS)).lower() == 'true' else False
LOOP_AFTER_SUCCESS_MAX = int(os.environ.get('LOOP_AFTER_SUCCESS_MAX', str(SETTING_LOOP_AFTER_SUCCESS_MAX)))

# --- ほかくパワー設定読み込み ---
ENABLE_CAPTURE_POWER = True if os.environ.get('ENABLE_CAPTURE_POWER', str(SETTING_ENABLE_CAPTURE_POWER)).lower() == 'true' else False

try:
    CAPTURE_LEVEL_REQ = int(os.environ.get('CAPTURE_LEVEL', str(SETTING_LEVEL_CAPTURE)))
except:
    CAPTURE_LEVEL_REQ = 3

ENABLE_CAPTURE_COMPROMISE = True if os.environ.get('ENABLE_CAPTURE_COMPROMISE', str(SETTING_CAPTURE_COMPROMISE)).lower() == 'true' else False

# --- 外部条件ファイル設定読み込み ---
ENABLE_CUSTOM_CONDITIONS = True if os.environ.get('USE_CUSTOM_CONDITIONS', str(SETTING_USE_CUSTOM_CONDITIONS)).lower() == 'true' else False
CONDITIONS_FILE = os.environ.get('CONDITIONS_FILE', SETTING_CONDITIONS_FILE)

# --- 連続マッチなし時のバックアップ再開設定読み込み ---
try:
    NO_MATCH_TIMEOUT_SECONDS = int(os.environ.get('NO_MATCH_TIMEOUT_SECONDS', str(SETTING_NO_MATCH_TIMEOUT_SECONDS)))
except:
    NO_MATCH_TIMEOUT_SECONDS = 60

# --- 昼夜切り替え間隔設定読み込み ---
try:
    DAY_NIGHT_INTERVAL = int(os.environ.get('DAY_NIGHT_INTERVAL', str(SETTING_DAY_NIGHT_INTERVAL))) * 60  # 分を秒に変換
except:
    DAY_NIGHT_INTERVAL = 3600  # デフォルト60分


# =============================================================================
# 動的レシピ検出機能
# =============================================================================
# レシピ管理機能
# =============================================================================
# スクリプトファイルの場所を取得（絶対パス）
SCRIPT_DIR_ABS = os.path.dirname(os.path.abspath(__file__))
RECIPE_DIR_ABS = os.path.join(SCRIPT_DIR_ABS, 'recipes')
CONDITIONS_FILE_ABS = os.path.join(SCRIPT_DIR_ABS, CONDITIONS_FILE)


def get_valid_recipes():
    """
    recipes/ ディレクトリ内のレシピファイルをスキャンして有効なレシピ名を返す

    Returns:
        list: 有効なレシピ名のリスト（拡張子なし）
    """
    valid_recipes = []

    if os.path.exists(RECIPE_DIR_ABS):
        for filename in os.listdir(RECIPE_DIR_ABS):
            if filename.endswith('.py') and filename != 'template.py':
                recipe_name = filename[:-3]  # .py を除去
                valid_recipes.append(recipe_name)

    return sorted(valid_recipes)


def load_recipe(recipe_name):
    """
    レシピファイルを読み込む関数

    Args:
        recipe_name: レシピ名（拡張子なし）

    Returns:
        dict: レシピデータ

    Raises:
        FileNotFoundError: レシピファイルが見つからない場合
        AttributeError: レシピモジュールに必須属性がない場合
    """
    recipe_file = os.path.join(RECIPE_DIR_ABS, f'{recipe_name}.py')

    if not os.path.exists(recipe_file):
        raise FileNotFoundError(f"レシピファイルが見つかりません: {recipe_file}")

    spec = importlib.util.spec_from_file_location(recipe_name, recipe_file)
    recipe_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(recipe_module)

    # バリデーション
    if not hasattr(recipe_module, 'NAME'):
        raise AttributeError(f"レシピファイルに 'NAME' が含まれていません: {recipe_file}")
    if not hasattr(recipe_module, 'STEPS'):
        raise AttributeError(f"レシピファイルに 'STEPS' が含まれていません: {recipe_file}")
    if not hasattr(recipe_module, 'TARGETS'):
        raise AttributeError(f"レシピファイルに 'TARGETS' が含まれていません: {recipe_file}")

    return {
        'name': getattr(recipe_module, 'NAME', recipe_name),
        'category': getattr(recipe_module, 'CATEGORY', 'custom'),
        'targets': getattr(recipe_module, 'TARGETS', []),
        'steps': getattr(recipe_module, 'STEPS', [])
    }


def load_custom_conditions():
    """
    外部条件ファイルからカスタム条件を読み込む関数

    Returns:
        dict: モードごとの条件リスト

    Raises:
        FileNotFoundError: 条件ファイルが見つからない場合
        json.JSONDecodeError: JSON形式が不正な場合
    """
    if not os.path.exists(CONDITIONS_FILE_ABS):
        print(f"[Warning] 条件ファイルが見つかりません: {CONDITIONS_FILE_ABS}")
        return {'shiny_conditions': [], 'tool_conditions': []}

    with open(CONDITIONS_FILE_ABS, 'r', encoding='utf-8') as f:
        conditions_dict = json.load(f)

    # 各モードの条件をフィルタリング
    result = {
        'shiny_conditions': [],
        'tool_conditions': []
    }

    for mode_key in ['shiny_conditions', 'tool_conditions']:
        if mode_key in conditions_dict:
            enabled = [c for c in conditions_dict[mode_key] if c.get('enabled', True)]
            result[mode_key] = enabled
            print(f"[System] {mode_key}: {len(enabled)} conditions loaded from {CONDITIONS_FILE}")

    return result


# カスタム条件を読み込み
CUSTOM_CONDITIONS_DICT = load_custom_conditions() if ENABLE_CUSTOM_CONDITIONS else {'shiny_conditions': [], 'tool_conditions': []}




# 有効性チェック
valid_recipes = get_valid_recipes()

# デバッグ用：有効なレシピを表示
if valid_recipes:
    print(f"[System] Available recipes: {', '.join(valid_recipes)}")

if ENV_RECIPE not in valid_recipes:
    # 既存の振り分けロジックを維持（後方互換性）
    if 'shiny' in ENV_RECIPE:
        if '4' in ENV_RECIPE:
            ENV_RECIPE = 'shiny4'
        elif '3' in ENV_RECIPE:
            ENV_RECIPE = 'shiny3'
        elif '1' in ENV_RECIPE:
            ENV_RECIPE = 'shiny1'
        else:
            ENV_RECIPE = 'shiny2'
    elif 'rainbow' in ENV_RECIPE:
        if '2' in ENV_RECIPE:
            ENV_RECIPE = 'rainbow2'
        elif '3' in ENV_RECIPE:
            ENV_RECIPE = 'rainbow3'
        else:
            ENV_RECIPE = 'rainbow1'
    elif '2' in ENV_RECIPE:
        ENV_RECIPE = 'recipe2'
    else:
        ENV_RECIPE = 'recipe1'

    # 振り分け後のレシピが有効かチェック
    if ENV_RECIPE in valid_recipes:
        print(f"[System] Mode Adjusted -> {ENV_RECIPE}")
    else:
        print(f"[System] Recipe '{ENV_RECIPE}' not found in available recipes")
        print(f"[System] Available recipes: {', '.join(valid_recipes)}")

# レシピをロードして、現在のレシピデータを保持
CURRENT_RECIPE = load_recipe(ENV_RECIPE)
print(f"[System] Recipe loaded: {CURRENT_RECIPE['name']} (targets: {', '.join(CURRENT_RECIPE['targets'])})")

# 現在のモードに応じた条件を取得
if 'shiny' in CURRENT_RECIPE['targets']:
    CUSTOM_CONDITIONS = CUSTOM_CONDITIONS_DICT.get('shiny_conditions', [])
else:
    CUSTOM_CONDITIONS = CUSTOM_CONDITIONS_DICT.get('tool_conditions', [])

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
if 'shiny' in CURRENT_RECIPE['targets']:
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
    ENABLE_LOOP_AFTER_SUCCESS = ENABLE_LOOP_AFTER_SUCCESS
    LOOP_AFTER_SUCCESS_MAX = LOOP_AFTER_SUCCESS_MAX

    # その他の定数
    FIELD_ENTER_WAIT = 2.5
    USE_IMAGE_CHECK = True

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    FOLDER = os.path.abspath(os.path.join(SCRIPT_DIR, 'LegendsZA'))

    def __init__(self, cam, preview=None):
        super().__init__(cam)
        self.count = 0
        self.templates = {}
        self._load_templates()
        self.success_count = 0  # 目標達成回数

    def log(self, msg):
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] [{self.count:05d}] {msg}")

    def _fmt_btn(self, btn):
        if isinstance(btn, (list, tuple)):
            return "[" + ", ".join([self._fmt_btn(b) for b in btn]) + "]"
        if hasattr(btn, 'name'):
            return f"{btn.__class__.__name__}.{btn.name}"
        return str(btn)

    def debug_log(self, msg):
        if self.DEBUG_LOG:
            self.log(f"[CMD] {msg}")

    def press(self, buttons, duration=0.1, wait=0.1):
        self.debug_log(f"Press: {self._fmt_btn(buttons)} (dur={duration}, wait={wait})")
        # super().press内部でのwait()ログ出力を抑止したい場合はフラグ制御
        _prev = self.DEBUG_LOG
        self.DEBUG_LOG = False # press内部の自動waitログを抑制
        super().press(buttons, duration, wait)
        self.DEBUG_LOG = _prev

    def pressRep(self, buttons, repeat=1, duration=0.1, interval=0.1, wait=0.1):
        self.debug_log(f"PressRep: {self._fmt_btn(buttons)} x{repeat} (dur={duration}, interval={interval}, wait={wait})")
        _prev = self.DEBUG_LOG
        self.DEBUG_LOG = False
        super().pressRep(buttons, repeat, duration, interval, wait)
        self.DEBUG_LOG = _prev

    def wait(self, duration):
        if self.DEBUG_LOG:
            self.log(f"[CMD] Wait: {duration}s")
        super().wait(duration)

    def _load_templates(self):
        # テンプレート読み込み処理
        files = {
            'dosari_label':   'dosari_label.png',
            'lv2': 'lv2.png',
            'lv3': 'lv3.png',
            'result_text': 'result_text.png'
        }
        if 'shiny' in CURRENT_RECIPE['targets']:
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

        # カスタム条件で必要な追加のテンプレートを読み込み
        if ENABLE_CUSTOM_CONDITIONS and CUSTOM_CONDITIONS:
            for condition in CUSTOM_CONDITIONS:
                # かがやきパワーの追加タイプチェック
                for power_key in ['power1', 'power2', 'power3']:
                    if power_key in condition:
                        power = condition[power_key]
                        if power['type'] == 'shiny':
                            attribute = power.get('attribute')
                            if attribute:
                                key = f"target_icon_{attribute}"
                                if key not in files:
                                    files[key] = f"Type_{attribute}.png"

                        # どうぐパワーの追加クラスチェック（toolモードのみ）
                        elif power['type'] == 'tool':
                            item_class = power['class']
                            key = f"target_icon_{item_class}"
                            if key not in files:
                                files[key] = f"class_{item_class}.png"

                        # ほかくパワーのテンプレート追加（captureタイプ使用時）
                        elif power['type'] == 'capture':
                            if 'capture_label' not in files:
                                files['capture_label'] = 'capture_label.png'
                            if 'type_all2' not in files:
                                files['type_all2'] = 'Type_All2.png'  # 「すべて」のアイコン
 
        print(f"[System] Version: {VERSION}")
        print(f"[System] Recipe: {ENV_RECIPE}")
        print(f"[System] Timing Mode: {TIMING_MODE}")

        if 'shiny' in CURRENT_RECIPE['targets']:
            print(f"[System] Target: {ENV_RECIPE} + Type=[{TARGET_TYPE_Display}] + {SIZE}")
            if ENABLE_CAPTURE_POWER:
                print(f"[System] CapturePower: Enabled (Lv={CAPTURE_LEVEL_REQ}, Compromise={ENABLE_CAPTURE_COMPROMISE})")
        else:
            print(f"[System] Target: Tool({INPUT_ITEM_CLASS}) + Dosari")

        if ENABLE_CUSTOM_CONDITIONS:
            print(f"[System] CustomConditions: Enabled ({len(CUSTOM_CONDITIONS)} conditions)")
            
        for key, filename in files.items():
            path = os.path.join(self.FOLDER, filename)
            if os.path.exists(path):
                self.templates[key] = cv2.imread(path, 0)
            else:
                self.templates[key] = None

        if self.templates.get('result_text') is None:
            print("[Warning] 'result_text.png' not found. Fallback to fixed timing.")

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

    def detect_power_icon_level(self, gray_screen, label_key, icon_key, target_levels, backup_icon_key=None, check_all_matches=False):
        """
        パワーアイコンとレベルを検出

        Args:
            gray_screen: グレースケール画像
            label_key: ラベルテンプレートのキー
            icon_key: アイコンテンプレートのキー
            target_levels: 対象レベルリスト
            backup_icon_key: バックアップアイコンキー
            check_all_matches: 全てのマッチング位置をチェックするか（複数のパワーがある場合用）

        Returns:
            tuple: (レベル, スコア)
        """
        label_tmpl = self.templates.get(label_key)
        if label_tmpl is None: return None, 0.0
        res = cv2.matchTemplate(gray_screen, label_tmpl, cv2.TM_CCOEFF_NORMED)

        if check_all_matches:
            # 全てのマッチング位置をチェック
            locs = np.where(res >= self.THRESHOLD_LABEL)
            h, w = gray_screen.shape[:2]
            tw, th = label_tmpl.shape[::-1]
            icon_tmpl = self.templates.get(icon_key)

            # マッチング位置をスコア順にソート
            matches = []
            for pt in zip(*locs[::-1]):
                score = res[pt[1], pt[0]]
                matches.append((score, pt))

            # スコア降順でソート
            matches.sort(reverse=True, key=lambda x: x[0])

            # 各マッチング位置でチェック
            for l_score, loc in matches:
                # ROI設定
                roi_y_start = max(0, loc[1] - 10)
                roi_y_end   = min(h, loc[1] + th + 10)
                roi_x_start = loc[0] + tw
                roi_x_end   = min(w, roi_x_start + 250)
                roi_img = gray_screen[roi_y_start:roi_y_end, roi_x_start:roi_x_end]

                # アイコンチェック
                if icon_tmpl is not None:
                    res_t = cv2.matchTemplate(roi_img, icon_tmpl, cv2.TM_CCOEFF_NORMED)
                    _, t_score, _, _ = cv2.minMaxLoc(res_t)
                    if t_score >= self.THRESHOLD_ICON:
                        # レベルチェック
                        best_lvl, best_lvl_score = self._detect_level_in_roi(roi_img, target_levels)
                        if best_lvl is not None:
                            self.debug_log(f"[MultiMatch] Found {icon_key} at ({loc[0]}, {loc[1]}): {best_lvl} (label={l_score:.2f}, icon={t_score:.2f})")
                            return best_lvl, t_score

            return None, 0.0
        else:
            # 従来の単一マッチング（最も高いスコアの位置のみ）
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

    def check_custom_condition(self, gray_screen, condition):
        """
        カスタム条件をチェックするメソッド

        Args:
            gray_screen: グレースケール画像
            condition: 条件辞書

        Returns:
            tuple: (成功フラグ, 検出情報辞書)
        """
        self.debug_log(f"[CustomCondition] Checking condition: {condition['name']}")

        # Power1 のチェック
        p1 = condition['power1']
        p1_result = self._check_single_power(gray_screen, p1)
        self.debug_log(f"[CustomCondition] Power1: {p1_result['info']}[{p1_result['level']}] (success={p1_result['success']}, score={p1_result['score']:.2f})")

        # Power2 のチェック
        p2 = condition['power2']
        p2_result = self._check_single_power(gray_screen, p2)
        self.debug_log(f"[CustomCondition] Power2: {p2_result['info']}[{p2_result['level']}] (success={p2_result['success']}, score={p2_result['score']:.2f})")

        # Power3 のチェック（存在する場合）
        p3_result = None
        if 'power3' in condition:
            p3 = condition['power3']
            p3_result = self._check_single_power(gray_screen, p3)
            self.debug_log(f"[CustomCondition] Power3: {p3_result['info']}[{p3_result['level']}] (success={p3_result['success']}, score={p3_result['score']:.2f})")

        # すべてのパワーが条件を満たしているかチェック
        if p3_result is not None:
            success = p1_result['success'] and p2_result['success'] and p3_result['success']
            debug_result = f"{success} (p1_success={p1_result['success']}, p2_success={p2_result['success']}, p3_success={p3_result['success']})"
        else:
            success = p1_result['success'] and p2_result['success']
            debug_result = f"{success} (p1_success={p1_result['success']}, p2_success={p2_result['success']})"

        detected_info = {
            'condition_name': condition['name'],
            'power1': {
                'type': p1['type'],
                'detected': p1_result
            },
            'power2': {
                'type': p2['type'],
                'detected': p2_result
            }
        }

        # Power3 が存在する場合は追加
        if p3_result is not None:
            detected_info['power3'] = {
                'type': condition['power3']['type'],
                'detected': p3_result
            }

        self.debug_log(f"[CustomCondition] Result: {debug_result}")

        return success, detected_info

    def _check_single_power(self, gray_screen, power_config):
        """
        単一のパワー条件をチェック

        Args:
            gray_screen: グレースケール画像
            power_config: パワー設定辞書

        Returns:
            dict: 検出結果 {'success': bool, 'level': str, 'score': float, 'info': str}
        """
        power_type = power_config['type']
        min_level = power_config['min_level']

        if power_type == 'shiny':
            # かがやきパワーチェック
            attribute = power_config.get('attribute')
            target_levels = get_target_levels(min_level)

            # attributeが配列か文字列かで処理を分ける
            if isinstance(attribute, list):
                # 複数タイプ指定
                attributes = attribute
                attr_display = ", ".join(attributes)
                for attr in attributes:
                    key = f"target_icon_{attr}"
                    lvl, score = self.detect_power_icon_level(gray_screen, 'shiny_label', key, target_levels)
                    if lvl is not None:
                        info = f"かがやき({attr})"
                        break
                if lvl is None:
                    info = f"かがやき({attr_display})"
            elif attribute:
                # 単一タイプ指定
                key = f"target_icon_{attribute}"
                lvl, score = self.detect_power_icon_level(gray_screen, 'shiny_label', key, target_levels)
                info = f"かがやき({attribute})"
            else:
                # 全タイプチェック（タイプ不問）
                # 複数の「かがやきパワー」がある場合、全てのマッチング位置をチェック
                self.debug_log(f"[CustomCondition] Checking all shiny powers (target levels: {target_levels})")

                # Type_Allを優先的にチェック
                lvl, score = self.detect_power_icon_level(gray_screen, 'shiny_label', 'type_all', target_levels, check_all_matches=True)
                if lvl is not None:
                    info = "かがやき(All)"
                    self.debug_log(f"[CustomCondition] Found Type_All: {lvl} (score={score:.2f})")
                else:
                    # Type_Allが見つからなければ全タイプを順にチェック（TARGET_TYPES以外も含む）
                    # 全タイプのリストを定義
                    ALL_TYPES = ['Normal', 'Fire', 'Water', 'Grass', 'Electric', 'Ice', 'Fighting',
                                'Poison', 'Ground', 'Flying', 'Psychic', 'Bug', 'Rock', 'Ghost',
                                'Dragon', 'Dark', 'Steel', 'Fairy']

                    # まずTARGET_TYPESをチェック（優先順位あり）
                    for t_name in TARGET_TYPES:
                        key = f"target_icon_{t_name}"
                        lvl, score = self.detect_power_icon_level(gray_screen, 'shiny_label', key, target_levels, check_all_matches=True)
                        if lvl is not None:
                            info = f"かがやき({t_name})"
                            self.debug_log(f"[CustomCondition] Found Type_{t_name}: {lvl} (score={score:.2f})")
                            break

                    # TARGET_TYPESで見つからなければ全タイプをチェック
                    if lvl is None:
                        for t_name in ALL_TYPES:
                            key = f"target_icon_{t_name}"
                            # テンプレートが存在する場合のみチェック
                            if key in self.templates:
                                lvl, score = self.detect_power_icon_level(gray_screen, 'shiny_label', key, target_levels, check_all_matches=True)
                                if lvl is not None:
                                    info = f"かがやき({t_name})"
                                    self.debug_log(f"[CustomCondition] Found Type_{t_name}: {lvl} (score={score:.2f})")
                                    break
                    if lvl is None:
                        info = "かがやき(N/A)"
                        self.debug_log(f"[CustomCondition] No matching shiny power found")

        elif power_type == 'size':
            # サイズパワーチェック
            size = power_config['size']
            target_levels = get_target_levels(min_level)

            lbl_key_map = {
                'oyabun': 'lbl_oyabun',
                'big': 'lbl_big',
                'small': 'lbl_small'
            }

            lbl_key = lbl_key_map.get(size, f'lbl_{size}')
            lvl, score = self.detect_power_level(gray_screen, lbl_key, target_levels)

            size_name_map = {
                'oyabun': 'オヤブン',
                'big': 'でかでか',
                'small': 'ちびちび'
            }
            info = size_name_map.get(size, size)

        elif power_type == 'tool':
            # どうぐパワーチェック
            item_class = power_config['class']
            target_levels = get_target_levels(min_level)

            # アイコンキーを生成
            if item_class == INPUT_ITEM_CLASS:
                icon_key = "target_icon"
            else:
                icon_key = f"target_icon_{item_class}"
                # テンプレートがロードされていない場合は動的にロード
                if icon_key not in self.templates:
                    filename = f"class_{item_class}.png"
                    path = os.path.join(self.FOLDER, filename)
                    if os.path.exists(path):
                        self.templates[icon_key] = cv2.imread(path, 0)
                        self.debug_log(f"Loaded tool icon template: {filename}")

            lvl, score = self.detect_power_icon_level(gray_screen, 'tool_label', icon_key, target_levels)

            class_name_map = {
                'kinomi': 'きのみ',
                'ball': 'ボール',
                'coin': 'コイン',
                'treasure': '宝物',
                'special': '特別',
                'candy': 'アメ'
            }
            info = class_name_map.get(item_class, item_class)

        elif power_type == 'dosari':
            # どっさりパワーチェック
            target_levels = get_target_levels(min_level)
            lvl, score = self.detect_power_level(gray_screen, 'dosari_label', target_levels)
            info = "どっさり"

        elif power_type == 'capture':
            # ほかくパワーチェック
            attribute = power_config.get('attribute')
            target_levels = get_target_levels(min_level)

            # Type_All2を優先的にチェック
            lvl, score = self.detect_power_icon_level(gray_screen, 'capture_label', 'type_all2', target_levels)
            if lvl is not None:
                info = "ほかく(すべて)"
                self.debug_log(f"[CustomCondition] Found Type_All2: {lvl} (score={score:.2f})")
            else:
                # Type_All2が見つからなければタイプをチェック
                if isinstance(attribute, list):
                    # 複数タイプ指定
                    attributes = attribute
                    attr_display = ", ".join(attributes)
                    for attr in attributes:
                        key = f"target_icon_{attr}"
                        if key in self.templates:
                            lvl, score = self.detect_power_icon_level(gray_screen, 'capture_label', key, target_levels)
                            if lvl is not None:
                                info = f"ほかく({attr})"
                                self.debug_log(f"[CustomCondition] Found Type_{attr}: {lvl} (score={score:.2f})")
                                break
                    if lvl is None:
                        info = f"ほかく({attr_display})"
                elif attribute:
                    # 単一タイプ指定
                    key = f"target_icon_{attribute}"
                    lvl, score = self.detect_power_icon_level(gray_screen, 'capture_label', key, target_levels)
                    info = f"ほかく({attribute})"
                else:
                    # 全タイプチェック（タイプ不問）
                    self.debug_log(f"[CustomCondition] Checking all capture types (target levels: {target_levels})")
                    for t_name in TARGET_TYPES:
                        key = f"target_icon_{t_name}"
                        if key in self.templates:
                            lvl, score = self.detect_power_icon_level(gray_screen, 'capture_label', key, target_levels)
                            if lvl is not None:
                                info = f"ほかく({t_name})"
                                self.debug_log(f"[CustomCondition] Found Type_{t_name}: {lvl} (score={score:.2f})")
                                break
                    if lvl is None:
                        info = "ほかく(N/A)"
                        self.debug_log(f"[CustomCondition] No matching capture power found")

        else:
            # 不明なタイプ
            return {'success': False, 'level': None, 'score': 0.0, 'info': f"Unknown({power_type})"}

        # レベルチェック
        level_num_map = {'lv3': 3, 'lv2': 2, 'lv1': 1}
        detected_level = level_num_map.get(lvl, 0) if lvl else 0
        success = detected_level >= min_level

        return {
            'success': success,
            'level': lvl,
            'score': score,
            'info': info
        }

    def check_all_custom_conditions(self, gray_screen):
        """
        すべてのカスタム条件をチェックし、一致するものがあれば終了する

        Args:
            gray_screen: グレースケール画像

        Returns:
            tuple: (終了フラグ, 検出された条件情報)
        """
        if not ENABLE_CUSTOM_CONDITIONS or not CUSTOM_CONDITIONS:
            return False, None

        mode = 'shiny' if 'shiny' in CURRENT_RECIPE['targets'] else 'tool'
        self.debug_log(f"Checking custom conditions for mode: {mode} ({len(CUSTOM_CONDITIONS)} conditions)")

        for condition in CUSTOM_CONDITIONS:
            success, detected_info = self.check_custom_condition(gray_screen, condition)
            if success:
                # 検出された条件をログ出力
                p1_info = detected_info['power1']
                p2_info = detected_info['power2']
                self.log(f"★★★ カスタム条件ヒット({mode}): {detected_info['condition_name']} ★★★")
                self.log(f"  Power1: {p1_info['detected']['info']}[{p1_info['detected']['level']}]({p1_info['detected']['score']:.2f})")
                self.log(f"  Power2: {p2_info['detected']['info']}[{p2_info['detected']['level']}]({p2_info['detected']['score']:.2f})")
                # Power3 が存在する場合はログ出力
                if 'power3' in detected_info:
                    p3_info = detected_info['power3']
                    self.log(f"  Power3: {p3_info['detected']['info']}[{p3_info['detected']['level']}]({p3_info['detected']['score']:.2f})")
                return True, detected_info

        return False, None

    def makeDonut(self):
        self.log(f"ドーナツ作成開始 ({TIMING_MODE})")

        # Step1: Open Picnic Menu (Common Start)
        self.debug_log(f"Step1: Open Picnic Menu ({TIMING_MODE})")
        self.press(Button.PLUS, 0.2, 0.5)
        self.wait(1.0)
        self.press(Button.Y, 0.2, 0.4)

        # --- エリア判定と動的移動ロジック ---
        if self.isContainTemplate('LegendsZA/area_all.png', 0.88) < 0.88:
            self.debug_log("エリア不一致：すべてへ移動を開始します")
            self.press(Button.MINUS, 0.2, 1.0)
            self.press(Button.A, 0.2, 0.5)
            self.press(Button.B, 0.2, 0.5)
            self.press(Button.Y, 0.2, 0.5)
        # ------------------------------------

        # 各モード共通のメニュー操作
        self.pressRep(Hat.BTM, repeat=3, duration=0.1, interval=0.1)
        self.press(Button.A, 0.2, 0.4)

        if TIMING_MODE == 'switch1':
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

        else: # switch2
            self.press(Button.A, 0.2, 0.6)
            
            self.debug_log("Step2: Loading Ingredients...")
            self.wait(2.6)
            
            self.debug_log("Step3: Selecting Ingredients")
            self.press(Button.Y, 0.2, 0.5)
            self.wait(0.5)
            self.press(Button.A, 0.2, 0.5)
            super().wait(3.6)
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
        """
        外部ファイルから読み込んだレシピを実行するメソッド
        """
        try:
            recipe_name = CURRENT_RECIPE['name']
            self.log(f"レシピ入力: {ENV_RECIPE} ({recipe_name})")

            for step in CURRENT_RECIPE['steps']:
                if step['action'] == 'pressRep':
                    self.pressRep(
                        step['type'],
                        repeat=step['repeat'],
                        duration=step['duration'],
                        interval=step['interval']
                    )

        except Exception as e:
            self.log(f"レシピ実行エラー: {e}")
            raise


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

    def moveToPokemonCenter(self):
        """
        ポケモンセンター（ベール）へ移動してセーブするメソッド
        """
        self.log("ポケモンセンター（ベール）へ移動してセーブします")
        # キャンセルでフィールドに戻る
        self.pressRep(Button.B, repeat=5, interval=0.5)
        self.wait(2.0)
        # メニューを開く
        self.press(Button.PLUS, 0.2, 1.0)
        # 地図を開く
        self.press(Button.Y, 0.2, 1.0)

        # --- エリア判定と動的移動ロジック ---
        if self.isContainTemplate('LegendsZA/area_all.png', 0.88) < 0.88:
            self.debug_log("エリア不一致：すべてへ移動を開始します")
            self.press(Button.MINUS, 0.2, 1.0)
            self.press(Button.A, 0.2, 0.5)
            self.press(Button.B, 0.2, 0.5)
            self.press(Button.Y, 0.2, 0.5)
        # ------------------------------------

        # カーソルを下に4回移動（ベールへ）
        self.pressRep(Hat.BTM, repeat=4, duration=0.1, interval=0.1)
        self.wait(0.5)
        # 決定
        self.pressRep(Button.A, repeat=2, interval=0.5)
        # 空中移動待機
        self.wait(4.0)

        self.log("セーブ完了、ポケモンセンター移動終了")

    def smooth_day_night_change(self, target_time):
        self.log(f"【昼夜切り替え】目標: {'昼' if target_time=='day' else '夜'}")
        if not self.move_to_ibeeru_center(): return False
        self.wait(2.0)
        self.log("イベールセンター移動完了")1   
        return True

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
        self.wait(4.0)
        self.press(Direction.LEFT, 0.65, 0.5)
        self.press(Direction.UP, 0.25, 0.5)
        for _ in range(6): self.press(Button.A, 0.1, 0.2)
        self.wait(15.0)
        for _ in range(6): self.press(Button.B, 0.1, 0.2)
        self.log("イベールセンター着席完了")
        self.wait(2.0)
        return True

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

        if 'shiny' in CURRENT_RECIPE['targets']:
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

        if 'shiny' in CURRENT_RECIPE['targets']:
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

        # === ほかくパワー検知（shinyモードかつ有効時のみ）===
        res3_lvl = None
        s3 = 0.0
        l3_n = "ほかく"
        capture_matched_type = None

        if 'shiny' in CURRENT_RECIPE['targets'] and ENABLE_CAPTURE_POWER:
            # まず「すべて」(Type_All2)をチェック
            res3_lvl, s3 = self.detect_power_icon_level(gray, 'capture_label', 'type_all2', TARGETS_CAPTURE)
            if res3_lvl is not None:
                capture_matched_type = "All2"  # 「すべて」
                l3_n = "ほかく(すべて)"

            # 「すべて」でなければ個別タイプをチェック
            if res3_lvl is None:
                # かがやきが "All" の場合は全タイプをチェック
                if matched_type_name == "All":
                    ALL_TYPES = ['Normal', 'Fire', 'Water', 'Grass', 'Electric', 'Ice', 'Fighting',
                                'Poison', 'Ground', 'Flying', 'Psychic', 'Bug', 'Rock', 'Ghost',
                                'Dragon', 'Dark', 'Steel', 'Fairy']
                    for t_name in ALL_TYPES:
                        key = f"target_icon_{t_name}"
                        if key in self.templates:
                            lvl, score = self.detect_power_icon_level(gray, 'capture_label', key, TARGETS_CAPTURE)
                            if lvl is not None:
                                res3_lvl = lvl
                                s3 = score
                                capture_matched_type = t_name
                                l3_n = f"ほかく({t_name})"
                                break
                else:
                    # かがやきが特定タイプの場合はターゲットタイプのみをチェック
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
            if matched_type_name == "All" and res2_lvl in TARGETS_EXTRA:
                # ほかくパワーがターゲットタイプのいずれかに該当、または「すべて」ならOK
                if capture_matched_type in TARGET_TYPES or capture_matched_type == "All2":
                    self.log(f"★ ほかくパワー妥協成功: かがやき(ぜんぶ){res2_lvl} + ほかく({capture_matched_type}){res3_lvl}")
                    capture_compromise_success = True

        str2 = res2_lvl if res2_lvl else "なし"
        str1 = res1_lvl if res1_lvl else "なし"

        self.log(f"判定: {l1_n}[{str1}]({s1:.2f}) / {l2_n}[{str2}]({s2:.2f})")

        # 特別終了条件(1): カスタム条件一致
        if ENABLE_CUSTOM_CONDITIONS:
            custom_success, custom_info = self.check_all_custom_conditions(gray)
            if custom_success:
                return True

        # 最終成功判定
        # 通常判定： (サイズ一致 AND かがやき一致) AND (ほかくパワー一致 OR ほかくパワー妥協成立)
        base_match = (res1_lvl is not None and res2_lvl is not None)
        capture_ok = (res3_lvl is not None) if ENABLE_CAPTURE_POWER else True

        if base_match and (capture_ok or capture_compromise_success):
            return True
        return False

    def do(self):
        self.log(f"=== ZA ドーナツ v{VERSION} ({ENV_RECIPE}) ===")
        if 'shiny' in CURRENT_RECIPE['targets']:
            self.log(f"Target: {ENV_RECIPE} + Type=[{TARGET_TYPE_Display}] & {SIZE}")
        else:
            self.log(f"Target: Tool/{INPUT_ITEM_CLASS} & Dosari")
        self.log(f"Timing Mode: {TIMING_MODE}")
        if ENABLE_CUSTOM_CONDITIONS:
            self.log(f"Custom Conditions: {len(CUSTOM_CONDITIONS)} loaded")

        # 目標達成後ループ設定の表示
        if self.ENABLE_LOOP_AFTER_SUCCESS:
            self.log(f"目標達成後ループ: 有効 (最大 {self.LOOP_AFTER_SUCCESS_MAX} 回)")
        else:
            self.log("目標達成後ループ: 無効")

        # 連続マッチなし時のバックアップ再開設定の表示
        if NO_MATCH_TIMEOUT_SECONDS > 0:
            self.log(f"連続マッチなし時のバックアップ再開: {NO_MATCH_TIMEOUT_SECONDS}秒で再開")
        else:
            self.log("連続マッチなし時のバックアップ再開: 無効")

        # 昼夜切り替え設定の表示
        if DAY_NIGHT_INTERVAL > 0:
            interval_min = DAY_NIGHT_INTERVAL // 60
            self.log(f"昼夜切り替え: {interval_min}分間隔で実行")
        else:
            self.log("昼夜切り替え: 無効")

        # 昼夜切り替え用の開始時刻を記録
        day_night_check_start_time = time.time()
        # 連続マッチなしの開始時刻を追跡
        no_match_start_time = None

        while self.count < self.MAX_LOOP:
            self.count += 1

            # 昼夜切り替えチェック（設定した間隔に1回）
            day_night_elapsed = time.time() - day_night_check_start_time
            if day_night_elapsed >= DAY_NIGHT_INTERVAL:
                # 現在時刻から昼夜を判定
                current_hour = datetime.now().hour
                target_time = "day" if 6 <= current_hour < 18 else "night"
                interval_min = DAY_NIGHT_INTERVAL // 60
                self.log(f"【{interval_min}分経過】昼夜切り替えシーケンスを実行します（ターゲット: {target_time}）")
                # backup_restart してから昼夜切り替え
                self.backupRestart()
                self.smooth_day_night_change(target_time)
                # ベールへ移動してセーブ
                self.moveToPokemonCenter()
                self.log("ドーナツ作成を再開します")
                # タイマーをリセット
                day_night_check_start_time = time.time()
                # 連続マッチなしタイマーもリセット
                no_match_start_time = None
                continue  # ドーナツ作成をスキップして次のループへ

            self.makeDonut()

            # 最初のドーナツ作成の前で時刻を記録（まだ記録されていない場合）
            if no_match_start_time is None:
                no_match_start_time = time.time()

            if self.checkDonutResult():
                self.success_count += 1
                self.log(f"★★★ 目標達成！(回数: {self.success_count}/{self.LOOP_AFTER_SUCCESS_MAX}) ★★★")
                self.save_capture("SUCCESS")
                # 成功時はマッチなし時間をリセット
                no_match_start_time = None

                # 目標達成後ループ機能の判定
                if self.ENABLE_LOOP_AFTER_SUCCESS and self.success_count < self.LOOP_AFTER_SUCCESS_MAX:
                    self.log("目標達成後ループ機能：ポケモンセンターへ移動してセーブします")
                    self.moveToPokemonCenter()
                    self.log("ドーナツ作成を再開します")
                    continue
                else:
                    self.finish()
                    break

            retry_success = False
            for i in range(self.RETRY_LIMIT):
                self.log(f"--- Retry {i+1}/{self.RETRY_LIMIT} ---")
                self.retry_creation()
                if self.checkDonutResult():
                    self.success_count += 1
                    self.log(f"★★★ 目標達成！(Retry {i+1}, 回数: {self.success_count}/{self.LOOP_AFTER_SUCCESS_MAX}) ★★★")
                    self.save_capture("SUCCESS")
                    retry_success = True
                    # 成功時はマッチなし時間をリセット
                    no_match_start_time = None

                    # 目標達成後ループ機能の判定
                    if self.ENABLE_LOOP_AFTER_SUCCESS and self.success_count < self.LOOP_AFTER_SUCCESS_MAX:
                        self.log("目標達成後ループ機能：ポケモンセンターへ移動してセーブします")
                        self.moveToPokemonCenter()
                        self.log("ドーナツ作成を再開します")
                        break
                    else:
                        break

            # 連続マッチなしのタイムアウトチェック
            if no_match_start_time is not None and NO_MATCH_TIMEOUT_SECONDS > 0:
                elapsed_time = time.time() - no_match_start_time
                if elapsed_time >= NO_MATCH_TIMEOUT_SECONDS:
                    self.log(f"⚠️ 連続マッチなしが {elapsed_time:.1f}秒を超えました。backup restartから再開します")
                    self.backupRestart()
                    no_match_start_time = None
                    continue

            if retry_success:
                if self.ENABLE_LOOP_AFTER_SUCCESS and self.success_count < self.LOOP_AFTER_SUCCESS_MAX:
                    continue
                self.finish()
                break
            else:
                self.backupRestart()
        self.finish()