# ZA ドーナツ厳選マクロ v2.0.0

  Pokémon Legends ZA におけるドーナツ作成を自動化し、特定のパワーやサイズを厳選するためのマクロです。

## フォルダ構成

  ```
  Poke-Controller-Modified-Extension/
  └── SerialController/
      └── Commands/
          └── PythonCommands/
              └── ZA_donut_correct/
                  ├── LegendsZA/          # 画像ファイル（テンプレート）
                  │   ├── shiny_label.png
                  │   ├── type_all.png
                  │   └── ... (その他画像)
                  ├── recipes/             # レシピファイル
                  │   ├── shiny1.py
                  │   ├── shiny2.py
                  │   ├── shiny3.py
                  │   ├── shiny4.py
                  │   ├── recipe1.py
                  │   ├── recipe2.py
                  │   ├── recipe3.py
                  │   ├── rainbow1.py
                  │   ├── rainbow2.py
                  │   ├── rainbow3.py
                  │   └── template.py
                  ├── ZA_donut_correct.py  # 本体プログラム
                  ├── config.json          # 設定ファイル（v2.0.0で追加）
                  ├── donut_conditions.json # カスタム条件ファイル
                  ├── USER_CONFIG_GUIDE.md # 設定ガイド（v2.0.0で追加）
                  ├── USER_RECIPE_GUIDE.md  # ユーザー独自レシピ作成ガイド
                  └── README.md            # このファイル
  ```
 
## インストール手順
 
 1. Poke-Controller-Modified-Extension をダウンロード・展開
 2. 以下のフォルダ構成になるようにファイルを配置
 
 ```
 Poke-Controller-Modified-Extension\
 └── SerialController\
     └── Commands\
         └── PythonCommands\
             └── ZA_donut_correct\
                 ├── LegendsZA\
                 ├── recipes\
                 ├── ZA_donut_correct.py
                 ├── USER_RECIPE_GUIDE.md
                 └── README.md
 ```
 
 3. Poke Controller を起動
 4. ZA ドーナツ厳選マクロを実行
 
 ## 主な機能

  ### 0. 設定ファイル外部化機能 (v2.0.0)
  全ての設定を `config.json` で管理できるようになりました。
  - **メインロジック保護**: `ZA_donut_correct.py` を更新しても設定値が上書きされない
  - **一元管理**: 全設定項目を単一のJSONファイルで管理
  - **詳細は `USER_CONFIG_GUIDE.md` を参照**

  ### 1. レシピ外部ファイル化機能 (v1.9.0)
  レシピを外部ファイル（`recipes/` ディレクトリ内の `.py` ファイル）から読み込むことができます。
  - **ユーザー独自レシピ**: `recipes/template.py` をコピーして独自のレシピを作成可能
  - **自動的レシピ検出**: `recipes/` ディレクトリ内の `.py` ファイルを自動検出
  - **詳細は `USER_RECIPE_GUIDE.md` を参照**

  ### 2. 昼夜切り替え機能 (v2.0.0)
  指定した時間間隔で自動的に昼夜を切り替える機能です。
  - **イベールセンター移動**: 設定間隔ごとにイベールセンターへ移動
  - **昼夜自動判定**: 現在時刻（6:00-18:00で昼、それ以外は夜）に応じて自動的に昼夜変更
  - **backup_restart**: 昼夜切り替え前にbackup_restartを実行し、その後ベールへ移動して再開
  - **間隔調整**: `config.json` の `day_night_interval` で分単位で設定（0で無効）
  - **デフォルト**: 60分ごとに実行

  ### 3. タイミング切り替え機能 (Switch1/Switch2)
  ハードウェアの読み込み速度に合わせて動作タイミングを最適化できます。
  - **Switch2**: 有機ELモデルや高速な読み込み向け
  - **Switch1**: 旧型やLiteなどの読み込みが遅いモデル向け

  ### 4. 多彩な厳選モード
  - **色違い厳選 (shiny1~4)**: 指定したタイプの「かがやきパワー」と「サイズ（オヤブン/でかでか/ちびちび）」を同時に狙います。
  - **どうぐパワー厳選 (recipe1~3)**: 指定した道具クラス（きのみ、ボール等）のパワーを効率よく集めます。
    - `TARGETS = ['tool']` となっており、どうぐパワー獲得が主な目的となります。

  ### 5. 目標達成後ループ機能
  目標達成後にポケモンセンター（ベール）へ移動してセーブし、ドーナツ作成を再開する機能です。
  - 設定で有効/無効を切り替え可能
  - 最大ループ回数を設定可能
  - 目標達成回数が最大回数に達すると終了します

