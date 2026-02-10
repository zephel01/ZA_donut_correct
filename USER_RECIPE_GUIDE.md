# ユーザー独自レシピの作成ガイド
 
 ## 概要
 
 `recipes/` ディレクトリ内に `.py` ファイルを追加するだけで、独自のレシピを作成・使用できます。
 また、[ZAドーナツシミュレーター](https://zadonutsimulator.zephel.com/)でレシピを自動作成することも可能です。そのダウンロードしたファイルを `recipes/` の下に置いて利用できます。名前は読み込みで利用されるため、わかりやすい名前に変更してください。
 
 
 ## レシピ名の決まり方
 
 **重要**: レシピ名は **ファイル名** から決まります。
 
 | ファイル名     | レシピ名    | 説明                                                |
 | -------------- | ----------- | --------------------------------------------------- |
 | `shiny1.py`    | `shiny1`    | ファイル名から `.py` を除去したものがレシピ名になる |
 | `recipe1.py`   | `recipe1`   |                                                     |
 | `rainbow1.py`  | `rainbow1`  |                                                     |
 | `my_recipe.py` | `my_recipe` |                                                     |
 
 ### 新しいレシピを追加する場合
 
 1. `recipes/my_new_recipe.py` を作成
 2. 設定ファイルで `SETTING_RECIPE = 'my_new_recipe'` を指定
 3. プログラム起動時に自動で検出・使用される
 
 ## 作成手順
 
 ### 1. テンプレートをコピー
 
 `recipes/template.py` をコピーして、新しいファイル名で保存してください。
 
 例: `my_custom_recipe.py`
 
 ### 2. レシピファイルを編集
 
 ```python
 # my_custom_recipe.py
 from Commands.Keys import Button, Hat
 
 NAME = "カスタムレシピ名"
 CATEGORY = "custom"  # shiny, tool, rainbow, custom など
 
 STEPS = [
     # ステップ1: カーソル移動（上）
     {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 1, 'duration': 0.05, 'interval': 0.1},
 
     # ステップ2: 決定ボタン押下
     {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
 ]
 ```
 
 ### 3. プログラム実行時にレシピを指定
 
 ```bash
 python ZA_donut_correct.py
 ```
 
 設定ファイル（ZA_donut_correct.py）で以下を設定:
 
 ```python
 SETTING_RECIPE = 'my_custom_recipe'
 ```
 
 または、環境変数で指定:
 
 ```bash
 RECIPE=my_custom_recipe python ZA_donut_correct.py
 ```
 
 ## 詳細設定
 
 ### 必須項目
 
 | 項目       | 説明                 | 例                                           |
 | ---------- | -------------------- | -------------------------------------------- |
 | `NAME`     | レシピの表示名       | `"色違い厳選レシピ"`                         |
 | `CATEGORY` | レシピのカテゴリ     | `"shiny"`, `"tool"`, `"rainbow"`, `"custom"` |
 | `TARGETS`  | 対象とするもの       | `['shiny']`, `['tool']`                      |
 | `STEPS`    | 操作ステップのリスト | `[...]`                                      |
 
 ### TARGETS について
 
 `TARGETS` は、そのレシピのどちらのパワーが強いかを指定します：
 
 | 値          | 説明               | 対応する既存レシピ    |
 | ----------- | ------------------ | --------------------- |
 | `['shiny']` | 色違いパワーが強い | shiny1-4              |
 | `['tool']`  | どうぐパワーが強い | recipe1-3, rainbow1-3 |
 
 **重要**: プログラムの動作は `TARGETS` の値に基づいて決定されます。
 - 色違い厳選モードとして動作させたい場合は `TARGETS = ['shiny']`
 - どうぐパワー重視モードとして動作させたい場合は `TARGETS = ['tool']`
 
 **rainbow レシピについて**:
 - rainbow レシピは素材の組み合わせを示すテンプレートです
 - 現在登録されている rainbow1-3 は `TARGETS = ['tool']` に設定されています
 - 新規に追加する場合は、どちらのパワーが強いかによって `TARGETS` を `['shiny']` か `['tool']` のどちらかに指定してください
 
 ## TARGETS による動作の振り分け
 
 ### 振り分けの仕組み
 
 **重要**: プログラムの動作は `TARGETS` の値によって振り分けられます。レシピ名（ファイル名）は関係ありません。
 
 | TARGETS の値 | 動作モード         | プログラムの動作                                     |
 | ------------ | ------------------ | ---------------------------------------------------- |
 | `['shiny']`  | 色違いモード       | 色違いのタイプ、サイズ、かがやきパワーを判定して厳選 |
 | `['tool']`   | どうぐパワーモード | どうぐパワー（道具の種類）のレベルを判定して厳選     |
 
 ### プログラム内での判定例
 
 ```python
 # 色違いモードの場合
 if 'shiny' in CURRENT_RECIPE['targets']:
     print(f"Target: {ENV_RECIPE} + Type=[{TARGET_TYPE_Display}] & {SIZE}")
     # 色違いのタイプやサイズを参照
 else:
     # どうぐパワーモードの場合
     print(f"Item Class: {INPUT_ITEM_CLASS}")
     # 道具の種類を参照
 ```
 
 ### 具体例
 
 #### 例1: shiny1 レシピ（色違いモード）
 
 ```python
 # recipes/shiny1.py
 TARGETS = ['shiny']
 ```
 
 **動作**:
 - 色違いモードで動作
 - `SETTING_TYPE`（例: 'Ghost', 'Dark'）を参照
 - `SETTING_SIZE`（例: 'small'）を参照
 - 色違い判定を行う
 
 **設定例**:
 ```python
 SETTING_RECIPE = 'shiny1'
 SETTING_TYPE = 'Ghost'
 SETTING_SIZE = 'small'
 ```
 
 #### 例2: recipe1 レシピ（どうぐパワーモード）
 
 ```python
 # recipes/recipe1.py
 TARGETS = ['tool']
 ```
 
 **動作**:
 - どうぐパワーモードで動作
 - `SETTING_ITEM_CLASS`（例: 'kinomi', 'ball'）を参照
 - どうぐパワー判定を行う
 
 **設定例**:
 ```python
 SETTING_RECIPE = 'recipe1'
 SETTING_ITEM_CLASS = 'kinomi'
 ```
 
 #### 例3: rainbow1 レシピ（どうぐパワーモード）
 
 ```python
 # recipes/rainbow1.py
 TARGETS = ['tool']
 ```
 
 **動作**: どうぐパワーモード
 
 **設定例**:
 ```python
 SETTING_RECIPE = 'rainbow1'
 SETTING_ITEM_CLASS = 'kinomi'
 ```
 
 ### rainbow レシピについて
 
 rainbow レシピは特殊な素材の組み合わせを示すレシピです。
 
 | レシピ        | 素材の組み合わせ                   | TARGETS    | 使用モード         |
 | ------------- | ---------------------------------- | ---------- | ------------------ |
 | `rainbow1.py` | バコウ1, ウタン1, ナモ4, ロゼル2   | `['tool']` | どうぐパワーモード |
 | `rainbow2.py` | バコウ1, ヨロギ1, ハバン1, ロゼル5 | `['tool']` | どうぐパワーモード |
 | `rainbow3.py` | ウタン1, ヨロギ1, ナモ4, ロゼル2   | `['tool']` | どうぐパワーモード |
 
 既存の rainbow1-3 レシピは素材の都合上、どうぐパワー（アイテムパワー）の獲得を目的として設計されています。そのため、デフォルトで `TARGETS = ['tool']` に設定されており、どうぐパワーモードとして動作します。
 
 ### 新しいレシピを作成する場合
 
 #### 色違いモードのレシピを作る場合
 
 ```python
 # my_shiny_recipe.py
 from Commands.Keys import Button, Hat
 
 NAME = "カスタム色違いレシピ"
 CATEGORY = "custom"
 TARGETS = ['shiny']  # 色違いモード
 
 STEPS = [
     {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 1, 'duration': 0.05, 'interval': 0.1},
     {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
 ]
 ```
 
 #### どうぐパワーモードのレシピを作る場合
 
 ```python
 # my_tool_recipe.py
 from Commands.Keys import Button, Hat
 
 NAME = "カスタムどうぐパワーレシピ"
 CATEGORY = "custom"
 TARGETS = ['tool']  # どうぐパワーモード
 
 STEPS = [
     {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 1, 'duration': 0.05, 'interval': 0.1},
     {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
 ]
 ```
 
 ### プログラム起動時の確認
 
 プログラム起動時に以下のメッセージで `TARGETS` の値を確認できます：
 
 ```
 [System] Available recipes: my_new_recipe, rainbow1, rainbow2, ...
 [System] Recipe loaded: バコウ1,ウタン1,ナモ4,ロゼル2 (targets: tool)
                                                         ^^^^^^^^^^^^
                                                         ここでTARGETSを確認
 ```
 
 ### まとめ
 
 | 項目          | 重要な点                                            |
 | ------------- | --------------------------------------------------- |
 | レシピ名      | ファイル名から決まる                                |
 | 動作モード    | `TARGETS` の値で決まる（`['shiny']` か `['tool']`） |
 | rainbowレシピ | 素材の組み合わせは固定、どうぐパワーモードで使用    |
 
 ### STEPS の書き方
 
 各ステップは辞書形式で記述します：
 
 ```python
 {
     'action': 'pressRep',      # アクション名（現在は pressRep のみ）
     'type': Hat.TOP,           # ボタン/十字キーの種類
     'repeat': 1,               # 繰り返し回数
     'duration': 0.05,         # 1回の押下時間（秒）
     'interval': 0.1            # 押下間隔（秒）
 }
 ```
 
 ### 利用可能なボタン
 
 | 十字キー    | ボタン     | LRボタン   | その他         |
 | ----------- | ---------- | ---------- | -------------- |
 | `Hat.TOP`   | `Button.A` | `Button.L` | `Button.PLUS`  |
 | `Hat.BTM`   | `Button.B` | `Button.R` | `Button.MINUS` |
 | `Hat.LEFT`  | `Button.X` |            |                |
 | `Hat.RIGHT` | `Button.Y` |            |                |
 
 ### パラメータの意味
 
 | パラメータ | 説明          | 単位 | 典型的な値 |
 | ---------- | ------------- | ---- | ---------- |
 | `repeat`   | 繰り返し回数  | 回   | 1〜10      |
 | `duration` | 1回の押下時間 | 秒   | 0.05〜0.2  |
 | `interval` | 押下間隔      | 秒   | 0.05〜0.2  |
 
 ## サンプルレシピ
 
 ### 例1: 色違いパワーが強いレシピ
 
 ```python
 # shiny_recipe.py
 from Commands.Keys import Button, Hat
 
 NAME = "シンプルレシピ（色違い）"
 CATEGORY = "custom"
 TARGETS = ['shiny']  # 色違いパワーが強い
 
 STEPS = [
     {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 2, 'duration': 0.05, 'interval': 0.1},
     {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
 ]
 ```
 
 ### 例2: どうぐパワーが強いレシピ
 
 ```python
 # tool_recipe.py
 from Commands.Keys import Button, Hat
 
 NAME = "複雑なレシピ（どうぐパワー）"
 CATEGORY = "custom"
 TARGETS = ['tool']  # どうぐパワーが強い
 
 STEPS = [
     # カーソル移動
     {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 1, 'duration': 0.05, 'interval': 0.1},
     # 決定
     {'action': 'pressRep', 'type': Button.A, 'repeat': 3, 'duration': 0.1, 'interval': 0.1},
     # カーソル移動
     {'action': 'pressRep', 'type': Hat.BTM, 'repeat': 2, 'duration': 0.05, 'interval': 0.1},
     # 決定
     {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
 ]
 ```
 
 ## 自動検出機能
 
 `recipes/` ディレクトリ内の `.py` ファイルは、以下の例外を除いて自動的に検出されます:
 
 - `template.py` (テンプレートファイルは無視されます)
 
 プログラム起動時に以下のメッセージが表示されます:
 
 ```
 [System] Available recipes: my_custom_recipe, recipe1, recipe2, ...
 ```
 
 ## 既存の振り分けロジック
 
 既存の振り分けロジックは維持されています:
 
 - `shiny` → `shiny1`, `shiny2`, `shiny3`, `shiny4`
 - `rainbow` → `rainbow1`, `rainbow2`, `rainbow3`（TARGETS はデフォルトで `['tool']`）
 - `2` → `recipe2`
 - その他 → `recipe1`
 
## 注意点

1. **エンコーディング**: ファイルは必ず UTF-8 で保存してください
2. **JSON構文**: JSON構文が正しいことを確認してください（カンマ、括弧など）
3. **タイプ名**: タイプ名は大文字小文字を区別し、正しい綴りで指定してください
4. **レベル指定**: `min_level` は `1`, `2`, `3` のいずれかを指定してください
5. **enabledフラグ**: テストする条件のみ `enabled: true` に設定してください
6. **モード別条件**: shinyモードでは `shiny_conditions`、toolモードでは `tool_conditions` が使用されます

---

## config.json による設定（v1.9.7で追加）

### 概要

v1.9.7 から、設定を外部ファイル `config.json` で管理できるようになりました。これにより、メインロジック（`ZA_donut_correct.py`）を修正する際に設定値が上書きされる問題を回避できます。

### 設定ファイルの場所

```
ZA_donut_correct/
├── ZA_donut_correct.py    # メインプログラム
├── config.json             # 設定ファイル（v1.9.7で追加）
├── recipes/                # レシピディレクトリ
└── ...
```

### 設定項目一覧

| 項目 | 説明 | デフォルト |
|-------|------|----------|
| `recipe` | 使用するレシピ名 | `"recipe1"` |
| `type` | ポケモンのタイプ（shiny系用） | `"Dragon"` |
| `item_class` | 道具の種類（recipe/rainbow系用） | `"kinomi"` |
| `size` | サイズの種類（shiny系用） | `"small"` |
| `level_size` | パワーの許容レベル（サイズ系） | `3` |
| `level_extra` | パワーの許容レベル（その他） | `3` |
| `threshold_label` | 画像認識のしきい値（ラベル） | `0.75` |
| `threshold_icon` | 画像認識のしきい値（アイコン） | `0.75` |
| `threshold_level` | 画像認識のしきい値（レベル） | `0.89` |
| `threshold_result` | 結果画面検知のしきい値 | `0.8` |
| `max_loop` | 最大ループ回数 | `999999` |
| `retry_limit` | リトライ回数 | `2` |
| `debug_log` | デバッグログ出力 | `true` |
| `day_night_interval` | 昼夜切り替え間隔（分） | `60` |
| `enable_loop_after_success` | 目標達成後ループを有効にする | `false` |
| `loop_after_success_max` | 目標達成後の最大ループ回数 | `1` |
| `no_match_timeout_seconds` | 連続マッチなし時のバックアップ再開秒数 | `60` |
| `use_custom_conditions` | カスタム条件を使用する | `false` |
| `conditions_file` | カスタム条件ファイルのパス | `"donut_conditions.json"` |
| `timing_mode` | 動作タイミングモード | `"switch2"` |
| `enable_capture_power` | ほかくパワー検知を使用する | `false` |
| `level_capture` | ほかくパワーの目標レベル | `1` |
| `capture_compromise` | ほかくパワー妥協オプション | `true` |

### 詳細設定

#### 基本設定

**1. recipe: 使用するレシピ名**

色違い厳選:
- `shiny1`   : 色違い厳選レシピ1 (節約版)
- `shiny2`   : 色違い厳選レシピ2 (タンガのみx8)
- `shiny3`   : 色違い厳選レシピ3 (ほかくパワー付与レシピ)
- `shiny4`   : 色違い厳選レシピ4 (ほかくパワー付与レシピ2 New)

どうぐパワー厳選:
- `recipe1`  : どうぐパワー節約レシピ
- `recipe2`  : どうぐパワー重視レシピ/カシブx8
- `recipe3`  : 節約レシピ recipe3

特殊レシピ:
- `rainbow1` : バコウ1,ウタン1,ナモ4,ロゼル2 (TARGETS=['tool'])
- `rainbow2` : バコウ1,ヨロギ1,ハバン1,ロゼル5 (TARGETS=['tool'])
- `rainbow3` : ウタン1,ヨロギ1,ナモ4,ロゼル2 (TARGETS=['tool'])

**2. type: ポケモンのタイプ（shiny系用・複数指定可）**

複数指定: `"Ghost, Dark, Dragon"` のようにカンマ区切りで指定

選択肢:
- Normal, Fire, Water, Grass, Electric, Ice, Fighting, Poison, Ground,
- Flying, Psychic, Bug, Rock, Ghost, Dragon, Dark, Steel, Fairy, All

**3. item_class: 道具の種類（recipe/rainbow系用）**

選択肢:
- `kinomi`   : きのみ
- `ball`     : ボール
- `coin`     : コイン
- `treasure` : 宝物
- `special`  : 特別
- `candy`    : アメ

**4. size: サイズの種類（shiny系用）**

選択肢:
- `oyabun` : オヤブン
- `big`    : でかでか
- `small`  : ちびちび

**5. timing_mode: 動作タイミングモード**

選択肢:
- `switch2` : 有機ELなど読み込みが速い場合 (待機短め・最適化)
- `switch1` : 旧型/Liteなど読み込みが遅い場合 (待機長め・ボタン連打多め)

#### レベル設定

**6. level_size: パワーの許容レベル（サイズ系・どっさり）**

選択肢:
- `3` : 厳選（Lv3のみ）
- `2` : 妥協（Lv2, Lv3）
- `1` : さらに妥協（Lv1, Lv2, Lv3）

**7. level_extra: パワーの許容レベル（かがやき・どうぐ）**

選択肢:
- `3` : 厳選（Lv3のみ）
- `2` : 妥協（Lv2, Lv3）
- `1` : さらに妥協（Lv1, Lv2, Lv3）

#### 感度・認識設定

**8. threshold_label: 画像認識のしきい値（ラベル）**

- 範囲: 0.00 〜 1.00（高いほど厳しい判定）
- デフォルト: 0.75

**9. threshold_icon: 画像認識のしきい値（アイコン）**

- 範囲: 0.00 〜 1.00（高いほど厳しい判定）
- デフォルト: 0.75

**10. threshold_level: 画像認識のしきい値（レベル）**

- 範囲: 0.00 〜 1.00（高いほど厳しい判定）
- デフォルト: 0.89

**11. threshold_result: 結果画面検知のしきい値**

- 範囲: 0.00 〜 1.00（高いほど厳しい判定）
- デフォルト: 0.80

#### 動作設定

**12. max_loop: 最大ループ回数**

- 説明: 繰り返し回数の上限（無限にしたい場合は999999など）
- デフォルト: 999999

**13. retry_limit: リトライ回数**

- 説明: 失敗時のリトライ回数
- デフォルト: 2

**14. debug_log: デバッグログ出力**

- 選択肢:
  - `true` : ログを表示（推奨）
  - `false` : ログを非表示
- デフォルト: true

#### 昼夜切り替え設定（v1.9.7で追加）

**15. day_night_interval: 昼夜切り替え間隔（分）**

- 説明: 指定した分数ごとにイベールセンターで昼夜切り替えを実行
  - 0 に設定すると無効化
- 例:
  - `30`  : 30分ごとに実行
  - `60`  : 60分ごとに実行
  - `0`   : 無効化
- デフォルト: 60

**動作フロー:**
```
時間経過 → backup_restart → イベール移動（昼夜変更） → ベールへ移動 → ドーナツ作成再開
```

**昼夜判定:**
- 6:00〜18:00: 昼
- 18:00〜6:00: 夜

#### 目標達成後ループ設定

**16. enable_loop_after_success: 目標達成後ループを有効にする**

- 選択肢:
  - `true` : 有効（目標達成後もループ続行）
  - `false` : 無効（1回達成で終了）
- デフォルト: false

**17. loop_after_success_max: 目標達成後の最大ループ回数**

- 説明: 何回まで目標達成を繰り返すか
- 例:
  - `1` : 1回達成で終了（無効と同じ）
  - `3` : 最大3回まで達成を繰り返す
- デフォルト: 1

#### 連続マッチなし時のバックアップ再開設定

**18. no_match_timeout_seconds: 連続マッチなし時のバックアップ再開秒数**

- 説明: 指定秒数以上連続してマッチしない場合に、backup restartから再開
  - 0 に設定すると無効化
- 例:
  - `30`  : 30秒以上マッチなしだら再開
  - `60`  : 60秒以上マッチなしだら再開
  - `120` : 120秒以上マッチなしだら再開
  - `0`   : 無効化
- デフォルト: 60

#### カスタム条件設定

**19. use_custom_conditions: カスタム条件を使用する**

- 選択肢:
  - `true` : 有効（donut_conditions.json の条件を使用）
  - `false` : 無効（通常の厳選を実行）
- デフォルト: false

**20. conditions_file: カスタム条件ファイルのパス**

- 説明: カスタム条件が記述されたJSONファイルのパス
- デフォルト: `"donut_conditions.json"`

#### ほかくパワー検知設定（shiny系モードでのみ有効）

**21. enable_capture_power: ほかくパワー検知を使用する**

- 選択肢:
  - `true` : 有効（ほかくパワーも検知対象に含める）
  - `false` : 無効
- デフォルト: false

**22. level_capture: ほかくパワーの目標レベル**

- 選択肢:
  - `3` : 厳選（Lv3のみ）
  - `2` : 妥協（Lv2, Lv3）
  - `1` : さらに妥協（Lv1, Lv2, Lv3）
- デフォルト: 1

**23. capture_compromise: ほかくパワー妥協オプション**

- 説明: trueの場合、かがやきパワーが「ぜんぶ」かつ目標Lv以上で、
  ほかくパワーのタイプがターゲットタイプに含まれていれば採用
- 選択肢:
  - `true` : 有効
  - `false` : 無効
- デフォルト: true

### 設定の優先順位

設定値の優先順位は以下の通りです：

```
環境変数 > config.json > デフォルト値
```

### 環境変数による上書き

config.json の設定は、環境変数で上書きできます。

主な環境変数の例:
```bash
# レシピ設定
export RECIPE=shiny1
export MODE=shiny2
export TYPE="Ghost, Dark"
export ITEM_CLASS=kinomi
export SIZE=small

# レベル設定
export SIZE_LEVEL=3
export EXTRA_LEVEL=3
export CAPTURE_LEVEL=1

# 感度設定
export THRESHOLD_LABEL=0.75
export THRESHOLD_ICON=0.75

# 動作設定
export MAX_LOOP=999999
export RETRY_LIMIT=2
export DEBUG_LOG=true

# 機能設定
export DAY_NIGHT_INTERVAL=60
export NO_MATCH_TIMEOUT_SECONDS=60
export ENABLE_LOOP_AFTER_SUCCESS=false
export LOOP_AFTER_SUCCESS_MAX=1

# カスタム条件
export USE_CUSTOM_CONDITIONS=false

# その他
export TIMING_MODE=switch2
export ENABLE_CAPTURE_POWER=false
```

### 設定例

#### 色違い厳選の設定例

```json
{
  "recipe": "shiny1",
  "type": "Ghost, Dark",
  "size": "small",
  "level_size": 3,
  "level_extra": 3,
  "day_night_interval": 60,
  "timing_mode": "switch2"
}
```

#### どうぐパワー集めの設定例

```json
{
  "recipe": "recipe1",
  "item_class": "kinomi",
  "level_size": 3,
  "level_extra": 3,
  "day_night_interval": 120,
  "enable_loop_after_success": true,
  "loop_after_success_max": 5
}
```

#### 昼夜切り替えを無効化する設定例

```json
{
  "recipe": "shiny1",
  "type": "Dragon",
  "size": "oyabun",
  "day_night_interval": 0,
  "no_match_timeout_seconds": 120
}
```

### 注意点

1. **ファイルエンコーディング**: config.json は UTF-8 で保存してください
2. **JSON構文**: JSON構文が正しいことを確認してください
3. **バックアップ**: 設定変更前はバックアップを取っておくことを推奨
4. **設定の反映**: 設定変更後はプログラムを再起動してください
5. **昼夜切り替え**: day_night_interval を 0 に設定すると機能が無効化されます

 ## トラブルシューティング
 
 ### レシピが認識されない場合
 
 1. ファイル名が `.py` で終わっているか確認
 2. `NAME`, `CATEGORY`, `TARGETS`, `STEPS` が正しく定義されているか確認
 3. 構文エラーがないか確認（Pythonの文法チェック）
 
 ### レシピ実行時にエラーが出る場合
 
 1. `type` に正しいボタン/十字キーを指定しているか確認
 2. `repeat`, `duration`, `interval` が数値であるか確認
 3. `STEPS` がリストであるか確認
 4. `TARGETS` が `['shiny']` か `['tool']` のどちらかであるか確認
 
 ## ユーザー間の共有
 
 独自レシピを他のユーザーと共有する場合:
 
 1. レシピファイル（`.py`）を共有
 2. 相手は `recipes/` ディレクトリに配置
 3. プログラム実行時にレシピ名を指定
 
## カスタム条件ファイルについて

カスタム条件ファイル（`donut_conditions.json`）を使用すると、特定のパワー組み合わせを自動で検知して終了することができます。
詳細は `README.md` の「4. カスタム条件機能」セクションを参照してください。

### ファイル概要

`donut_conditions.json` は、ドーナツ作成時のパワー条件を定義するJSONファイルです。
- ファイル名: `donut_conditions.json`
- 配置場所: `ZA_donut_correct.py` と同じディレクトリ
- エンコード: UTF-8

### JSON構造

```json
{
  "_comment": "コメント",
  "_description": "説明",
  "_note": "補足情報",
  "shiny_conditions": [
    {
      "name": "条件名",
      "_description": "条件の説明",
      "_note": "補足説明",
      "power1": { ... },
      "power2": { ... },
      "power3": { ... },  // 省略可能
      "enabled": true
    }
  ],
  "tool_conditions": [
    {
      "name": "条件名",
      "_description": "条件の説明",
      "_note": "補足説明",
      "power1": { ... },
      "power2": { ... },
      "power3": { ... },  // 省略可能
      "enabled": true
    }
  ]
}
```

### モード別条件

| セクション名 | 対応モード | 説明 |
|-------------|-----------|------|
| `shiny_conditions` | shiny系モード | 色違い厳選モード（shiny1-4）で使用 |
| `tool_conditions` | どうぐパワーモード | レシピ/レインボーモード（recipe1-3, rainbow1-3）で使用 |

### 条件の有効化

各条件には `"enabled"` フィールドがあります：
- `true`: 条件が有効になり、一致すると終了
- `false`: 条件が無効になり、チェックされない
- 省略: デフォルトで `true` として扱われる

### 複数条件の判定

カスタム条件はリスト順にチェックされ、最初に一致した条件で終了します。
- 複数の条件を有効にした場合、上から順にチェック
- 条件に優先順位を持たせたい場合は、リストの順序を調整

### パワーテンプレートの詳細（5種類）

カスタム条件では以下の5種類のパワーテンプレートを使用できます。

#### 1. かがやきパワー (shiny)

かがやきパワーのレベルとタイプを判定します。

| パラメータ | 説明 | 指定可能な値 |
|-----------|------|----------------|
| `type` | パワータイプ | `"shiny"` (固定) |
| `attribute` | タイプ指定 | `null` (タイプ不問) または タイプ名 (`"Fire"`, `"Water"`, 等) または タイプ配列 (`["Fire", "Ground"]`) |
| `min_level` | 目標レベル | `1` (妥協), `2`, `3` (厳選) |

**タイプ指定の例:**
```json
// タイプ不問
"attribute": null

// 単一タイプ
"attribute": "Fire"

// 複数タイプ
"attribute": ["Fire", "Ground"]
```

**対応タイプ一覧:**
Normal, Fire, Water, Grass, Electric, Ice, Fighting, Poison, Ground, Flying, Psychic, Bug, Rock, Ghost, Dragon, Dark, Steel, Fairy

#### 2. サイズパワー (size)

サイズパワーの種類とレベルを判定します。

| パラメータ | 説明 | 指定可能な値 |
|-----------|------|----------------|
| `type` | パワータイプ | `"size"` (固定) |
| `size` | サイズ種類 | `"oyabun"` (オヤブン), `"big"` (でかでか), `"small"` (ちびちび) |
| `min_level` | 目標レベル | `1` (妥協), `2`, `3` (厳選) |

#### 3. ほかくパワー (capture)

ほかくパワーのレベルとタイプを判定します。

| パラメータ | 説明 | 指定可能な値 |
|-----------|------|----------------|
| `type` | パワータイプ | `"capture"` (固定) |
| `attribute` | タイプ指定 | `null` (タイプ不問) または タイプ名 (`"Fire"`, `"Water"`, 等) または タイプ配列 (`["Fire", "Ground"]`) |
| `min_level` | 目標レベル | `1` (妥協), `2`, `3` (厳選) |

**タイプ指定の例:**
```json
// タイプ不問
"attribute": null

// 単一タイプ
"attribute": "Fire"

// 複数タイプ
"attribute": ["Fire", "Ground"]
```

#### 4. どうぐパワー (tool)

どうぐパワーのクラスとレベルを判定します。

| パラメータ | 説明 | 指定可能な値 |
|-----------|------|----------------|
| `type` | パワータイプ | `"tool"` (固定) |
| `class` | アイテムクラス | `"kinomi"` (きのみ), `"ball"` (ボール), `"coin"` (コイン), `"treasure"` (宝物), `"special"` (特別), `"candy"` (アメ) |
| `min_level` | 目標レベル | `1` (妥協), `2`, `3` (厳選) |

#### 5. どっさりパワー (dosari)

どっさりパワーのレベルを判定します。

| パラメータ | 説明 | 指定可能な値 |
|-----------|------|----------------|
| `type` | パワータイプ | `"dosari"` (固定) |
| `min_level` | 目標レベル | `1` (妥協), `2`, `3` (厳選) |

### 3パワー構造 (power3の使用)

カスタム条件では、最大3つのパワーを同時に指定できます。

#### 構造

```json
{
  "name": "条件名",
  "power1": { ... },  // 必須
  "power2": { ... },  // 必須
  "power3": { ... }   // 省略可能
}
```

#### 使用例 (3パワー)

```json
{
  "name": "かがやき＋サイズ＋ほかく",
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
```

#### 動作

- power1, power2, power3 のすべての条件を満たす場合に終了
- power3 を省略した場合、power1 と power2 のみで判定
- power3 は追加の条件として使用可能

### 設定例

#### 例1: オヤブン×かがやき (タイプ不問)

```json
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
```

#### 例2: かがやきパワー(Fire/Ground) × ちびちび (複数タイプ)

```json
{
  "name": "かがやき(Fire/Ground) × ちびちび",
  "power1": {
    "type": "shiny",
    "attribute": ["Fire", "Ground"],
    "min_level": 3
  },
  "power2": {
    "type": "size",
    "size": "small",
    "min_level": 3
  },
  "enabled": true
}
```

#### 例3: どうぐパワー(きのみ) × どっさり (toolモード)

```json
{
  "name": "どうぐパワー(きのみ) × どっさり",
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
```

#### 例4: かがやき＋サイズ＋ほかく (3パワー)

```json
{
  "name": "かがやき＋サイズ＋ほかく",
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
```

### 注意点

1. **エンコーディング**: ファイルは必ず UTF-8 で保存してください
2. **JSON構文**: JSON構文が正しいことを確認してください（カンマ、括弧など）
3. **タイプ名**: タイプ名は大文字小文字を区別し、正しい綴りで指定してください
4. **レベル指定**: `min_level` は `1`, `2`, `3` のいずれかを指定してください
5. **enabledフラグ**: テストする条件のみ `enabled: true` に設定してください
6. **モード別条件**: shinyモードでは `shiny_conditions`、toolモードでは `tool_conditions` が使用されます

