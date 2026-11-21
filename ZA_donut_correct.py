#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZA ドーナツ厳選 v2.1.0
・開始時に設定画面を表示し、config.json の項目を選んでから実行する方式を追加 (Update v2.1.0)
・Poke-Controller-Modified-Extension 0.2.0 に対応（予約・モニターからの開始は自動で開始、Web版・実行リストは画面なし）(Update v2.1.0)
・コマンド名を文字列リテラルで固定（PCME 0.2.0 は NAME を静的に読むため。f 文字列だと一覧に出ない）(Update v2.1.0)
・どうぐ＋どっさりのときは、config の値に関係なく、ほかくパワーを判定に使わないよう修正（ほかくを含むカスタム条件も外す）(Update v2.1.0)
v2.0.0 (Major Update)
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
VERSION = '2.1.0'

# 【外部設定ファイルのパス】
# config.json に詳細設定を記述してください
# ここで指定したファイルから設定を読み込みます
CONFIG_FILE = 'config.json'

# =============================================================================
# ▲▲▲ 設定エリアここまで ▲▲▲
# =============================================================================

# --- 設定のデフォルト値 ---
DEFAULT_CONFIG = {
    'recipe': 'recipe1',
    'type': 'Dradon',
    'item_class': 'kinomi',
    'item_class_2nd': '',          # 2つめのどうぐの種類（'' = 選ばない）。item_class か、これに一致すれば成功
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
    'capture_compromise': True,
    # --- 設定画面 (v2.1.0) ---
    'show_settings_ui': True,
    'settings_ui_timeout_seconds': 60
}


# --- 設定ファイル読み込み関数 ---
def load_config_file(config_path):
    """
    外部設定ファイルから設定値を読み込む関数

    Args:
        config_path: 設定ファイルのパス

    Returns:
        dict: 設定値の辞書
    """
    default_config = dict(DEFAULT_CONFIG)

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

# =============================================================================
# レシピ・カスタム条件の読み込み関数
# =============================================================================
# スクリプトファイルの場所を取得（絶対パス）
SCRIPT_DIR_ABS = os.path.dirname(os.path.abspath(__file__))
RECIPE_DIR_ABS = os.path.join(SCRIPT_DIR_ABS, 'recipes')
CONFIG_FILE_ABS = os.path.join(SCRIPT_DIR_ABS, CONFIG_FILE)


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


def load_custom_conditions(conditions_file_abs, conditions_file):
    """
    外部条件ファイルからカスタム条件を読み込む関数

    Args:
        conditions_file_abs: 条件ファイルの絶対パス
        conditions_file: 条件ファイル名（ログ表示用）

    Returns:
        dict: モードごとの条件リスト

    Raises:
        json.JSONDecodeError: JSON形式が不正な場合
    """
    if not os.path.exists(conditions_file_abs):
        print(f"[Warning] 条件ファイルが見つかりません: {conditions_file_abs}")
        return {'shiny_conditions': [], 'tool_conditions': []}

    with open(conditions_file_abs, 'r', encoding='utf-8') as f:
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
            print(f"[System] {mode_key}: {len(enabled)} conditions loaded from {conditions_file}")

    return result


# 判定用リスト生成関数
def get_target_levels(req_lvl):
    targets = []
    if req_lvl <= 3: targets.append('lv3')
    if req_lvl <= 2: targets.append('lv2')
    if req_lvl <= 1: targets.append('lv1')
    return targets


def _is_true(value):
    """設定値の真偽判定（従来どおり、文字列にして 'true' のときだけ True）"""
    return str(value).lower() == 'true'


VALID_ITEM_CLASSES = ['kinomi', 'ball', 'coin', 'treasure', 'special', 'candy']


