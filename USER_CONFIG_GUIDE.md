# 設定ガイド（config.json）

## 概要

v1.9.7 から、設定を外部ファイル `config.json` で管理できるようになりました。これにより、メインロジック（`ZA_donut_correct.py`）を修正する際に設定値が上書きされる問題を回避できます。

## 設定ファイルの場所

```
ZA_donut_correct/
├── ZA_donut_correct.py    # メインプログラム
├── config.json             # 設定ファイル（v1.9.7で追加）
├── recipes/                # レシピディレクトリ
├── LegendsZA/              # 画像ファイル
└── ...
```

## 設定項目一覧

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

---

## 詳細設定

### 基本設定

#### 1. recipe: 使用するレシピ名

**色違い厳選:**
- `shiny1`   : 色違い厳選レシピ1 (節約版)
- `shiny2`   : 色違い厳選レシピ2 (タンガのみx8)
- `shiny3`   : 色違い厳選レシピ3 (ほかくパワー付与レシピ)
- `shiny4`   : 色違い厳選レシピ4 (ほかくパワー付与レシピ2 New)

**どうぐパワー厳選:**
- `recipe1`  : どうぐパワー節約レシピ
- `recipe2`  : どうぐパワー重視レシピ/カシブx8
- `recipe3`  : 節約レシピ recipe3

**特殊レシピ:**
- `rainbow1` : バコウ1,ウタン1,ナモ4,ロゼル2 (TARGETS=['tool'])
- `rainbow2` : バコウ1,ヨロギ1,ハバン1,ロゼル5 (TARGETS=['tool'])
- `rainbow3` : ウタン1,ヨロギ1,ナモ4,ロゼル2 (TARGETS=['tool'])

#### 2. type: ポケモンのタイプ（shiny系用・複数指定可）

**複数指定:** `"Ghost, Dark, Dragon"` のようにカンマ区切りで指定

**選択肢:**
- Normal, Fire, Water, Grass, Electric, Ice, Fighting, Poison, Ground,
- Flying, Psychic, Bug, Rock, Ghost, Dragon, Dark, Steel, Fairy, All

#### 3. item_class: 道具の種類（recipe/rainbow系用）

**選択肢:**
- `kinomi`   : きのみ
- `ball`     : ボール
- `coin`     : コイン
- `treasure` : 宝物
- `special`  : 特別
- `candy`    : アメ

#### 4. size: サイズの種類（shiny系用）

**選択肢:**
- `oyabun` : オヤブン
- `big`    : でかでか
- `small`  : ちびちび

#### 5. timing_mode: 動作タイミングモード

**選択肢:**
- `switch2` : 有機ELなど読み込みが速い場合 (待機短め・最適化)
- `switch1` : 旧型/Liteなど読み込みが遅い場合 (待機長め・ボタン連打多め)

---

### レベル設定

#### 6. level_size: パワーの許容レベル（サイズ系・どっさり）

**選択肢:**
- `3` : 厳選（Lv3のみ）
- `2` : 妥協（Lv2, Lv3）
- `1` : さらに妥協（Lv1, Lv2, Lv3）

#### 7. level_extra: パワーの許容レベル（かがやき・どうぐ）

**選択肢:**
- `3` : 厳選（Lv3のみ）
- `2` : 妥協（Lv2, Lv3）
- `1` : さらに妥協（Lv1, Lv2, Lv3）

---

### 感度・認識設定

#### 8. threshold_label: 画像認識のしきい値（ラベル）

- 範囲: 0.00 〜 1.00（高いほど厳しい判定）
- デフォルト: 0.75

#### 9. threshold_icon: 画像認識のしきい値（アイコン）

- 範囲: 0.00 〜 1.00（高いほど厳しい判定）
- デフォルト: 0.75

#### 10. threshold_level: 画像認識のしきい値（レベル）

- 範囲: 0.00 〜 1.00（高いほど厳しい判定）
- デフォルト: 0.89

#### 11. threshold_result: 結果画面検知のしきい値

- 範囲: 0.00 〜 1.00（高いほど厳しい判定）
- デフォルト: 0.80

---

### 動作設定

#### 12. max_loop: 最大ループ回数

- 説明: 繰り返し回数の上限（無限にしたい場合は999999など）
- デフォルト: 999999

#### 13. retry_limit: リトライ回数

- 説明: 失敗時のリトライ回数
- デフォルト: 2

#### 14. debug_log: デバッグログ出力

**選択肢:**
- `true` : ログを表示（推奨）
- `false` : ログを非表示
- デフォルト: true

---

### 昼夜切り替え設定（v1.9.7で追加）

#### 15. day_night_interval: 昼夜切り替え間隔（分）

**説明:** 指定した分数ごとにイベールセンターで昼夜切り替えを実行
- 0 に設定すると無効化

**例:**
- `30`  : 30分ごとに実行
- `60`  : 60分ごとに実行
- `0`   : 無効化

**デフォルト:** 60

**動作フロー:**
```
時間経過 → backup_restart → イベール移動（昼夜変更） → ベールへ移動 → ドーナツ作成再開
```

