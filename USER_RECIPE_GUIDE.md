# ユーザー独自レシピの作成ガイド
 
 ## 概要
 
 `recipes/` ディレクトリ内に `.py` ファイルを追加するだけで、独自のレシピを作成・使用できます。
 また、[ZAドーナツシミュレーター](https://zadonutsimulator.zephyr.com/)でレシピを自動作成することも可能です。そのダウンロードしたファイルを `recipes/` の下に置いて利用できます。名前は読み込みで利用されるため、わかりやすい名前に変更してください。
 
 
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
 
 1. **ファイル名**: ファイル名は半角英数字のみ推奨（例: `my_recipe.py`）
 2. **拡張子**: 必ず `.py` で終わるようにしてください
 3. **重複**: 既存のレシピ名と同じ名前は避けてください
 4. **エラーハンドリング**: レシピファイルにエラーがある場合、プログラム実行時にエラーメッセージが表示されます
 
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