def apply_config(cfg, use_env=True):
    """
    設定値（config.json の辞書）から、各モジュール変数を決めて反映する (v2.1.0)

    Args:
        cfg: 設定値の辞書（config.json と同じキー）
        use_env: True なら環境変数での上書きを有効にする（起動時）。
                 設定画面で選んだ値を使うときは False（画面の値をそのまま使う）
    """
    env = os.environ if use_env else {}
    g = {}

    # 各設定値を環境変数 > 設定ファイル > デフォルト値 の順で決定
    recipe = str(env.get('RECIPE', env.get('MODE', cfg['recipe']))).lower()
    input_type_raw = env.get('TYPE', cfg['type'])

    # 複数タイプ対応：カンマ区切りをリスト化し、空白除去・Capitalize
    g['INPUT_TYPE_RAW'] = input_type_raw
    g['TARGET_TYPES'] = [t.strip().capitalize() for t in input_type_raw.split(',') if t.strip()]
    g['TARGET_TYPE_Display'] = "/".join(g['TARGET_TYPES'])

    # 環境変数で上書き可能な設定値の読み込み（環境変数 > 設定ファイル）
    size = str(env.get('SIZE', cfg['size'])).lower()
    g['INPUT_ITEM_CLASS'] = str(env.get('ITEM_CLASS', cfg['item_class'])).lower()
    # 2つめのどうぐの種類（'' / none / null = 選ばない。1つめと同じなら選ばない扱い）
    item2 = env.get('ITEM_CLASS_2ND', cfg.get('item_class_2nd', ''))
    item2 = '' if item2 is None else str(item2).strip().lower()
    if item2 in ('none', 'null', '選ばない'):
        item2 = ''
    if item2 and item2 not in VALID_ITEM_CLASSES:
        print(f"[Warning] item_class_2nd '{item2}' は使えません（{', '.join(VALID_ITEM_CLASSES)}）。2つめは選ばない扱いにします。")
        item2 = ''
    if item2 == g['INPUT_ITEM_CLASS']:
        item2 = ''
    g['INPUT_ITEM_CLASS_2ND'] = item2
    g['ITEM_CLASS_DISPLAY'] = g['INPUT_ITEM_CLASS'] + (f"/{item2}" if item2 else '')

    # タイミングモード設定
    timing_mode = str(env.get('TIMING_MODE', cfg['timing_mode'])).lower()
    if timing_mode not in ['switch1', 'switch2']:
        print(f"[Warning] Unknown TIMING_MODE '{timing_mode}'. Fallback to 'switch2'.")
        timing_mode = 'switch2'
    g['TIMING_MODE'] = timing_mode

    # レベル設定
    try:
        g['SIZE_LEVEL_REQ'] = int(env.get('SIZE_LEVEL', str(cfg['level_size'])))
    except Exception:
        g['SIZE_LEVEL_REQ'] = 3

    try:
        g['EXTRA_LEVEL_REQ'] = int(env.get('EXTRA_LEVEL', str(cfg['level_extra'])))
    except Exception:
        g['EXTRA_LEVEL_REQ'] = 3

    # 詳細設定
    g['THRESHOLD_LABEL'] = float(env.get('THRESHOLD_LABEL', cfg['threshold_label']))
    g['THRESHOLD_ICON'] = float(env.get('THRESHOLD_ICON', cfg['threshold_icon']))
    g['THRESHOLD_LEVEL'] = float(env.get('THRESHOLD_LEVEL', cfg['threshold_level']))
    g['THRESHOLD_RESULT'] = float(env.get('THRESHOLD_RESULT', cfg['threshold_result']))

    g['MAX_LOOP'] = int(env.get('MAX_LOOP', cfg['max_loop']))
    g['RETRY_LIMIT'] = int(env.get('RETRY_LIMIT', cfg['retry_limit']))
    g['DEBUG_LOG'] = _is_true(env.get('DEBUG_LOG', str(cfg['debug_log'])))

    # 目標達成後ループ設定の読み込み
    g['ENABLE_LOOP_AFTER_SUCCESS'] = _is_true(env.get('ENABLE_LOOP_AFTER_SUCCESS', str(cfg['enable_loop_after_success'])))
    g['LOOP_AFTER_SUCCESS_MAX'] = int(env.get('LOOP_AFTER_SUCCESS_MAX', str(cfg['loop_after_success_max'])))

    # --- ほかくパワー設定読み込み ---
    g['ENABLE_CAPTURE_POWER'] = _is_true(env.get('ENABLE_CAPTURE_POWER', str(cfg['enable_capture_power'])))

    try:
        g['CAPTURE_LEVEL_REQ'] = int(env.get('CAPTURE_LEVEL', str(cfg['level_capture'])))
    except Exception:
        g['CAPTURE_LEVEL_REQ'] = 3

    g['ENABLE_CAPTURE_COMPROMISE'] = _is_true(env.get('ENABLE_CAPTURE_COMPROMISE', str(cfg['capture_compromise'])))

    # --- 外部条件ファイル設定読み込み ---
    g['ENABLE_CUSTOM_CONDITIONS'] = _is_true(env.get('USE_CUSTOM_CONDITIONS', str(cfg['use_custom_conditions'])))
    conditions_file = env.get('CONDITIONS_FILE', cfg['conditions_file'])
    g['CONDITIONS_FILE'] = conditions_file
    g['CONDITIONS_FILE_ABS'] = os.path.join(SCRIPT_DIR_ABS, conditions_file)

    # --- 連続マッチなし時のバックアップ再開設定読み込み ---
    try:
        g['NO_MATCH_TIMEOUT_SECONDS'] = int(env.get('NO_MATCH_TIMEOUT_SECONDS', str(cfg['no_match_timeout_seconds'])))
    except Exception:
        g['NO_MATCH_TIMEOUT_SECONDS'] = 60

    # --- 昼夜切り替え間隔設定読み込み ---
    try:
        g['DAY_NIGHT_INTERVAL'] = int(env.get('DAY_NIGHT_INTERVAL', str(cfg['day_night_interval']))) * 60  # 分を秒に変換
    except Exception:
        g['DAY_NIGHT_INTERVAL'] = 3600  # デフォルト60分

    # カスタム条件を読み込み
    if g['ENABLE_CUSTOM_CONDITIONS']:
        custom_conditions_dict = load_custom_conditions(g['CONDITIONS_FILE_ABS'], conditions_file)
    else:
        custom_conditions_dict = {'shiny_conditions': [], 'tool_conditions': []}
    g['CUSTOM_CONDITIONS_DICT'] = custom_conditions_dict

    # 有効性チェック
    valid_recipes = get_valid_recipes()

    # デバッグ用：有効なレシピを表示
    if valid_recipes:
        print(f"[System] Available recipes: {', '.join(valid_recipes)}")

    if recipe not in valid_recipes:
        # 既存の振り分けロジックを維持（後方互換性）
        if 'shiny' in recipe:
            if '4' in recipe:
                recipe = 'shiny4'
            elif '3' in recipe:
                recipe = 'shiny3'
            elif '1' in recipe:
                recipe = 'shiny1'
            else:
                recipe = 'shiny2'
        elif 'rainbow' in recipe:
            if '2' in recipe:
                recipe = 'rainbow2'
            elif '3' in recipe:
                recipe = 'rainbow3'
            else:
                recipe = 'rainbow1'
        elif '2' in recipe:
            recipe = 'recipe2'
        else:
            recipe = 'recipe1'

        # 振り分け後のレシピが有効かチェック
        if recipe in valid_recipes:
            print(f"[System] Mode Adjusted -> {recipe}")
        else:
            print(f"[System] Recipe '{recipe}' not found in available recipes")
            print(f"[System] Available recipes: {', '.join(valid_recipes)}")

    g['SETTING_RECIPE'] = recipe
    g['ENV_RECIPE'] = recipe

    # レシピをロードして、現在のレシピデータを保持
    current_recipe = load_recipe(recipe)
    g['CURRENT_RECIPE'] = current_recipe
    print(f"[System] Recipe loaded: {current_recipe['name']} (targets: {', '.join(current_recipe['targets'])})")

    # 現在のモードに応じた条件を取得
    if 'shiny' in current_recipe['targets']:
        g['CUSTOM_CONDITIONS'] = custom_conditions_dict.get('shiny_conditions', [])
    else:
        # どうぐモード（どうぐ＋どっさり）のドーナツには、ほかくパワーは付かない。
        # config の値に関係なく、ほかくパワーは判定に使わない
        if g['ENABLE_CAPTURE_POWER'] or g['ENABLE_CAPTURE_COMPROMISE']:
            print("[System] どうぐモードのため、ほかくパワーの設定（enable_capture_power / capture_compromise）は使いません")
        g['ENABLE_CAPTURE_POWER'] = False
        g['ENABLE_CAPTURE_COMPROMISE'] = False
        # ほかくパワーを含むカスタム条件は、どうぐモードでは成立しないので外す
        tool_conditions = []
        for cond in custom_conditions_dict.get('tool_conditions', []):
            if any(isinstance(cond.get(k), dict) and cond[k].get('type') == 'capture' for k in ('power1', 'power2', 'power3')):
                print(f"[Warning] カスタム条件「{cond.get('name', '?')}」はほかくパワーを含むため、どうぐモードでは使いません")
                continue
            tool_conditions.append(cond)
        g['CUSTOM_CONDITIONS'] = tool_conditions

    valid_sizes = ['oyabun', 'big', 'small']
    if size not in valid_sizes:
        size = 'oyabun'
    g['SIZE'] = size

    g['TARGETS_SIZE'] = get_target_levels(g['SIZE_LEVEL_REQ'])
    g['TARGETS_EXTRA'] = get_target_levels(g['EXTRA_LEVEL_REQ'])
    g['TARGETS_CAPTURE'] = get_target_levels(g['CAPTURE_LEVEL_REQ'])

    globals().update(g)

    # クラスに持たせている値も合わせる（クラス定義後に呼ばれた場合）
    cls = globals().get('ZA_DonutV188')
    if cls is not None:
        for key in ('THRESHOLD_LABEL', 'THRESHOLD_ICON', 'THRESHOLD_LEVEL', 'THRESHOLD_RESULT',
                    'MAX_LOOP', 'RETRY_LIMIT', 'DEBUG_LOG',
                    'ENABLE_LOOP_AFTER_SUCCESS', 'LOOP_AFTER_SUCCESS_MAX'):
            setattr(cls, key, g[key])