**昼夜判定:**
- 6:00〜18:00: 昼
- 18:00〜6:00: 夜

---

### 目標達成後ループ設定

#### 16. enable_loop_after_success: 目標達成後ループを有効にする

**選択肢:**
- `true` : 有効（目標達成後もループ続行）
- `false` : 無効（1回達成で終了）
- デフォルト: false

#### 17. loop_after_success_max: 目標達成後の最大ループ回数

**説明:** 何回まで目標達成を繰り返すか

**例:**
- `1` : 1回達成で終了（無効と同じ）
- `3` : 最大3回まで達成を繰り返す

**デフォルト:** 1

---

### 連続マッチなし時のバックアップ再開設定

#### 18. no_match_timeout_seconds: 連続マッチなし時のバックアップ再開秒数

**説明:** 指定秒数以上連続してマッチしない場合に、backup restartから再開
- 0 に設定すると無効化

**例:**
- `30`  : 30秒以上マッチなしだら再開
- `60`  : 60秒以上マッチなしだら再開
- `120` : 120秒以上マッチなしだら再開
- `0`   : 無効化

**デフォルト:** 60

---

### カスタム条件設定

#### 19. use_custom_conditions: カスタム条件を使用する

**選択肢:**
- `true` : 有効（donut_conditions.json の条件を使用）
- `false` : 無効（通常の厳選を実行）
- デフォルト: false

#### 20. conditions_file: カスタム条件ファイルのパス

**説明:** カスタム条件が記述されたJSONファイルのパス
**デフォルト:** `"donut_conditions.json"`

---

### ほかくパワー検知設定（shiny系モードでのみ有効）

#### 21. enable_capture_power: ほかくパワー検知を使用する

**選択肢:**
- `true` : 有効（ほかくパワーも検知対象に含める）
- `false` : 無効
- デフォルト: false

#### 22. level_capture: ほかくパワーの目標レベル

**選択肢:**
- `3` : 厳選（Lv3のみ）
- `2` : 妥協（Lv2, Lv3）
- `1` : さらに妥協（Lv1, Lv2, Lv3）
- デフォルト: 1

#### 23. capture_compromise: ほかくパワー妥協オプション

**説明:** trueの場合、かがやきパワーが「ぜんぶ」かつ目標Lv以上で、
ほかくパワーのタイプがターゲットタイプに含まれていれば採用

**選択肢:**
- `true` : 有効
- `false` : 無効
- デフォルト: true

---

## 設定の優先順位

設定値の優先順位は以下の通りです：

```
環境変数 > config.json > デフォルト値
```

---

## 環境変数による上書き

config.json の設定は、環境変数で上書きできます。

### 主な環境変数の例

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

---

## 設定例

### 色違い厳選の設定例

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

### どうぐパワー集めの設定例

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

### 昼夜切り替えを無効化する設定例

```json
{
  "recipe": "shiny1",
  "type": "Dragon",
  "size": "oyabun",
  "day_night_interval": 0,
  "no_match_timeout_seconds": 120
}
```

---

## 注意点

1. **ファイルエンコーディング**: config.json は UTF-8 で保存してください
2. **JSON構文**: JSON構文が正しいことを確認してください
3. **バックアップ**: 設定変更前はバックアップを取っておくことを推奨
4. **設定の反映**: 設定変更後はプログラムを再起動してください
5. **昼夜切り替え**: day_night_interval を 0 に設定すると機能が無効化されます
6. **環境変数の優先**: 環境変数で設定した値が、config.json の値よりも優先されます

---

## トラブルシューティング

### config.json が読み込まれない場合

1. ファイル名が `config.json` であるか確認
2. ファイルの配置場所が正しいか確認（ZA_donut_correct.py と同じディレクトリ）
3. JSON構文が正しいか確認（カンマ、括弧など）
4. ファイルが UTF-8 で保存されているか確認

### 設定が反映されない場合

1. プログラムを再起動して確認
2. 環境変数が設定されていないか確認（環境変数が優先されます）
3. ログ出力を確認してエラーメッセージがないか確認

---

## フォルダ構成の確認

```
ZA_donut_correct/
├── ZA_donut_correct.py           # メインプログラム
├── config.json                  # 設定ファイル（v1.9.7で追加）
├── donut_conditions.json        # カスタム条件ファイル
├── USER_CONFIG_GUIDE.md         # このファイル（設定ガイド）
├── USER_RECIPE_GUIDE.md        # レシピ作成ガイド
├── README.md                   # メインREADME
├── LegendsZA/                  # 画像ファイル（テンプレート）
│   ├── shiny_label.png
│   ├── type_all.png
│   └── ...
└── recipes/                    # レシピディレクトリ
    ├── shiny1.py
    ├── shiny2.py
    ├── shiny3.py
    ├── shiny4.py
    ├── recipe1.py
    ├── recipe2.py
    ├── recipe3.py
    ├── rainbow1.py
    ├── rainbow2.py
    ├── rainbow3.py
    └── template.py
```
