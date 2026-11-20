# 設定ガイド（config.json）

対象バージョン: `ZA_donut_correct.py` v<!-- version -->2.1.0<!-- /version -->

`config.json` は `ZA_donut_correct.py` の動作をすべて決める設定ファイルです。メインロジック（`ZA_donut_correct.py`）を更新しても、設定値は上書きされません。

---

## 目次

1. [クイックスタート](#クイックスタート)
2. [設定画面（v2.1.0）](#設定画面v210)
3. [ファイルの場所と読み込みルール](#ファイルの場所と読み込みルール)
4. [JSON の書き方の注意](#json-の書き方の注意)
5. [設定項目一覧](#設定項目一覧)
6. [選択肢一覧](#選択肢一覧)
7. [モード別：どの項目が使われるか](#モード別どの項目が使われるか)
8. [各項目の詳細](#各項目の詳細)
9. [判定ロジック（成功条件）](#判定ロジック成功条件)
10. [環境変数による上書き](#環境変数による上書き)
11. [不正な値を入れたときの挙動](#不正な値を入れたときの挙動)
12. [既知の問題（v2.0.0）](#既知の問題v200)
13. [設定例](#設定例)
14. [トラブルシューティング](#トラブルシューティング)

---

## クイックスタート

全項目を書いたテンプレートです。そのまま `config.json` にコピーして使えます。

```json
{
  "recipe": "shiny1",
  "type": "Dragon",
  "item_class": "kinomi",
  "size": "small",
  "level_size": 3,
  "level_extra": 3,
  "threshold_label": 0.75,
  "threshold_icon": 0.75,
  "threshold_level": 0.89,
  "threshold_result": 0.8,
  "max_loop": 999999,
  "retry_limit": 2,
  "debug_log": true,
  "no_match_timeout_seconds": 60,
  "day_night_interval": 60,
  "enable_loop_after_success": false,
  "loop_after_success_max": 1,
  "use_custom_conditions": false,
  "conditions_file": "donut_conditions.json",
  "timing_mode": "switch2",
  "enable_capture_power": false,
  "level_capture": 1,
  "capture_compromise": true,
  "show_settings_ui": true,
  "settings_ui_timeout_seconds": 60
}
```

v2.1.0 では、Start を押すと開く[設定画面](#設定画面v210)で、これらの項目を選べます。config.json を直接書く場合、最低限変更が必要なのは次の項目です。

| やりたいこと | 変更する項目 |
|---|---|
| 色違い厳選 | `recipe`（shiny系）, `type`, `size` |
| どうぐパワー集め | `recipe`（recipe/rainbow系）, `item_class` |
| Switch 1 / Lite で動かす | `timing_mode: "switch1"` |

---

## 設定画面（v2.1.0）

v2.1.0 から、Poke-Controller で **Start を押すと設定画面が開き、項目を選んでから実行**します。config.json を直接書かなくても、ほとんどの項目を画面で変えられます。

### 使い方

1. コマンド一覧で「ZA ドーナツ厳選 v<!-- version -->2.1.0<!-- /version -->」を選び、Start を押す
2. 設定画面で、レシピと各タブの項目を選ぶ
3. 「開始」を押すと、その設定で動き始めます。「キャンセル」（または Esc・ウィンドウを閉じる）なら何もしません

| タブ | 内容 | 対応する項目 |
|---|---|---|
| （上） | レシピ（名前とモードを表示） | `recipe` |
| 狙う条件（色違い） | かがやきのタイプ（複数可。チェックした順に判定）、サイズ、各レベル、ほかくパワー | `type` / `size` / `level_size` / `level_extra` / `enable_capture_power` / `level_capture` / `capture_compromise` |
| 狙う条件（どうぐ） | どうぐの種類、どっさり・どうぐのレベル | `item_class` / `level_size` / `level_extra` |
| 回数・リセット | ドーナツを作る最大回数、リトライ回数、目標達成後も続けるか、連続はずれでリセットする秒数、昼夜切り替えの間隔、動作タイミング、デバッグログ | `max_loop` / `retry_limit` / `enable_loop_after_success` / `loop_after_success_max` / `no_match_timeout_seconds` / `day_night_interval` / `timing_mode` / `debug_log` |
| 認識・カスタム条件 | カスタム条件を使うか、条件ファイル、しきい値 4 つ | `use_custom_conditions` / `conditions_file` / `threshold_*` |
| この画面 | 次から画面を出すか、自動で開始するまでの秒数 | `show_settings_ui` / `settings_ui_timeout_seconds` |

- タブの中身はレシピのモードで切り替わります（色違いレシピなら、かがやき・サイズ・ほかく。どうぐレシピなら、どうぐ・どっさり）。
- 「この設定を config.json に保存する」にチェックがあると（初期値はチェックあり）、開始時に config.json へ書き込みます。ファイルにある項目の順番や、画面に無い項目はそのまま残します。チェックを外すと、その回だけ画面の値で動きます。
- 入力がおかしいとき（数字以外、範囲外、条件ファイルが無いなど）は、メッセージを出して開始しません。
- 画面の初期値は config.json の値です。**画面から開始したときは、環境変数（`RECIPE` など）より画面の値が優先**されます。環境変数が設定されていると、画面に注意が出ます。

### 自動で開始（予約・モニターから開始したとき）

画面を開いたまま `settings_ui_timeout_seconds` 秒（初期値 60 秒）何も操作しないと、表示している設定で自動的に開始します。Poke-Controller-Modified-Extension 0.2.0 の「開始と停止の予約」やモニターの All Start など、PC の前に人がいないときでも止まらないようにするためです。画面をクリックしたりキーを押したりすると、自動で開始するのを止めます。`0` にすると自動では開始しません。

### 画面を出さずに開始する場合

| 状況 | 動き |
|---|---|
| `show_settings_ui` が `false` | 画面を出さず、config.json の値（＋環境変数）で開始。画面に戻すには config.json で `true` にする |
| Web ブラウザ版（PCME 0.2.0）など、Tk の画面が無いとき | 画面を出さず、config.json の値で開始 |
| 実行リスト（連続実行）の中で動かすとき | 画面を出さない。最後に開始したときの設定（初回は config.json の値）で動く |

### 追加した設定項目

| 項目 | 型 | デフォルト | 有効範囲 | 意味 |
|---|---|---|---|---|
| `show_settings_ui` | 真偽値 | `true` | `true` / `false` | Start で設定画面を出すか |
| `settings_ui_timeout_seconds` | 整数 | `60` | 0 以上（秒） | 何も操作しないときに自動で開始するまでの秒数。`0` で自動開始しない |

### Poke-Controller-Modified-Extension 0.2.0 での注意

- コマンド名は「ZA ドーナツ厳選 v<!-- version -->2.1.0<!-- /version -->」です。0.2.0 は `NAME` を構文解析だけで読むため、v2.1.0 では `NAME` を文字列リテラルで書いています（v2.0.0 までの f 文字列では一覧に出ませんでした。[SCRIPTS_GUIDE.md](SCRIPTS_GUIDE.md#poke-controller-のコマンド名name)）。
- どうぐモード（どうぐ＋どっさり）のドーナツには、ほかくパワーは付きません。v2.1.0 では、config の値に関係なくプログラム側でほかくパワーを判定から外します（`enable_capture_power` / `capture_compromise` は無視、ほかくパワーを含む `tool_conditions` のカスタム条件も使いません）。
- 設定画面は Poke-Controller のテーマ（ダークなど）の色に合わせます。
- 設定画面の入力欄・コンボボックスにカーソルがある間は、Poke-Controller 本体の仕組みで、キーボードでの手動操作（ゲーム機へのキー送信）が止まります。

---

## ファイルの場所と読み込みルール

```
ZA_donut_correct/
├── ZA_donut_correct.py
├── config.json              ← ここ（本体と同じフォルダ）
├── donut_conditions.json
├── recipes/
├── LegendsZA/
└── docs/
```

| ルール | 内容 |
|---|---|
| 読み込み場所 | `ZA_donut_correct.py` と**同じフォルダ**の `config.json`（カレントディレクトリではない） |
| ファイル名 | `config.json` 固定（`ZA_donut_correct.py` 冒頭の `CONFIG_FILE` で変更可能） |
| 読み込みタイミング | Poke-Controller がコマンドを読み込んだとき（モジュール読み込み時）。**変更後は Poke-Controller の再起動、またはコマンドの再読み込みが必要** |
| 省略した項目 | デフォルト値で補われる（書きたい項目だけ書いてもよい） |
| 未知のキー | 無視される（エラーにならない。**キー名のタイプミスに気付きにくいので注意**） |
| ファイルが無い | 警告を出して全項目デフォルト値で起動 |
| JSON が壊れている | 警告を出して**全項目デフォルト値**で起動（一部だけ有効にはならない） |
| 優先順位 | `環境変数 > config.json > デフォルト値` |

起動時ログで読み込み結果を確認できます。

```
[System] Config loaded from: /…/ZA_donut_correct/config.json   ← 正常
[Warning] Config file not found: …                               ← ファイルが無い
[Warning] Failed to load config file: Expecting ',' delimiter…   ← JSON 構文エラー
```

---

## JSON の書き方の注意

| NG | OK | 理由 |
|---|---|---|
| `// コメント` / `# コメント` | （書かない） | JSON はコメント非対応。書くと構文エラー → 全項目デフォルト |
| 最後の項目の後ろに `,` | 最後の項目はカンマなし | 末尾カンマは構文エラー |
| `'recipe1'` | `"recipe1"` | 文字列はダブルクォートのみ |
| `True` / `False` | `true` / `false` | 真偽値は小文字 |
| `"level_size": "3"` | `"level_size": 3` | 数値は引用符なし（文字列でも動く項目はあるが非推奨） |
| `"type": ["Fire", "Ground"]` | `"type": "Fire, Ground"` | **`type` は配列非対応。配列にすると起動時にエラー停止** |

保存時の文字コードは **UTF-8** にしてください。

---

## 設定項目一覧

| 項目 | 型 | デフォルト | 有効範囲 / 選択肢 | 環境変数 |
|---|---|---|---|---|
| `recipe` | 文字列 | `"recipe1"` | `recipes/` 内のファイル名（拡張子なし）→ [一覧](#recipe--レシピ) | `RECIPE`（別名 `MODE`） |
| `type` | 文字列 | `"Dradon"` ※ | タイプ名（カンマ区切りで複数可）→ [一覧](#タイプかがやきパワー--ほかくパワー) | `TYPE` |
| `item_class` | 文字列 | `"kinomi"` | `kinomi` / `ball` / `coin` / `treasure` / `special` / `candy` | `ITEM_CLASS` |
| `size` | 文字列 | `"small"` | `oyabun` / `big` / `small` | `SIZE` |
| `level_size` | 整数 | `3` | `1`〜`3` | `SIZE_LEVEL` |
| `level_extra` | 整数 | `3` | `1`〜`3` | `EXTRA_LEVEL` |
| `threshold_label` | 小数 | `0.75` | `0.0`〜`1.0` | `THRESHOLD_LABEL` |
| `threshold_icon` | 小数 | `0.75` | `0.0`〜`1.0` | `THRESHOLD_ICON` |
| `threshold_level` | 小数 | `0.89` | `0.0`〜`1.0` | `THRESHOLD_LEVEL` |
| `threshold_result` | 小数 | `0.80` | `0.0`〜`1.0` | `THRESHOLD_RESULT` |
| `max_loop` | 整数 | `999999` | 1 以上 | `MAX_LOOP` |
| `retry_limit` | 整数 | `2` | 0 以上 | `RETRY_LIMIT` |
| `debug_log` | 真偽値 | `true` | `true` / `false` | `DEBUG_LOG` |
| `no_match_timeout_seconds` | 整数 | `60` | 0 以上（秒、0 で無効） | `NO_MATCH_TIMEOUT_SECONDS` |
| `day_night_interval` | 整数 | `60` | 1 以上（分）※0 は既知の問題あり | `DAY_NIGHT_INTERVAL` |
| `enable_loop_after_success` | 真偽値 | `false` | `true` / `false` | `ENABLE_LOOP_AFTER_SUCCESS` |
| `loop_after_success_max` | 整数 | `1` | 1 以上 | `LOOP_AFTER_SUCCESS_MAX` |
| `use_custom_conditions` | 真偽値 | `false` | `true` / `false` | `USE_CUSTOM_CONDITIONS` |
| `conditions_file` | 文字列 | `"donut_conditions.json"` | 本体フォルダからの相対パス | `CONDITIONS_FILE` |
| `timing_mode` | 文字列 | `"switch2"` | `switch1` / `switch2` | `TIMING_MODE` |
| `enable_capture_power` | 真偽値 | `false` | `true` / `false` | `ENABLE_CAPTURE_POWER` |
| `level_capture` | 整数 | `1` | `1`〜`3` | `CAPTURE_LEVEL` |
| `capture_compromise` | 真偽値 | `true` | `true` / `false` | `ENABLE_CAPTURE_COMPROMISE` |
| `show_settings_ui` | 真偽値 | `true` | `true` / `false` | — |
| `settings_ui_timeout_seconds` | 整数 | `60` | 0 以上（秒、0 で自動開始しない） | — |

※ `type` のデフォルト値はソース上 `"Dradon"`（タイプミス）です。`type` を省略すると色違い判定が成立しません。shiny系では **必ず `type` を書いてください**（[既知の問題](#既知の問題v200)参照）。

---

## 選択肢一覧

種類から選ぶ項目の選択肢をまとめています。値は **左列の英字表記をそのまま** 書いてください（日本語名は書けません）。

### `recipe` — レシピ

`recipes/` 内の `.py` ファイル名（拡張子なし）。同梱分は以下のとおりです（`template.py` は選択不可）。

| 値 | レシピ名（`NAME`） | きのみと数 | モード |
|---|---|---|---|
| `shiny1` | スイートドーナツ タンガ4,ハバン4 | いじげんタンガのみ4, いじげんハバンのみ4 | 色違い |
| `shiny2` | スイートドーナツ タンガ8 | いじげんタンガのみ8 | 色違い |
| `shiny3` | スイートドーナツ ハバン6,タンガ2 | いじげんハバンのみ6, いじげんタンガのみ2 | 色違い |
| `shiny4` | ミックスドーナツ ヤチェ1,ウタン1,ハバン6 | いじげんヤチェのみ1, いじげんウタンのみ1, いじげんハバンのみ6 | 色違い |
| `recipe1` | サワードーナツ ロゼル4,カシブ4 | いじげんロゼルのみ4, いじげんカシブのみ4 | どうぐ |
| `recipe2` | サワードーナツ カシブ8 | いじげんカシブのみ8 | どうぐ |
| `recipe3` | サワードーナツ ナモ3,リリバ4,ロゼル1 | いじげんナモのみ3, いじげんリリバのみ4, いじげんロゼルのみ1 | どうぐ |
| `sour1` | サワードーナツ ナモ6,ロゼル2 | いじげんナモのみ6, いじげんロゼルのみ2 | どうぐ |
| `sour2` | サワードーナツ ロゼル2,リリバ2,ナモ2,カシブ2 | いじげんロゼルのみ2, いじげんリリバのみ2, いじげんナモのみ2, いじげんカシブのみ2 | どうぐ |
| `rainbow1` | ミックスドーナツ バコウ1,ウタン1,ナモ4,ロゼル2 | いじげんバコウのみ1, いじげんウタンのみ1, いじげんナモのみ4, いじげんロゼルのみ2 | どうぐ |
| `rainbow2` | ミックスドーナツ バコウ1,ヨロギ1,ハバン1,ロゼル5 | いじげんバコウのみ1, いじげんヨロギのみ1, いじげんハバンのみ1, いじげんロゼルのみ5 | どうぐ |
| `rainbow3` | ミックスドーナツ ウタン1,ヨロギ1,ナモ4,ロゼル2 | いじげんウタンのみ1, いじげんヨロギのみ1, いじげんナモのみ4, いじげんロゼルのみ2 | どうぐ |
| `rainbow4` | ミックスドーナツ ロゼル6,ウブ1,ホズ1 | いじげんロゼルのみ6, いじげんウブのみ1, いじげんホズのみ1 | どうぐ |
| `rainbow5` | ミックスドーナツ ナモ5,ロゼル1,リリバ1,ヤチェ1 | いじげんナモのみ5, いじげんロゼルのみ1, いじげんリリバのみ1, いじげんヤチェのみ1 | どうぐ |
| `rainbow6` | ミックスドーナツ ナモ5,カシブ1,ヤチェ1,リリバ1 | いじげんナモのみ5, いじげんカシブのみ1, いじげんヤチェのみ1, いじげんリリバのみ1 | どうぐ |
| `rainbow7` | ミックスドーナツ リリバ5,カシブ2,ヨロギ1 | いじげんリリバのみ5, いじげんカシブのみ2, いじげんヨロギのみ1 | どうぐ |
| `rainbow8` | ミックスドーナツ リリバ6,ソクノ1,ロゼル1 | いじげんリリバのみ6, いじげんソクノのみ1, いじげんロゼルのみ1 | どうぐ |

自作レシピを `recipes/` に置いた場合は、そのファイル名も指定できます。詳細は [RECIPES_LIST.md](RECIPES_LIST.md) を参照してください。

### タイプ（かがやきパワー / ほかくパワー）

`config.json` の `type` と、`donut_conditions.json` の `attribute` で共通の値です。

| 値 | 日本語名 | 使用画像 |
|---|---|---|
| `Normal` | ノーマル | `Type_Normal.png` |
| `Fire` | ほのお | `Type_Fire.png` |
| `Water` | みず | `Type_Water.png` |
| `Grass` | くさ | `Type_Grass.png` |
| `Electric` | でんき | `Type_Electric.png` |
| `Ice` | こおり | `Type_Ice.png` |
| `Fighting` | かくとう | `Type_Fighting.png` |
| `Poison` | どく | `Type_Poison.png` |
| `Ground` | じめん | `Type_Ground.png` |
| `Flying` | ひこう | `Type_Flying.png` |
| `Psychic` | エスパー | `Type_Psychic.png` |
| `Bug` | むし | `Type_Bug.png` |
| `Rock` | いわ | `Type_Rock.png` |
| `Ghost` | ゴースト | `Type_Ghost.png` |
| `Dragon` | ドラゴン | `Type_Dragon.png` |
| `Dark` | あく | `Type_Dark.png` |
| `Steel` | はがね | `Type_Steel.png` |
| `Fairy` | フェアリー | `Type_Fairy.png` |

「ぜんぶ」（かがやき: `Type_All.png`）と「すべて」（ほかく: `Type_All2.png`）は値として指定しません。自動で判定されます。

書き方は場所によって異なります。

| 場所 | 1タイプ | 複数タイプ | タイプ不問 | 大文字小文字 |
|---|---|---|---|---|
| `config.json` の `type` | `"Dragon"` | カンマ区切り文字列 `"Ghost, Dark"`（配列は起動時エラー） | 指定不可（ぜんぶは常に判定） | 自動補正される |
| `donut_conditions.json` の `attribute` | `"Fire"` | 配列 `["Fire", "Ground"]` | `null` | **補正なし**。先頭大文字で書く |

> **注意（v2.0.0）:** `attribute` に書いたタイプのアイコン画像は、`config.json` の `type` に含まれていないと読み込まれない場合があります（配列指定・ほかくパワーで発生）。`attribute` で使うタイプは `type` にも書いておいてください。

### `size` — サイズパワー

`config.json` の `size` と、`donut_conditions.json` のサイズパワー（`"type": "size"`）の `size` で共通です。

| 値 | 日本語名 | 使用画像 |
|---|---|---|
| `oyabun` | オヤブン | `oyabun_label.png` |
| `big` | でかでか | `big2_label.png` |
| `small` | ちびちび | `small2_label.png` |

### `item_class` — どうぐパワーの種類

`config.json` の `item_class` と、`donut_conditions.json` のどうぐパワー（`"type": "tool"`）の `class` で共通です。

| 値 | 日本語名 | 使用画像 |
|---|---|---|
| `kinomi` | きのみ | `class_kinomi.png` |
| `ball` | ボール | `class_ball.png` |
| `coin` | コイン | `class_coin.png` |
| `treasure` | 宝物 | `class_treasure.png` |
| `special` | 特別 | `class_special.png` |
| `candy` | アメ | `class_candy.png` |

### `timing_mode` — 動作タイミング

| 値 | 想定機種 |
|---|---|
| `switch2` | 有機ELモデルなど読み込みが速い環境 |
| `switch1` | 旧型 / Lite など読み込みが遅い環境 |

### 真偽値の項目

`true` / `false` のみ（`"true"` や `1` は `false` 扱い）。

| 項目 | `true` のとき |
|---|---|
| `debug_log` | デバッグログを出力 |
| `enable_loop_after_success` | 目標達成後も `loop_after_success_max` 回まで続行 |
| `use_custom_conditions` | `conditions_file` のカスタム条件を使用 |
| `enable_capture_power` | ほかくパワーも成功条件に含める（色違いモード） |
| `capture_compromise` | ほかくパワーの妥協判定を有効にする |

### `level_*` — レベル

`level_size` / `level_extra` / `level_capture` は `1` / `2` / `3`（詳細は [レベル設定](#レベル設定)）。

### 参考：`donut_conditions.json` のパワー種類（`power.type`）

| 値 | 日本語名 | 追加で書く項目 |
|---|---|---|
| `shiny` | かがやきパワー | `attribute`（タイプ / 配列 / `null`） |
| `size` | サイズパワー | `size`（`oyabun` / `big` / `small`） |
| `capture` | ほかくパワー | `attribute`（タイプ / 配列 / `null`） |
| `tool` | どうぐパワー | `class`（`item_class` と同じ値） |
| `dosari` | どっさりパワー | なし |

すべて `min_level`（`1`〜`3`）が必要です。詳細は [USER_CONDITIONS_GUIDE.md](USER_CONDITIONS_GUIDE.md) を参照してください。

---

## モード別：どの項目が使われるか

レシピファイルの `TARGETS` によってモードが決まります（[RECIPES_LIST.md](RECIPES_LIST.md) 参照）。

| 項目 | 色違いモード（`TARGETS=['shiny']`） | どうぐモード（`TARGETS=['tool']`） |
|---|---|---|
| `type` | ✅ かがやきパワーのタイプ | — 無視 |
| `size` | ✅ サイズパワーの種類 | — 無視 |
| `item_class` | — 無視 | ✅ どうぐパワーの種類 |
| `level_size` | ✅ サイズパワーのレベル | ✅ **どっさりパワー**のレベル |
| `level_extra` | ✅ かがやきパワーのレベル | ✅ どうぐパワーのレベル |
| `enable_capture_power` / `level_capture` / `capture_compromise` | ✅ | — 無視 |
| その他（しきい値・ループ・昼夜・カスタム条件など） | ✅ | ✅ |

| 同梱レシピ | モード |
|---|---|
| `shiny1`〜`shiny4` | 色違いモード |
| `recipe1`〜`recipe3`, `sour1`〜`sour2`, `rainbow1`〜`rainbow8` | どうぐモード |

---

## 各項目の詳細

### 基本設定

#### `recipe` — 使用するレシピ名

- `recipes/` フォルダ内の `.py` ファイル名（拡張子なし）を指定します。`template.py` は対象外です。
- 大文字小文字は区別しません（内部で小文字化）。
- 同梱レシピの内容は [RECIPES_LIST.md](RECIPES_LIST.md)、自作方法は [USER_RECIPE_GUIDE.md](USER_RECIPE_GUIDE.md) を参照してください。

**存在しない名前を指定した場合（自動補正）:** 名前に含まれる文字で以下のように読み替えます。

| 名前に含まれる文字 | 読み替え先 |
|---|---|
| `shiny` ＋ `4` / `3` / `1` / それ以外 | `shiny4` / `shiny3` / `shiny1` / `shiny2` |
| `rainbow` ＋ `2` / `3` / それ以外 | `rainbow2` / `rainbow3` / `rainbow1` |
| `2`（上記以外） | `recipe2` |
| 上記以外 | `recipe1` |

ログに `[System] Mode Adjusted -> xxx` と出たら補正が働いています。意図しないレシピで動くことがあるので、レシピ名は正確に書いてください。

#### `type` — かがやきパワーのタイプ（色違いモード）

- 選択肢: 18タイプ（日本語名との対応は [選択肢一覧：タイプ](#タイプかがやきパワー--ほかくパワー)）
- **複数指定:** カンマ区切りの文字列 `"Ghost, Dark, Dragon"`（前後の空白は無視）。指定順に判定し、最初に一致したタイプで成立します。
- 大文字小文字は自動補正されます（`"dragon"` → `Dragon`）。
- 指定タイプに一致しない場合でも、かがやきパワーが**「ぜんぶ」（Type_All）**なら成立扱いになります（自動・無効化不可）。
- `"All"` を指定する必要はありません（上記のとおり常にチェックされます）。
- 名前は `LegendsZA/Type_<名前>.png` と一致する必要があります。存在しない名前（例: `Dradon`）は画像が見つからず、そのタイプは永久に一致しません。

#### `item_class` — どうぐパワーの種類（どうぐモード）

| 値 | 意味 | 使用画像 |
|---|---|---|
| `kinomi` | きのみ | `class_kinomi.png` |
| `ball` | ボール | `class_ball.png` |
| `coin` | コイン | `class_coin.png` |
| `treasure` | 宝物 | `class_treasure.png` |
| `special` | 特別 | `class_special.png` |
| `candy` | アメ | `class_candy.png` |

一覧にない値は補正されず、画像が見つからないため一致しなくなります。

#### `size` — サイズパワーの種類（色違いモード）

| 値 | 意味 | 使用画像 |
|---|---|---|
| `oyabun` | オヤブン | `oyabun_label.png` |
| `big` | でかでか | `big2_label.png` |
| `small` | ちびちび | `small2_label.png` |

一覧にない値は **`oyabun` に自動補正**されます（警告なし）。

#### `timing_mode` — 動作タイミング

| 値 | 想定機種 | 違い |
|---|---|---|
| `switch2` | 有機ELモデルなど読み込みが速い環境 | 待機短め（最適化済み） |
| `switch1` | 旧型 / Lite など読み込みが遅い環境 | 待機長め、ボタン操作が多い |

一覧にない値は警告を出して `switch2` に補正されます。
ドーナツ作成・リトライ・リセット（backupRestart）の待機時間すべてに影響します。食材画面の読み込みが間に合わずレシピ入力がずれる場合は `switch1` を試してください。

---

### レベル設定

`level_size` / `level_extra` / `level_capture` は共通の書式です。

| 値 | 合格とするレベル |
|---|---|
| `3` | Lv3 のみ（厳選） |
| `2` | Lv2, Lv3 |
| `1` | Lv1, Lv2, Lv3 ※ |

※ v2.0.0 では `lv1.png` が同梱されておらず、読み込み処理にも含まれていないため、**`1` を指定しても実質 `2` と同じ（Lv1 は検出されない）**です。Lv1 も拾う方法は [IMAGE_TEMPLATES.md](IMAGE_TEMPLATES.md#lv1-を検出できるようにする) を参照してください。

| 項目 | 対象パワー |
|---|---|
| `level_size` | 色違いモード: サイズパワー / どうぐモード: **どっさりパワー** |
| `level_extra` | 色違いモード: かがやきパワー / どうぐモード: どうぐパワー |
| `level_capture` | ほかくパワー（`enable_capture_power: true` のときのみ） |

注意:
- `4` 以上を指定すると合格レベルが空になり、**永久に一致しません**。
- `0` 以下は `1` と同じ扱いです。
- 数値に変換できない値（`"abc"` など）は `3` として扱われます（`level_capture` も `3` になり、デフォルトの `1` にはなりません）。

---

### 画像認識しきい値

テンプレートマッチング（`cv2.TM_CCOEFF_NORMED`）の類似度スコアに対するしきい値です。高いほど厳しく判定します。

| 項目 | デフォルト | 対象 | 判定 |
|---|---|---|---|
| `threshold_label` | `0.75` | パワー名ラベル（かがやき / サイズ / どうぐ / どっさり / ほかく） | スコア ≥ 値 |
| `threshold_icon` | `0.75` | タイプアイコン・どうぐ種類アイコン | スコア ≥ 値 |
| `threshold_level` | `0.89` | レベル表示（`lv2.png` / `lv3.png`） | スコア > 値 |
| `threshold_result` | `0.80` | 結果画面（`result_text.png`）の検知 | スコア > 値 |

**調整の目安**（`debug_log: true` で判定スコアがログに出ます）:

| 症状 | 対処 |
|---|---|
| 目的のパワーが付いているのに「なし」になる | 該当しきい値を 0.05 刻みで下げる |
| 別タイプ・別レベルで成功判定される（誤検知） | 該当しきい値を上げる |
| Lv2 と Lv3 を取り違える | `threshold_level` を上げる（0.90〜0.93） |
| `Warning: Result detection timed out` が頻発 | `threshold_result` を下げる、または `timing_mode: "switch1"` |

ログの読み方:

```
判定: Size(small)[lv3](0.95) / かがやき(Dragon)[なし](0.62)
       ^ラベル名    ^検出Lv ^スコア
```

---

### 動作設定

#### `max_loop` — 最大ループ回数

ドーナツ作成（＋リトライ）の1サイクルを1回と数えます。上限に達すると終了します。実質無制限にしたい場合は `999999` のままで構いません。

#### `retry_limit` — リトライ回数

1回のドーナツ作成で条件を満たさなかったとき、**リセットせずに**同じ場で作り直す回数です。リトライでも満たさなければ backupRestart（ソフト再起動）でセーブ地点に戻ります。

- `0`: リトライせず毎回リセット
- `2`（デフォルト）: 初回＋リトライ2回 → 不成立ならリセット

#### `debug_log` — デバッグログ

| 値 | 内容 |
|---|---|
| `true` | ボタン操作・待機・ステップ・判定スコアの詳細を出力（推奨） |
| `false` | 主要ログのみ |

`debug_log` に関係なく、毎回の判定時の画面が `debug_captures/BEFORE_*.png`、成功時の画面が `debug_captures/SUCCESS_*.png` に保存されます。

> `debug_captures/` は **Poke-Controller の実行時カレントディレクトリ**（通常は `SerialController/`）に作られます。`ZA_donut_correct/` 内ではありません。長時間動かすと大量に溜まるので定期的に削除してください。

---

### 連続マッチなし時のリセット

#### `no_match_timeout_seconds`

最後の成功（または計測開始）から指定秒数が経過しても成功しない場合、backupRestart を実行してタイマーをリセットします。

- `0`: 無効
- チェックはリトライ処理の後に行われるため、実際のリセットは「指定秒数を過ぎた最初のサイクル終了時」です。
- 1サイクル（作成＋リトライ）にかかる時間より短く設定すると、毎サイクルでリセットされます。

---

### 昼夜切り替え

#### `day_night_interval` — 間隔（分）

指定した分数が経過するたびに、次の流れを実行します。

```
backupRestart（ソフト再起動）
  → イベールセンターへ移動してベンチに座る（時間を進める）
  → ベールへ移動してセーブ
  → ドーナツ作成を再開
```

- 単位は**分**です（内部で秒に変換）。
- 目標の時間帯（昼/夜）は **PC の時計**で決まります（6:00〜17:59 → 昼、それ以外 → 夜）。ゲーム内の時刻を画像で確認する処理はありません。
- **`0` を指定しても無効になりません**（v2.0.0 の既知の問題）。毎ループで昼夜切り替えが実行され、ドーナツ作成が始まりません。昼夜切り替えを使いたくない場合は、当面 `999999` など十分大きい値を指定してください。

---

### 目標達成後ループ

#### `enable_loop_after_success` / `loop_after_success_max`

| 設定 | 動作 |
|---|---|
| `false`（`max` は無関係） | 1回達成で終了 |
| `true` ＋ `max: 1` | 1回達成で終了（`false` と同じ） |
| `true` ＋ `max: 3` | 達成 → ベールへ移動してセーブ → 再開、を繰り返し、3回目の達成で終了 |

達成時のドーナツはセーブで確定するため、そのまま次の厳選に移れます。

---

### カスタム条件

#### `use_custom_conditions` / `conditions_file`

`true` にすると、通常の判定に加えて `conditions_file` に書いた条件のいずれかに一致した場合も成功とします（OR 条件）。条件ファイルの書き方は [USER_CONDITIONS_GUIDE.md](USER_CONDITIONS_GUIDE.md) を参照してください。

- `conditions_file` は `ZA_donut_correct.py` と同じフォルダからの相対パスです。
- ファイルが無い場合は警告を出し、カスタム条件 0 件として続行します。
- JSON 構文エラーの場合は**起動時にエラーで停止**します。
- 色違いモードでは `shiny_conditions`、どうぐモードでは `tool_conditions` が使われます。

---

### ほかくパワー（色違いモードのみ）

#### `enable_capture_power`

`true` にすると、ほかくパワーも成功条件に加わります（サイズ・かがやき・ほかくの3つすべてが必要）。

ほかくパワーのタイプ判定:
1. ほかくパワーが「すべて」（`Type_All2.png`）なら一致
2. かがやきが特定タイプで一致した場合 → `type` に指定したタイプのみチェック
3. かがやきが「ぜんぶ」で一致した場合 → 読み込み済みのタイプアイコン（通常は `type` 指定分）をチェック

#### `level_capture`

ほかくパワーの合格レベル。書式は[レベル設定](#レベル設定)と同じです。

#### `capture_compromise` — ほかくパワー妥協

次の**すべて**を満たすと、ほかくパワーのレベル条件を満たさなくても成功とします。

- `enable_capture_power: true`
- レシピ名に `shiny` を含む
- かがやきパワーが「ぜんぶ」（Type_All）で、かつ `level_extra` の条件を満たす
- ほかくパワーのタイプが `type` のいずれか、または「すべて」
- サイズパワーも条件を満たす

---

## 判定ロジック（成功条件）

```
成功 = カスタム条件のいずれかに一致（use_custom_conditions: true のとき）
     OR ( パワー1 一致 AND パワー2 一致 AND (ほかく一致 OR ほかく妥協成立) )
```

| | パワー1 | パワー2 | ほかく |
|---|---|---|---|
| 色違いモード | サイズ（`size`, `level_size`） | かがやき（`type` または ぜんぶ, `level_extra`） | `enable_capture_power: true` のときのみ必須 |
| どうぐモード | どっさり（`level_size`） | どうぐ（`item_class`, `level_extra`） | 対象外（常に OK） |

---

## 環境変数による上書き

環境変数を設定すると config.json より優先されます。Poke-Controller を起動するシェルで設定してください。

> v2.1.0: [設定画面](#設定画面v210)から開始したときは、画面の値が優先されます（環境変数は使われません）。環境変数が効くのは、`show_settings_ui: false` のときと、画面を出さずに開始したときです。

| 環境変数 | 対応する項目 | 備考 |
|---|---|---|
| `RECIPE` | `recipe` | |
| `MODE` | `recipe` | `RECIPE` が無いときのみ有効（旧名） |
| `TYPE` | `type` | |
| `ITEM_CLASS` | `item_class` | |
| `SIZE` | `size` | |
| `SIZE_LEVEL` | `level_size` | |
| `EXTRA_LEVEL` | `level_extra` | |
| `CAPTURE_LEVEL` | `level_capture` | |
| `THRESHOLD_LABEL` | `threshold_label` | |
| `THRESHOLD_ICON` | `threshold_icon` | |
| `THRESHOLD_LEVEL` | `threshold_level` | |
| `THRESHOLD_RESULT` | `threshold_result` | |
| `MAX_LOOP` | `max_loop` | |
| `RETRY_LIMIT` | `retry_limit` | |
| `DEBUG_LOG` | `debug_log` | `true` 以外はすべて false 扱い |
| `NO_MATCH_TIMEOUT_SECONDS` | `no_match_timeout_seconds` | |
| `DAY_NIGHT_INTERVAL` | `day_night_interval` | 分 |
| `ENABLE_LOOP_AFTER_SUCCESS` | `enable_loop_after_success` | `true` 以外は false |
| `LOOP_AFTER_SUCCESS_MAX` | `loop_after_success_max` | |
| `USE_CUSTOM_CONDITIONS` | `use_custom_conditions` | `true` 以外は false |
| `CONDITIONS_FILE` | `conditions_file` | |
| `TIMING_MODE` | `timing_mode` | |
| `ENABLE_CAPTURE_POWER` | `enable_capture_power` | `true` 以外は false |
| `ENABLE_CAPTURE_COMPROMISE` | `capture_compromise` | `true` 以外は false |

```bash
# 例: 一時的にレシピとタイプだけ変えて起動
export RECIPE=shiny4
export TYPE="Ghost, Dark"
# この後、同じシェルから Poke-Controller を起動する
```

真偽値は文字列 `true`（大文字小文字不問）のみが真です。`1` や `yes` は false になります。

> 設定が config.json どおりに反映されないときは、まず環境変数が残っていないか確認してください（`env | grep -E 'RECIPE|TYPE|SIZE'` など）。

---

## 不正な値を入れたときの挙動

| 項目 | 不正な値の例 | 挙動 | 警告 |
|---|---|---|---|
| JSON 全体 | 構文エラー | 全項目デフォルト値 | あり |
| `recipe` | 存在しない名前 | 名前の一部から自動補正（上表） | ログに `Mode Adjusted` |
| `type` | 配列 `["Fire"]` | **起動時エラーで停止** | 例外 |
| `type` | 存在しないタイプ名 | そのタイプは永久に不一致 | なし |
| `item_class` | 一覧外 | 永久に不一致 | なし |
| `size` | 一覧外 | `oyabun` に補正 | なし |
| `timing_mode` | 一覧外 | `switch2` に補正 | あり |
| `level_*` | 数値以外 | `3` | なし |
| `level_*` | `4` 以上 | 永久に不一致 | なし |
| `threshold_*` / `max_loop` / `retry_limit` / `loop_after_success_max` | 数値以外 | **起動時エラーで停止** | 例外 |
| `no_match_timeout_seconds` | 数値以外 | `60` | なし |
| `day_night_interval` | 数値以外 | `60`分 | なし |
| 真偽値項目 | `"yes"`, `1` など | `false` 扱い | なし |
| キー名 | タイプミス（`"recipie"` など） | 無視され、正しいキーはデフォルト値 | なし |

---

## 既知の問題（v2.0.0）

| # | 内容 | 影響 | 回避策 |
|---|---|---|---|
| 1 | `day_night_interval: 0` で無効にならない | 毎ループで昼夜切り替えが走り、ドーナツ作成に進まない | `999999` など大きい値を指定 |
| 2 | `type` のデフォルト値が `"Dradon"`（タイプミス） | `type` を省略すると色違い判定が成立しない | `type` を必ず明記 |
| 3 | `lv1.png` が同梱されておらず、読み込み対象にも入っていない | レベル指定 `1` が `2` と同じ動作になる | `lv1.png` の追加と、コードへの1行追加（[IMAGE_TEMPLATES.md](IMAGE_TEMPLATES.md#lv1-を検出できるようにする)） |
| 4 | Poke-Controller Modified Extension 0.2.0 以降でコマンド一覧に表示されない | コマンドクラスの `NAME` が f 文字列のため、静的解析で読み取れない | **v2.1.0 で解消**（`NAME` を文字列リテラルに変更。[SCRIPTS_GUIDE.md](SCRIPTS_GUIDE.md#poke-controller-のコマンド名name)） |
| 5 | どうぐモードで `enable_capture_power: true` にすると成立しない | どうぐ＋どっさりのドーナツにはほかくパワーが付かないのに、判定に使っていた | **v2.1.0 で解消**（プログラム側で、色違いモードのときだけ判定に使う） |

---

## 設定例

### 色違い厳選（ゴースト/あく × ちびちび）

```json
{
  "recipe": "shiny1",
  "type": "Ghost, Dark",
  "size": "small",
  "level_size": 3,
  "level_extra": 3,
  "timing_mode": "switch2"
}
```

### 色違い厳選 ＋ ほかくパワー（shiny4）

```json
{
  "recipe": "shiny4",
  "type": "Dragon",
  "size": "oyabun",
  "level_size": 3,
  "level_extra": 3,
  "enable_capture_power": true,
  "level_capture": 2,
  "capture_compromise": true
}
```

### どうぐパワー集め（きのみ、5回達成まで連続）

```json
{
  "recipe": "recipe1",
  "item_class": "kinomi",
  "level_size": 3,
  "level_extra": 3,
  "enable_loop_after_success": true,
  "loop_after_success_max": 5
}
```

### 昼夜切り替えを実質無効にする（既知の問題 #1 の回避）

```json
{
  "recipe": "shiny2",
  "type": "Dragon",
  "size": "oyabun",
  "day_night_interval": 999999,
  "no_match_timeout_seconds": 120
}
```

### Switch 1 / Lite で、認識をやや緩める

```json
{
  "recipe": "shiny1",
  "type": "Fire",
  "size": "big",
  "timing_mode": "switch1",
  "threshold_label": 0.70,
  "threshold_icon": 0.70
}
```

### カスタム条件を併用する

```json
{
  "recipe": "shiny1",
  "type": "Fire",
  "size": "oyabun",
  "use_custom_conditions": true,
  "conditions_file": "donut_conditions.json"
}
```

---

## トラブルシューティング

| 症状 | 確認すること |
|---|---|
| 設定を変えたのに反映されない | Poke-Controller を再起動したか / 環境変数が残っていないか / キー名のタイプミス |
| 起動ログに `Config file not found` | `config.json` が `ZA_donut_correct.py` と同じフォルダにあるか（`docs/` ではない） |
| 起動ログに `Failed to load config file` | JSON 構文（コメント・末尾カンマ・クォート）。https://jsonlint.com 等で検証 |
| 意図しないレシピで動く | ログの `Mode Adjusted ->` を確認し、`recipe` 名を `recipes/` のファイル名と一致させる |
| 色違いが一度も成立しない | `type` を書いているか / タイプ名のスペル / `size` の値 |
| ドーナツを作らず移動ばかりする | `day_night_interval` が `0` になっていないか |
| 毎回すぐリセットされる | `no_match_timeout_seconds` が1サイクルより短くないか |
| コマンド一覧に出てこない | `NAME` が文字列リテラルか（f 文字列・変数は不可。既知の問題 #4）。直したら F5 で再読み込み |

---

## 関連ドキュメント

- [README.md](README.md) - ドキュメント一覧
- [RECIPES_LIST.md](RECIPES_LIST.md) - 同梱レシピ一覧
- [USER_RECIPE_GUIDE.md](USER_RECIPE_GUIDE.md) - 独自レシピの作成
- [USER_CONDITIONS_GUIDE.md](USER_CONDITIONS_GUIDE.md) - カスタム条件（donut_conditions.json）
- [IMAGE_TEMPLATES.md](IMAGE_TEMPLATES.md) - 画像テンプレート
- [SCRIPTS_GUIDE.md](SCRIPTS_GUIDE.md) - 補助スクリプト・Poke-Controller 連携