# --- 設定値の読み込み処理（起動時: 環境変数 > config.json > デフォルト値） ---
apply_config(config, use_env=True)

CAPTURE_DIR = "debug_captures"
os.makedirs(CAPTURE_DIR, exist_ok=True)

class ZA_DonutV188(ImageProcPythonCommand):
    # PCME 0.2.0 以降は NAME をソースから構文解析だけで読む（実行しない）。
    # f 文字列や変数を使うと「not a literal」として無視され、コマンド一覧に出なくなるので、必ず文字列リテラルで書く。
    # バージョンを上げるときは、上の VERSION とこの NAME の両方を書き換えること。
    NAME = "ZA ドーナツ厳選 v2.1.0"

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

    def __init__(self, cam, gui=None):
        # PCME 0.2.0: 第2引数にプレビュー（CaptureArea）が渡される。設定画面の親ウィンドウに使う
        try:
            super().__init__(cam, gui)
        except TypeError:
            super().__init__(cam)
            self.gui = gui
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
            if INPUT_ITEM_CLASS_2ND:
                files['target_icon_2nd'] = f"class_{INPUT_ITEM_CLASS_2ND}.png"

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
            print(f"[System] Target: Tool({ITEM_CLASS_DISPLAY}) + Dosari")

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
        self.log("イベールセンター移動完了") 
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
            # 1つめで一致しなければ、2つめのどうぐの種類で判定
            if res2_lvl is None and INPUT_ITEM_CLASS_2ND:
                lvl_2nd, s_2nd = self.detect_power_icon_level(
                    gray, 'tool_label', 'target_icon_2nd', TARGETS_EXTRA
                )
                if lvl_2nd is not None:
                    res2_lvl, s2 = lvl_2nd, s_2nd
                    l2_n = f"どうぐ({INPUT_ITEM_CLASS_2ND}・2つめ)"
                else:
                    s2 = max(s2, s_2nd)
                    l2_n = f"どうぐ({ITEM_CLASS_DISPLAY})"

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
        if ENABLE_CAPTURE_COMPROMISE and 'shiny' in CURRENT_RECIPE['targets'] and ENABLE_CAPTURE_POWER:
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
        # ほかくパワーは色違いモードのときだけ判定に使う（どうぐ＋どっさりのドーナツには付かない）
        capture_ok = (res3_lvl is not None) if ('shiny' in CURRENT_RECIPE['targets'] and ENABLE_CAPTURE_POWER) else True

        if base_match and (capture_ok or capture_compromise_success):
            return True
        return False

    # =========================================================================
    # 開始前の設定画面 (v2.1.0)
    # =========================================================================
    def _tk_root(self):
        """設定画面の親にする Tk のウィンドウ（Web ブラウザ版など、Tk の画面が無いときは None）"""
        gui = getattr(self, 'gui', None)
        if gui is None:
            return None
        try:
            import tkinter as tk
            if not isinstance(gui, tk.Misc):
                return None
            return gui.winfo_toplevel()
        except Exception:
            return None

    def _later(self, fn):
        """画面のスレッドで、今の処理が終わった後に fn を呼ぶ（キャンセル時の postProcess 用）"""
        if fn is None:
            return
        root = self._tk_root()
        try:
            if root is not None:
                root.after_idle(fn)
                return
        except Exception:
            pass
        fn()

    def _reload_templates(self):
        self.templates = {}
        self._load_templates()

    def start(self, ser, postProcess):
        """
        Start ボタンで呼ばれる（画面のスレッド）。設定画面を出して、選んだ設定で開始する。
        - PCME 0.2.0 の command_service.start は、この関数が戻った後に状態を「実行中」にする。
          そのため、キャンセル時の postProcess（ボタンを戻す処理）は after_idle で後から呼ぶ
        - 実行リストは start を通らず do_safe を直接呼ぶので、画面は出ない（config.json の値で動く）
        """
        try:
            ok = self._prepare_settings()
        except Exception:
            import traceback
            traceback.print_exc()
            print("[Error] 設定画面でエラーが出たため、開始しませんでした。")
            ok = False
        if not ok:
            print("[System] 開始をキャンセルしました。")
            self._later(postProcess)
            return None
        return super().start(ser, postProcess)

    def _prepare_settings(self):
        """設定を決めて反映する。開始してよければ True、キャンセルなら False"""
        cfg = load_config_file(CONFIG_FILE)
        root = self._tk_root()
        show = _is_true(cfg.get('show_settings_ui', True))
        if not show or root is None or not _is_main_thread():
            if show and root is None:
                print("[System] 設定画面を出せない画面（Web ブラウザ版など）なので、config.json の値で開始します。")
            apply_config(cfg, use_env=True)
            self._reload_templates()
            return True

        result = _SettingsDialog(root, cfg).show()
        if result is None:
            return False
        new_cfg, save = result
        if save:
            try:
                save_config_file(CONFIG_FILE, new_cfg)
                print(f"[System] 設定を保存しました: {CONFIG_FILE_ABS}")
            except Exception as e:
                print(f"[Warning] config.json に保存できませんでした（この回は画面の値で動きます）: {e}")
        apply_config(new_cfg, use_env=False)
        self.DEBUG_LOG = DEBUG_LOG
        self._reload_templates()
        return True

    def do(self):
        self.log(f"=== ZA ドーナツ v{VERSION} ({ENV_RECIPE}) ===")
        if 'shiny' in CURRENT_RECIPE['targets']:
            self.log(f"Target: {ENV_RECIPE} + Type=[{TARGET_TYPE_Display}] & {SIZE}")
        else:
            self.log(f"Target: Tool/{ITEM_CLASS_DISPLAY} & Dosari")
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