**設定項目:**
```python
# 目標達成後に再度ドーナツ作成を行うモード（True/False）
SETTING_ENABLE_LOOP_AFTER_SUCCESS = False
# 目標達成後の最大ループ回数
SETTING_LOOP_AFTER_SUCCESS_MAX = 1
```

**環境変数で指定する場合:**
```bash
# 目標達成後ループを有効にする
ENABLE_LOOP_AFTER_SUCCESS=true

# 最大ループ回数を設定する（例: 3回までループ）
LOOP_AFTER_SUCCESS_MAX=3

python ZA_donut_correct.py
```

**動作例:**
- `SETTING_ENABLE_LOOP_AFTER_SUCCESS = False` または `LOOP_AFTER_SUCCESS_MAX = 1`
  - 1回クリアして終了
- `SETTING_ENABLE_LOOP_AFTER_SUCCESS = True` 且つ `LOOP_AFTER_SUCCESS_MAX = 3`
  - 1回クリア → ポケモンセンターへ移動してセーブ → 再開
  - 2回クリア → ポケモンセンターへ移動してセーブ → 再開
  - 3回クリア → 終了

### 4. 連続マッチなし時のバックアップ再開機能
ドーナツの画像比較で指定秒数以上連続して引っかからない状態が続いたら、backup restartから再開する機能です。
- 長時間マッチしない状況で自動的にリセットを行い、効率よく厳選を継続できます
- 設定で有効/無効を切り替え可能
- 0秒に設定すると機能が無効化されます

**設定項目:**
```python
# 連続マッチなし時のバックアップ再開設定
# ドーナツの画像比較で指定秒数以上連続して引っかからない状態が続いたら、backup restartから再開する
SETTING_NO_MATCH_TIMEOUT_SECONDS = 60
```

**環境変数で指定する場合:**
```bash
# 120秒に設定して実行
NO_MATCH_TIMEOUT_SECONDS=120 python ZA_donut_correct.py

# 機能を無効化
NO_MATCH_TIMEOUT_SECONDS=0 python ZA_donut_correct.py
```

**動作例:**
- `SETTING_NO_MATCH_TIMEOUT_SECONDS = 60`
  - 連続で60秒間マッチしない場合、backup restartから再開
- `SETTING_NO_MATCH_TIMEOUT_SECONDS = 0`
  - 機能が無効化され、通常動作（backup restartはリトライ失敗時のみ実行）