# =============================================================================
# 設定画面 (v2.1.0)
# =============================================================================
def _is_main_thread():
    import threading
    return threading.current_thread() is threading.main_thread()


def save_config_file(config_path, cfg):
    """
    config.json に書き込む。ファイルにあるキーの順番はそのまま、無いキーは後ろに足す。
    （画面に無いキーや、知らないキーも消さない）
    """
    abs_path = os.path.join(SCRIPT_DIR_ABS, config_path)
    data = {}
    if os.path.exists(abs_path):
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                data = loaded
        except Exception:
            data = {}
    for key, value in cfg.items():
        data[key] = value
    tmp_path = abs_path + '.tmp'
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    os.replace(tmp_path, abs_path)


# 選択肢（docs/USER_CONFIG_GUIDE.md の「選択肢一覧」と同じ）
UI_TYPES = [
    ('Normal', 'ノーマル'), ('Fire', 'ほのお'), ('Water', 'みず'), ('Grass', 'くさ'),
    ('Electric', 'でんき'), ('Ice', 'こおり'), ('Fighting', 'かくとう'), ('Poison', 'どく'),
    ('Ground', 'じめん'), ('Flying', 'ひこう'), ('Psychic', 'エスパー'), ('Bug', 'むし'),
    ('Rock', 'いわ'), ('Ghost', 'ゴースト'), ('Dragon', 'ドラゴン'), ('Dark', 'あく'),
    ('Steel', 'はがね'), ('Fairy', 'フェアリー'),
]
UI_SIZES = [('oyabun', 'オヤブン'), ('big', 'でかでか'), ('small', 'ちびちび')]
UI_ITEM_CLASSES = [('kinomi', 'きのみ'), ('ball', 'ボール'), ('coin', 'コイン'),
                   ('treasure', '宝物'), ('special', '特別'), ('candy', 'アメ')]
UI_TIMING_MODES = [('switch2', 'Switch 2 / 有機EL など（速い）'), ('switch1', 'Switch / Lite など（遅い）')]

# 設定画面の値より優先されなくなる環境変数（画面を使うときは、画面の値で動く）
UI_ENV_KEYS = ['RECIPE', 'MODE', 'TYPE', 'ITEM_CLASS', 'ITEM_CLASS_2ND', 'SIZE', 'SIZE_LEVEL', 'EXTRA_LEVEL', 'THRESHOLD_LABEL',
               'THRESHOLD_ICON', 'THRESHOLD_LEVEL', 'THRESHOLD_RESULT', 'MAX_LOOP', 'RETRY_LIMIT', 'DEBUG_LOG',
               'NO_MATCH_TIMEOUT_SECONDS', 'DAY_NIGHT_INTERVAL', 'ENABLE_LOOP_AFTER_SUCCESS', 'LOOP_AFTER_SUCCESS_MAX',
               'USE_CUSTOM_CONDITIONS', 'CONDITIONS_FILE', 'TIMING_MODE', 'ENABLE_CAPTURE_POWER', 'CAPTURE_LEVEL',
               'ENABLE_CAPTURE_COMPROMISE']


def _recipe_infos():
    """[(レシピ名, NAME, 'shiny' / 'tool')]（読めないレシピは飛ばす）"""
    infos = []
    for name in get_valid_recipes():
        try:
            r = load_recipe(name)
        except Exception as e:
            print(f"[Warning] レシピ {name} を読めませんでした: {e}")
            continue
        infos.append((name, r['name'], 'shiny' if 'shiny' in r['targets'] else 'tool'))
    return infos


class _SettingsDialog:
    """
    開始前に config.json の項目を選ぶ画面（Tk の Toplevel。Start を押した画面のスレッドで開き、閉じるまで待つ）。
    show() の戻り値: (設定の辞書, config.json に保存するか)。キャンセルなら None
    """

    def __init__(self, root, cfg):
        import tkinter as tk
        from tkinter import ttk, messagebox
        self.tk, self.ttk, self.messagebox = tk, ttk, messagebox
        self.root = root
        self.cfg = dict(DEFAULT_CONFIG)
        self.cfg.update(cfg)
        self.result = None
        self._countdown = None
        self._after_id = None
        self.recipes = _recipe_infos()
        self.colors = self._theme_colors(root)

    @staticmethod
    def _theme_colors(root):
        """PCME 0.2.0 のテーマの色（使えない色名のとき・テーマが無いときは、決まった色）"""
        colors = {'bg': None, 'muted': '#707070', 'danger': '#c0392b'}
        try:
            import Theme
            for role in colors:
                try:
                    value = Theme.color(role)
                    root.winfo_rgb(value)      # この OS で使える色か（"SystemGrayText" などは Windows だけ）
                    colors[role] = value
                except Exception:
                    pass
        except Exception:
            pass
        return colors

    # ---------------------------------------------------------------- 部品
    def _note(self, parent, text, danger=False, **pack):
        lbl = self.ttk.Label(parent, text=text, wraplength=620,
                             foreground=self.colors['danger' if danger else 'muted'])
        lbl.pack(anchor='w', **pack)
        return lbl

    def _row(self, parent, label):
        f = self.ttk.Frame(parent)
        f.pack(fill='x', pady=2)
        self.ttk.Label(f, text=label, width=24).pack(side='left')
        return f

    def _spin(self, parent, label, var, from_, to, inc=1, note='', width=8):
        f = self._row(parent, label)
        self.ttk.Spinbox(f, from_=from_, to=to, increment=inc, textvariable=var, width=width).pack(side='left')
        if note:
            self.ttk.Label(f, text=note, foreground=self.colors['muted']).pack(side='left', padx=6)
        return f

    def _radios(self, parent, label, var, choices):
        f = self._row(parent, label)
        for value, text in choices:
            self.ttk.Radiobutton(f, text=text, value=value, variable=var).pack(side='left', padx=(0, 8))
        return f

    def _levels(self, parent, label, var):
        return self._radios(parent, label, var, [('3', 'Lv3 のみ'), ('2', 'Lv2 以上'), ('1', 'Lv1 以上 ※')])

    # ---------------------------------------------------------------- 画面
    def show(self):
        tk, ttk = self.tk, self.ttk
        c = self.cfg
        win = tk.Toplevel(self.root)
        self.win = win
        win.title(f"ZA ドーナツ厳選 v{VERSION}: 設定")
        win.transient(self.root)
        win.resizable(False, False)
        if self.colors['bg']:
            try:
                win.configure(bg=self.colors['bg'])
            except tk.TclError:
                pass

        body = ttk.Frame(win, padding=12)
        body.pack(fill='both', expand=True)

        # --- 変数
        recipe_values = [f"{n} — {title}（{'色違い' if mode == 'shiny' else 'どうぐ'}）" for n, title, mode in self.recipes]
        recipe_names = [n for n, _, _ in self.recipes]
        cur_recipe = str(c['recipe']).lower()
        self.v_recipe = tk.StringVar(value=recipe_values[recipe_names.index(cur_recipe)] if cur_recipe in recipe_names
                                     else (recipe_values[0] if recipe_values else ''))
        self.recipe_values, self.recipe_names = recipe_values, recipe_names
        cur_types = [t.strip().capitalize() for t in str(c['type']).split(',') if t.strip()]
        self.type_order = [t for t in cur_types if t in dict(UI_TYPES)]
        self.v_types = {t: tk.BooleanVar(value=t in cur_types) for t, _ in UI_TYPES}
        self.v_size = tk.StringVar(value=str(c['size']).lower() if str(c['size']).lower() in dict(UI_SIZES) else 'oyabun')
        self.v_item = tk.StringVar(value=str(c['item_class']).lower())
        item2 = c.get('item_class_2nd', '')
        item2 = '' if item2 is None else str(item2).strip().lower()
        self.v_item2 = tk.StringVar(value=item2 if item2 in dict(UI_ITEM_CLASSES) else '')
        self.v_level_size = tk.StringVar(value=str(c['level_size']))
        self.v_level_extra = tk.StringVar(value=str(c['level_extra']))
        self.v_capture = tk.BooleanVar(value=_is_true(c['enable_capture_power']))
        self.v_level_capture = tk.StringVar(value=str(c['level_capture']))
        self.v_compromise = tk.BooleanVar(value=_is_true(c['capture_compromise']))
        self.v_max_loop = tk.StringVar(value=str(c['max_loop']))
        self.v_retry = tk.StringVar(value=str(c['retry_limit']))
        self.v_loop_after = tk.BooleanVar(value=_is_true(c['enable_loop_after_success']))
        self.v_loop_after_max = tk.StringVar(value=str(c['loop_after_success_max']))
        self.v_no_match = tk.StringVar(value=str(c['no_match_timeout_seconds']))
        self.v_day_night = tk.StringVar(value=str(c['day_night_interval']))
        self.v_timing = tk.StringVar(value=str(c['timing_mode']).lower() if str(c['timing_mode']).lower() in dict(UI_TIMING_MODES) else 'switch2')
        self.v_debug = tk.BooleanVar(value=_is_true(c['debug_log']))
        self.v_custom = tk.BooleanVar(value=_is_true(c['use_custom_conditions']))
        self.v_cond_file = tk.StringVar(value=str(c['conditions_file']))
        self.v_th = {k: tk.StringVar(value=str(c[k])) for k in
                     ('threshold_label', 'threshold_icon', 'threshold_level', 'threshold_result')}
        self.v_show_ui = tk.BooleanVar(value=_is_true(c.get('show_settings_ui', True)))
        self.v_ui_timeout = tk.StringVar(value=str(c.get('settings_ui_timeout_seconds', 60)))
        self.v_save = tk.BooleanVar(value=True)

        # --- レシピ（上に固定）
        f = self._row(body, 'レシピ')
        cb = ttk.Combobox(f, textvariable=self.v_recipe, values=recipe_values, state='readonly', width=58)
        cb.pack(side='left')
        cb.bind('<<ComboboxSelected>>', lambda e: self._update_mode())
        self.mode_label = ttk.Label(body, text='', foreground=self.colors['muted'])
        self.mode_label.pack(anchor='w', pady=(0, 6))

        nb = ttk.Notebook(body)
        nb.pack(fill='both', expand=True)
        tab_target = ttk.Frame(nb, padding=10)
        tab_run = ttk.Frame(nb, padding=10)
        tab_detect = ttk.Frame(nb, padding=10)
        tab_ui = ttk.Frame(nb, padding=10)
        nb.add(tab_target, text='狙う条件')
        nb.add(tab_run, text='回数・リセット')
        nb.add(tab_detect, text='認識・カスタム条件')
        nb.add(tab_ui, text='この画面')

        # --- タブ1: 狙う条件
        self.shiny_frame = ttk.Frame(tab_target)
        self.tool_frame = ttk.Frame(tab_target)

        sf = self.shiny_frame
        ttk.Label(sf, text='かがやきパワーのタイプ（複数可。チェックした順に判定。「ぜんぶ」は常に判定）').pack(anchor='w')
        grid = ttk.Frame(sf)
        grid.pack(anchor='w', pady=(2, 6))
        for i, (t, jp) in enumerate(UI_TYPES):
            ttk.Checkbutton(grid, text=f"{jp}（{t}）", variable=self.v_types[t],
                            command=lambda t=t: self._type_toggled(t)).grid(row=i // 6, column=i % 6, sticky='w', padx=(0, 10), pady=1)
        self.type_order_label = ttk.Label(sf, text='', foreground=self.colors['muted'])
        self.type_order_label.pack(anchor='w', pady=(0, 6))
        self._radios(sf, 'サイズパワー', self.v_size, UI_SIZES)
        self._levels(sf, 'サイズパワーのレベル', self.v_level_size)
        self._levels(sf, 'かがやきパワーのレベル', self.v_level_extra)
        ttk.Separator(sf).pack(fill='x', pady=6)
        ttk.Checkbutton(sf, text='ほかくパワーも条件にする', variable=self.v_capture,
                        command=self._update_capture).pack(anchor='w')
        self.capture_rows = [self._levels(sf, 'ほかくパワーのレベル', self.v_level_capture)]
        cf = ttk.Frame(sf)
        cf.pack(fill='x')
        ttk.Checkbutton(cf, text='ほかくパワーの妥協判定（かがやき「ぜんぶ」のとき、ほかくのタイプ一致で成立）',
                        variable=self.v_compromise).pack(anchor='w')
        self.capture_rows.append(cf)

        tf = self.tool_frame
        f = self._row(tf, 'どうぐパワーの種類')
        for i, (value, text) in enumerate(UI_ITEM_CLASSES):
            ttk.Radiobutton(f, text=text, value=value, variable=self.v_item).pack(side='left', padx=(0, 8))
        f = self._row(tf, '2つめのどうぐの種類')
        for value, text in UI_ITEM_CLASSES + [('', '選ばない')]:
            ttk.Radiobutton(f, text=text, value=value, variable=self.v_item2).pack(side='left', padx=(0, 8))
        self._note(tf, '　どうぐの種類は抽選です。1つめか2つめのどちらかが条件のレベルで付けば成功にします（1つめと同じものを選ぶと「選ばない」と同じ）。',
                   pady=(0, 4))
        self._levels(tf, 'どっさりパワーのレベル', self.v_level_size)
        self._levels(tf, 'どうぐパワーのレベル', self.v_level_extra)
        self._note(tab_target, '※ Lv1 の画像（lv1.png）は同梱していないため、「Lv1 以上」は今は「Lv2 以上」と同じ動きです。',
                   side='bottom', pady=(8, 0))

        # --- タブ2: 回数・リセット
        r = tab_run
        self._spin(r, 'ドーナツを作る最大回数', self.v_max_loop, 1, 999999, note='回（ループの上限）', width=10)
        self._spin(r, '1 回あたりのリトライ回数', self.v_retry, 0, 99, note='回（はずれたとき、作り直す回数）')
        ttk.Separator(r).pack(fill='x', pady=6)
        ttk.Checkbutton(r, text='目標を達成しても続ける（ポケセンでセーブしてから再開）', variable=self.v_loop_after).pack(anchor='w')
        self._spin(r, '　達成何回で終えるか', self.v_loop_after_max, 1, 9999, note='回')
        ttk.Separator(r).pack(fill='x', pady=6)
        self._spin(r, '連続はずれでリセット', self.v_no_match, 0, 86400, note='秒（はずれが続いたらバックアップから再開。0 = しない）', width=10)
        self._spin(r, '昼夜切り替えの間隔', self.v_day_night, 1, 1440, note='分（この間隔でイベールセンターへ移動して昼夜を合わせる）')
        ttk.Separator(r).pack(fill='x', pady=6)
        self._radios(r, '動作タイミング', self.v_timing, UI_TIMING_MODES)
        ttk.Checkbutton(r, text='デバッグログを出す', variable=self.v_debug).pack(anchor='w', pady=(4, 0))

        # --- タブ3: 認識・カスタム条件
        d = tab_detect
        ttk.Checkbutton(d, text='カスタム条件（donut_conditions.json など）も使う', variable=self.v_custom).pack(anchor='w')
        f = self._row(d, '　条件ファイル')
        json_files = sorted(fn for fn in os.listdir(SCRIPT_DIR_ABS) if fn.endswith('.json') and fn != CONFIG_FILE)
        ttk.Combobox(f, textvariable=self.v_cond_file, values=json_files, width=30).pack(side='left')
        ttk.Separator(d).pack(fill='x', pady=6)
        ttk.Label(d, text='画像認識のしきい値（0.0〜1.0。上げると厳しく、下げるとゆるく）').pack(anchor='w')
        for key, label in (('threshold_label', 'パワー名（ラベル）'), ('threshold_icon', 'アイコン（タイプ・どうぐ）'),
                           ('threshold_level', 'レベル（Lv2 / Lv3）'), ('threshold_result', '結果画面')):
            self._spin(d, '　' + label, self.v_th[key], 0.0, 1.0, inc=0.01, note=f'（{key}）')

        # --- タブ4: この画面
        u = tab_ui
        ttk.Checkbutton(u, text='Start を押したときに、この画面を出す', variable=self.v_show_ui).pack(anchor='w')
        self._note(u, '外した場合は、次から config.json の値ですぐに開始します。'
                      'もう一度出すには config.json の "show_settings_ui" を true にしてください。')
        self._spin(u, '何もしなければ自動で開始', self.v_ui_timeout, 0, 3600,
                   note='秒（予約・モニターからの開始用。0 = 自動で開始しない）')

        # --- 環境変数の注意
        env_set = [k for k in UI_ENV_KEYS if k in os.environ]
        if env_set:
            self._note(body, '環境変数 {} が設定されていますが、この画面から開始したときは画面の値で動きます。'.format(
                ', '.join(env_set)), danger=True, pady=(6, 0))

        # --- 下のボタン
        bottom = ttk.Frame(body)
        bottom.pack(fill='x', pady=(10, 0))
        ttk.Checkbutton(bottom, text='この設定を config.json に保存する', variable=self.v_save).pack(side='left')
        ttk.Button(bottom, text='キャンセル', command=self._cancel).pack(side='right', padx=3)
        ttk.Button(bottom, text='開始', command=self._ok).pack(side='right', padx=3)
        self.countdown_label = ttk.Label(body, text='', foreground=self.colors['muted'])
        self.countdown_label.pack(anchor='e', pady=(4, 0))

        win.protocol('WM_DELETE_WINDOW', self._cancel)
        win.bind('<Escape>', lambda e: self._cancel())
        # 何か操作したら、自動で開始するのをやめる
        for seq in ('<Button>', '<Key>', '<MouseWheel>'):
            win.bind(seq, self._stop_countdown, add='+')

        self._update_mode()
        self._update_capture()
        self._update_type_order()
        self._start_countdown()

        win.update_idletasks()
        try:
            x = self.root.winfo_rootx() + max(0, (self.root.winfo_width() - win.winfo_width()) // 2)
            y = self.root.winfo_rooty() + max(0, (self.root.winfo_height() - win.winfo_height()) // 3)
            win.geometry(f'+{x}+{y}')
        except tk.TclError:
            pass
        try:
            win.grab_set()
        except tk.TclError:
            pass
        win.focus_set()
        self.root.wait_window(win)
        return self.result

    # ---------------------------------------------------------------- 表示の切り替え
    def _current_recipe(self):
        try:
            i = self.recipe_values.index(self.v_recipe.get())
        except ValueError:
            return None, 'tool'
        return self.recipes[i][0], self.recipes[i][2]

    def _update_mode(self):
        _, mode = self._current_recipe()
        self.shiny_frame.pack_forget()
        self.tool_frame.pack_forget()
        if mode == 'shiny':
            self.shiny_frame.pack(fill='x')
            self.mode_label.configure(text='色違いモード: かがやき × サイズ（＋ほかく）を狙います')
        else:
            self.tool_frame.pack(fill='x')
            self.mode_label.configure(text='どうぐモード: どうぐ × どっさりを狙います')

    def _update_capture(self):
        state = '!disabled' if self.v_capture.get() else 'disabled'
        for row in self.capture_rows:
            for w in row.winfo_children():
                try:
                    w.state([state])
                except Exception:
                    pass

    def _type_toggled(self, t):
        if self.v_types[t].get():
            if t not in self.type_order:
                self.type_order.append(t)
        elif t in self.type_order:
            self.type_order.remove(t)
        self._update_type_order()

    def _update_type_order(self):
        jp = dict(UI_TYPES)
        text = ' → '.join(jp[t] for t in self.type_order) if self.type_order else '（未選択: 「ぜんぶ」のときだけ成立します）'
        self.type_order_label.configure(text='判定する順: ' + text)

    # ---------------------------------------------------------------- 自動で開始
    def _start_countdown(self):
        try:
            sec = int(float(self.v_ui_timeout.get()))
        except ValueError:
            sec = 0
        if sec <= 0:
            return
        self._countdown = sec
        self._tick()

    def _tick(self):
        if self._countdown is None:
            return
        if self._countdown <= 0:
            self.countdown_label.configure(text='')
            self._countdown = None
            self._ok(auto=True)
            return
        self.countdown_label.configure(text=f'あと {self._countdown} 秒操作がなければ、この設定で開始します（何か操作すると止まります）')
        self._countdown -= 1
        self._after_id = self.win.after(1000, self._tick)

    def _stop_countdown(self, event=None):
        if self._countdown is None:
            return
        self._countdown = None
        if self._after_id is not None:
            try:
                self.win.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        self.countdown_label.configure(text='')

    # ---------------------------------------------------------------- 決定
    def _int(self, var, label, lo, hi=None):
        try:
            v = int(float(str(var.get()).strip()))
        except ValueError:
            raise ValueError(f'{label}: 数字を入れてください')
        if v < lo or (hi is not None and v > hi):
            raise ValueError(f'{label}: {lo}〜{hi if hi is not None else ""} の範囲で入れてください')
        return v

    def _float(self, var, label):
        try:
            v = float(str(var.get()).strip())
        except ValueError:
            raise ValueError(f'{label}: 数字を入れてください')
        if not 0.0 <= v <= 1.0:
            raise ValueError(f'{label}: 0.0〜1.0 の範囲で入れてください')
        return round(v, 4)

    def collect(self):
        """画面の値を、config.json と同じ形の辞書にする（入力がおかしいときは ValueError）"""
        recipe, mode = self._current_recipe()
        if recipe is None:
            raise ValueError('レシピを選んでください')
        cfg = dict(self.cfg)
        cfg['recipe'] = recipe
        # タイプ: 1 つも選ばないと、かがやきパワーは「ぜんぶ」のときだけ成立する
        cfg['type'] = ', '.join(self.type_order)
        cfg['size'] = self.v_size.get()
        cfg['item_class'] = self.v_item.get()
        item2 = self.v_item2.get()
        cfg['item_class_2nd'] = '' if item2 == cfg['item_class'] else item2
        cfg['level_size'] = self._int(self.v_level_size, 'レベル', 1, 3)
        cfg['level_extra'] = self._int(self.v_level_extra, 'レベル', 1, 3)
        cfg['enable_capture_power'] = bool(self.v_capture.get())
        cfg['level_capture'] = self._int(self.v_level_capture, 'ほかくパワーのレベル', 1, 3)
        cfg['capture_compromise'] = bool(self.v_compromise.get())
        cfg['max_loop'] = self._int(self.v_max_loop, 'ドーナツを作る最大回数', 1)
        cfg['retry_limit'] = self._int(self.v_retry, 'リトライ回数', 0)
        cfg['enable_loop_after_success'] = bool(self.v_loop_after.get())
        cfg['loop_after_success_max'] = self._int(self.v_loop_after_max, '達成何回で終えるか', 1)
        cfg['no_match_timeout_seconds'] = self._int(self.v_no_match, '連続はずれでリセット', 0)
        cfg['day_night_interval'] = self._int(self.v_day_night, '昼夜切り替えの間隔', 1)
        cfg['timing_mode'] = self.v_timing.get()
        cfg['debug_log'] = bool(self.v_debug.get())
        cfg['use_custom_conditions'] = bool(self.v_custom.get())
        cond = self.v_cond_file.get().strip()
        if not cond:
            raise ValueError('条件ファイル: ファイル名を入れてください')
        if cfg['use_custom_conditions'] and not os.path.exists(os.path.join(SCRIPT_DIR_ABS, cond)):
            raise ValueError(f'条件ファイル: {cond} が見つかりません')
        cfg['conditions_file'] = cond
        for key in self.v_th:
            cfg[key] = self._float(self.v_th[key], key)
        cfg['show_settings_ui'] = bool(self.v_show_ui.get())
        cfg['settings_ui_timeout_seconds'] = self._int(self.v_ui_timeout, '自動で開始するまでの秒数', 0)
        return cfg

    def _ok(self, auto=False):
        try:
            cfg = self.collect()
        except ValueError as e:
            if auto:
                print(f"[Warning] 設定画面: {e}（自動では開始しませんでした）")
            self.messagebox.showinfo('ZA ドーナツ厳選', str(e), parent=self.win)
            return
        if auto:
            print('[System] 設定画面で操作がなかったので、表示していた設定で開始します。')
        self.result = (cfg, bool(self.v_save.get()))
        self._close()

    def _cancel(self):
        self.result = None
        self._close()

    def _close(self):
        self._stop_countdown()
        try:
            self.win.grab_release()
        except Exception:
            pass
        self.win.destroy()


# NAME（文字列リテラル）と VERSION の書き忘れに気づけるようにする
if ZA_DonutV188.NAME != f"ZA ドーナツ厳選 v{VERSION}":
    print(f"[Warning] NAME ({ZA_DonutV188.NAME}) と VERSION ({VERSION}) が合っていません。両方を同じ版に書き換えてください。")