### 5. カスタム条件機能
 外部ファイル（`donut_conditions.json`）から任意の条件を定義し、その条件に一致するドーナツが出現した場合に自動的に終了する機能です。
 
 **対応するパワーテンプレート（5種類）:**
 | テンプレート | type | 説明 |
 |-------------|------|------|
 | かがやきパワー | `shiny` | `attribute`でタイプを指定、`null`でタイプ不問 |
 | サイズ | `size` | `size`で`oyabun`/`big`/`small`を指定 |
 | ほかくパワー | `capture` | `attribute`でタイプを指定、`null`でタイプ不問 |
 | どうぐパワー | `tool` | `class`で`kinomi`/`ball`/`coin`等を指定 |
 | どっさりパワー | `dosari` | どっさりパワー（引数なし） |
 
 **モード別の条件:**
 - **shinyモード時**:
   - かがやきパワー × サイズパワーの組み合わせを狙う
   - オヤブンLv3 × かがやき(特定タイプ)Lv3
   - でかでかLv3 × かがやき(特定タイプ)Lv3
   - ちびちびLv3 × かがやき(特定タイプ)Lv3
   - かがやきパワー × サイズ × ほかくパワー（3パワー構造）
 
 - **toolモード時**:
   - どうぐパワー × どっさりパワーの組み合わせを狙う
   - どっさりLv3 × どうぐ(きのみ/ボール)Lv3
 
 **条件の定義方法:**
 `donut_conditions.json` ファイルを編集することで、モードごとに条件を定義できます。
 
 ```json
 {
   "shiny_conditions": [
     {
       "name": "オヤブン×かがやき",
       "power1": {
         "type": "shiny",
         "attribute": null,
         "min_level": 3
       },
       "power2": {
         "type": "size",
         "size": "oyabun",
         "min_level": 3
       },
       "enabled": true
     }
   ],
   "tool_conditions": [
     {
       "name": "どっさり×どうぐ(きのみ)",
       "power1": {
         "type": "tool",
         "class": "kinomi",
         "min_level": 3
       },
       "power2": {
         "type": "dosari",
         "min_level": 3
       },
       "enabled": true
     }
   ]
 }
 ```
 
 **有効化方法:**
 ```python
 SETTING_USE_CUSTOM_CONDITIONS = True
 ```
 
 **3パワー構造（power3を使用する場合）:**
 カスタム条件では最大3つのパワーを指定できます。
 
 ```json
 {
   "name": "かがやき＋サイズ＋ほかく（3パワー）",
   "power1": {
     "type": "shiny",
     "attribute": null,
     "min_level": 3
   },
   "power2": {
     "type": "size",
     "size": "small",
     "min_level": 3
   },
   "power3": {
     "type": "capture",
     "attribute": null,
     "min_level": 1
   },
   "enabled": false
 }
 ```
 
 **設定例:**
 
 例1: かがやきパワー(Fire)Lv3 × オヤブンLv3 を狙う場合
 ```json
 {
   "shiny_conditions": [
     {
       "name": "かがやき(Fire)Lv3 × オヤブンLv3",
       "power1": {
         "type": "shiny",
         "attribute": "Fire",
         "min_level": 3
       },
       "power2": {
         "type": "size",
         "size": "oyabun",
         "min_level": 3
       },
       "enabled": true
     }
   ],
   "tool_conditions": []
 }
 ```
 
 例2: かがやきパワー(Fire/Ground)Lv3 × オヤブンLv3 を狙う場合（複数タイプ指定）
 ```json
 {
   "shiny_conditions": [
     {
       "name": "かがやき(Fire/Ground)Lv3 × オヤブンLv3",
       "power1": {
         "type": "shiny",
         "attribute": ["Fire", "Ground"],
         "min_level": 3
       },
       "power2": {
         "type": "size",
         "size": "oyabun",
         "min_level": 3
       },
       "enabled": true
     }
   ],
   "tool_conditions": []
 }
 ```
 
 例3: すべてのかがやきパワーLv3 × すべてのサイズLv3 を狙う場合
 ```json
 {
   "shiny_conditions": [
     {
       "name": "オヤブン×かがやき",
       "power1": { "type": "shiny", "attribute": null, "min_level": 3 },
       "power2": { "type": "size", "size": "oyabun", "min_level": 3 },
       "enabled": true
     },
     {
       "name": "でかでか×かがやき",
       "power1": { "type": "shiny", "attribute": null, "min_level": 3 },
       "power2": { "type": "size", "size": "big", "min_level": 3 },
       "enabled": true
     },
     {
       "name": "ちびちび×かがやき",
       "power1": { "type": "shiny", "attribute": null, "min_level": 3 },
       "power2": { "type": "size", "size": "small", "min_level": 3 },
       "enabled": true
     }
   ],
   "tool_conditions": []
 }
 ```
 
 例4: かがやきパワー × サイズ × ほかくパワー（3パワー）を狙う場合
 ```json
 {
   "shiny_conditions": [
     {
       "name": "かがやき＋サイズ＋ほかく（3パワー）",
       "power1": {
         "type": "shiny",
         "attribute": null,
         "min_level": 3
       },
       "power2": {
         "type": "size",
         "size": "small",
         "min_level": 3
       },
       "power3": {
         "type": "capture",
         "attribute": null,
         "min_level": 1
       },
       "enabled": true
     }
   ],
   "tool_conditions": []
 }
 ```
 
 例5: どっさりLv3 × どうぐ(きのみ)Lv3 を狙う場合
 ```json
 {
   "shiny_conditions": [],
   "tool_conditions": [
     {
       "name": "どっさり×どうぐ(きのみ)",
       "power1": { "type": "tool", "class": "kinomi", "min_level": 3 },
       "power2": { "type": "dosari", "min_level": 3 },
       "enabled": true
     }
   ]
 }
 ```
 
 ### 5. 知能的なエラーリカバリ
 - **自動エリア判定 & 移動**: マクロ開始時にピクニックメニューからエリアを判定し、メディオプラザ外であれば自動的に正しい場所へ移動して再開します。
 - **動的待機**: 固定秒数の待機ではなく、画面の画像認識によって結果画面を検知し、最適なタイミングで次の操作に移ります。
 - **リトライ機能**: 作成に失敗（焦げた等）した場合、自動的にレシピ入力からやり直します。
 
 ### 6. デバッグ・可視化
 - **進行ログの可視化**: どのボタンを何秒押したか、現在のステップがどこかをリアルタイムでログ出力します。
 - **判定スコアの表示**: 画像認識の類似度スコアを表示し、閾値の調整を容易にします。
 
  ## 設定方法

  ### 設定ファイル（推奨）

  v2.0.0 から、全ての設定を `config.json` で管理できます。**この方法を推奨します。**

  **設定ファイルの場所:** `config.json`

  **主な設定項目:**
  - `recipe`: 使用するレシピ名
  - `type`: ポケモンのタイプ（shiny系用）
  - `item_class`: 道具の種類（recipe/rainbow系用）
  - `size`: サイズの種類（shiny系用）
  - `timing_mode`: 動作タイミングモード（switch1/switch2）
  - `day_night_interval`: 昼夜切り替え間隔（分）- v2.0.0で追加
  - `enable_loop_after_success`: 目標達成後ループを有効にするか
  - `no_match_timeout_seconds`: 連続マッチなし時のバックアップ再開秒数
  - など...

  **詳細な設定項目と選択肢:** `USER_CONFIG_GUIDE.md` を参照してください。

  ### 環境変数による設定（上書き）

  `config.json` の設定は、環境変数で上書きできます。

  **設定例:**
  ```bash
  # レシピ設定
  export RECIPE=shiny1
  export TYPE="Ghost, Dark"
  export ITEM_CLASS=kinomi
  export SIZE=small

  # 昼夜切り替え設定（v2.0.0）
  export DAY_NIGHT_INTERVAL=60

  # その他の設定
  export TIMING_MODE=switch2
  export DEBUG_LOG=true
  ```

  **優先順位:** 環境変数 > config.json > デフォルト値
 
 ### ほかくパワー検知設定 (shiny系モードでのみ有効)
 
 | 設定項目 | 説明 | デフォルト |
 |-----------|------|-----------|
 | `SETTING_ENABLE_CAPTURE_POWER` | ほかくパワー検知を有効にするか | `False` |
 | `SETTING_LEVEL_CAPTURE` | ほかくパワーの目標レベル（1=妥協/2/3=厳選） | `1` |
 | `SETTING_CAPTURE_COMPROMISE` | ほかくパワー妥協オプション | `True` |
 
 **環境変数で指定する場合:**
 ```bash
 ENABLE_CAPTURE_POWER=true
 CAPTURE_LEVEL=3
 python ZA_donut_correct.py
 ```
 
 ### カスタム条件設定
 
 | 設定項目 | 説明 | デフォルト |
 |-----------|------|-----------|
 | `SETTING_USE_CUSTOM_CONDITIONS` | カスタム条件機能を有効にするか（True/False） | `False` |
 | `SETTING_CONDITIONS_FILE` | 条件ファイルのパス | `donut_conditions.json` |
 
 **環境変数で指定する場合:**
 ```bash
 USE_CUSTOM_CONDITIONS=true
 python ZA_donut_correct.py
 ```
 
 ### ユーザー独自レシピの作成方法
 
 `recipes/` ディレクトリ内に `.py` ファイルを追加するだけで、独自のレシピを作成・使用できます。
 また、[ZAドーナツシミュレーター](https://zadonutsimulator.zephyr.com/)でレシピを自動作成し、ダウンロードしたファイルを `recipes/` フォルダに置いて利用することも可能です。
 ファイル名は読み込み時の名前として利用されるため、わかりやすい名前に変更して使用してください。
 
 
 #### レシピ名の決まり方
 
 - **レシピ名 = ファイル名**（`.py`を除外）
 - 例: `my_recipe.py` → レシピ名は `my_recipe`
 - 例: `shiny1.py` → レシピ名は `shiny1`
 
 #### レシピの選び方
 
 ##### 色違い厳選したい場合
 
 | レシピ名 | 説明                           | 特徴                           |
 | -------- | ------------------------------ | ------------------------------ |
 | `shiny1` | 色違い厳選（節約版）           | 比較的少ない素材で作成         |
 | `shiny2` | 色違い厳選（タングのみx8）     | タングの実を8つ使用            |
 | `shiny3` | 色違い厳選（ほかくパワー付与） | ほかくパワーが付与されるレシピ |
 | `shiny4` | 色違い厳選（最新版）           | ほかくパワー付与レシピの改良版 |
 
 使用例:
 ```python
 SETTING_RECIPE = 'shiny1'  # 色違い厳選をしたい場合
 ```
 
 ##### どうぐパワーを集めたい場合
 
 | レシピ名  | 説明                         | 特徴                   |
 | --------- | ---------------------------- | ---------------------- |
 | `recipe1` | どうぐパワー節約レシピ       | 効率よくパワーを集める |
 | `recipe2` | どうぐパワー重視（カシブx8） | カシブの実を8つ使用    |
 | `recipe3` | 節約レシピ3                  | 別の素材組み合わせ     |
 
 使用例:
 ```python
 SETTING_RECIPE = 'recipe1'  # どうぐパワーを集めたい場合
 ```
 
 ##### 特定の素材組み合わせを使いたい場合（rainbow）
 
 | レシピ名   | 素材の組み合わせ                   | TARGETS（デフォルト） |
 | ---------- | ---------------------------------- | --------------------- |
 | `rainbow1` | バコウ1, ウタン1, ナモ4, ロゼル2   | `['tool']`            |
 | `rainbow2` | バコウ1, ヨロギ1, ハバン1, ロゼル5 | `['tool']`            |
 | `rainbow3` | ウタン1, ヨロギ1, ナモ4, ロゼル2   | `['tool']`            |
 
 **rainbow レシピの使い方:**
 - `TARGETS = ['tool']`（デフォルト）となっており、どうぐパワーモードで動作します。
 
 使用例:
 ```python
 SETTING_RECIPE = 'rainbow1'  # 特定の素材組み合わせでどうぐパワーを集めたい場合
 ```
 
 #### ユーザー独自レシピの作成手順
 
 1. `recipes/template.py` をコピーして名前を変更（例: `my_recipe.py`）
 2. `NAME`, `CATEGORY`, `TARGETS`, `STEPS` を編集
 3. `SETTING_RECIPE = 'my_recipe'` で指定
 
 詳細は `USER_RECIPE_GUIDE.md` を参照してください。
 
   ## 更新履歴

   ### v2.0.0 (Major Update)
   - **設定ファイル外部化機能を追加**
     - 全ての設定を `config.json` で管理可能に
     - メインロジック更新時の設定上書きを防止
     - 環境変数、config.json、デフォルト値の優先順位で設定を適用
   - **昼夜切り替え機能を追加**
     - 指定時間間隔で自動的に昼夜を切り替え
     - イベールセンターへ移動して昼夜変更（現在時刻で自動判定）
     - backup_restart → 昼夜変更 → ベールへ移動 → ドーナツ作成再開のフローを実装
     - 設定項目 `day_night_interval` を追加（分単位、0で無効）
   - **設定ガイドの新規追加**
     - `USER_CONFIG_GUIDE.md` を新規追加
     - 全設定項目の詳細説明と選択肢を記載
   - **フォルダ構成の更新**
     - `config.json` の追加
     - `USER_CONFIG_GUIDE.md` の追加

   ### v1.9.6
  - **連続マッチなし時のバックアップ再開機能を追加**
    - 指定秒数以上連続してドーナツの画像比較で引っかからない状態が続いたら、backup restartから再開する機能
    - 設定項目 `SETTING_NO_MATCH_TIMEOUT_SECONDS` を追加
    - 環境変数 `NO_MATCH_TIMEOUT_SECONDS` で設定可能
    - 0秒に設定すると機能を無効化

  ### v1.9.5
  - テンプレートの追加(donut_conditions.json)

  ### v1.9.4
  - 重複機能の削除

  ### v1.9.3
 - **目標達成後ループ機能を追加**
   - 目標達成後にポケモンセンター（ベール）へ移動してセーブする機能
   - 最大ループ回数の設定（`SETTING_LOOP_AFTER_SUCCESS_MAX`）
   - 環境変数 `ENABLE_LOOP_AFTER_SUCCESS`, `LOOP_AFTER_SUCCESS_MAX` で設定可能
 - **カスタム条件機能の拡張**
   - 3パワー構造（power1, power2, power3）に対応
   - ほかくパワー（capture）のテンプレートを追加
   - どうぐパワー（tool）、どっさりパワー（dosari）のテンプレートを追加
   - カスタム条件のテンプレート前提を明記（5種類）
 - **既存機能の削除（カスタム条件への移行）**
   - タイプ不問オヤブン終了オプション（`SETTING_STOP_ON_ANY_TYPE_OYABUN`）を削除
   - サイズ相互互換（`SETTING_CROSS_SIZE_OYABUN`, `SETTING_CROSS_SIZE_BIG`, `SETTING_CROSS_SIZE_SMALL`）を削除
   - 道具クラス相互互換（`SETTING_CROSS_MATCH`）を削除
   - どうぐパワー単独終了オプション（`SETTING_STOP_ON_TOOL_ONLY`）を削除
 - **バグ修正**
   - ほかくパワーのタイプチェック範囲の不整合を修正（かがやきがAllの場合の挙動）
   - カスタム条件で `attribute: null` の場合、全タイプをチェックするように修正
 
 ### v1.9.2
 - カスタム条件のバグ修正
   - `attribute: null` の場合、`Type_All` を優先的にチェックするように修正
   - 複数の「かがやきパワー」がある場合、全てのマッチング位置をチェックするように修正
   - カスタム条件チェック中のデバッグログを追加
 
 ### v1.9.1
 - カスタム条件機能を追加（外部JSONファイルから条件を読み込んでドーナツを確保）
 - モード別条件対応（shinyモードではかがやき×サイズ、toolモードではどうぐ×どっさり）
 - 複数タイプ指定に対応（`attribute: ["Fire", "Ground"]` 配列形式）
 - `donut_conditions.json` を新規追加
 
 ### v1.9.0
 - レシピを外部ファイル化（`recipes/` ディレクトリ内の `.py` ファイルから読み込み）
 - ユーザーが独自レシピを作成できる機能を追加
 - レシピの自動検出機能を実装
 - `TARGETS` フィールドを追加して、レシピが対象とするもの（色違い・どうぐパワー）を明確化
 - `USER_RECIPE_GUIDE.md` を追加して、独自レシピ作成ガイドを提供
 
 ### v1.8.14 (以前)
 - 色違い厳選レシピ4 (shiny4) を追加
 - recipe3レシピを追加
 - デバッグ機能の修正
 - エリア判定を追加
