# ZA ドーナツ厳選マクロ

![version](https://img.shields.io/badge/version-2.1.0-blue)
[![release](https://img.shields.io/github/v/release/zephel01/ZA_donut_correct?label=release)](https://github.com/zephel01/ZA_donut_correct/releases/latest)
![Poke-Controller](https://img.shields.io/badge/Poke--Controller_Modified_Extension-0.2.0-informational)
[![version check](https://github.com/zephel01/ZA_donut_correct/actions/workflows/version-check.yml/badge.svg)](https://github.com/zephel01/ZA_donut_correct/actions/workflows/version-check.yml)

Pokémon Legends ZA におけるドーナツ作成を自動化し、特定のパワーやサイズを厳選するためのマクロです。

| | |
|---|---|
| **現在のバージョン** | v<!-- version -->2.1.0<!-- /version -->（[更新履歴](CHANGELOG.md)） |
| **動作環境** | Poke-Controller Modified Extension 0.2.0 |
| **マニュアル一覧** | [docs/README.md](docs/README.md) |

> **v2.1.0 の主な変更:** Start を押すと設定画面が開き、config.json の項目を選んでから実行できるようになりました（[設定画面](docs/USER_CONFIG_GUIDE.md#設定画面v210)）。Poke-Controller Modified Extension 0.2.0 に対応しています。詳しくは [CHANGELOG.md](CHANGELOG.md) を参照してください。

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
                │   ├── sour1.py
                │   ├── sour2.py
                │   ├── rainbow1.py
                │   ├── rainbow2.py
                │   ├── rainbow3.py
                │   ├── rainbow4.py
                │   ├── rainbow5.py
                │   ├── rainbow6.py
                │   ├── rainbow7.py
                │   ├── rainbow8.py
                │   └── template.py
                ├── ZA_donut_correct.py  # 本体プログラム
                ├── ZA_backupRestart.py  # 補助: リセット＆復帰のみ
                ├── ZA_day_night.py      # 補助: イベールセンター移動＋時間帯確認
                ├── config.json          # 設定ファイル
                ├── donut_conditions.json # カスタム条件ファイル
                ├── docs/                # マニュアル
                │   ├── README.md                # ドキュメント一覧
                │   ├── USER_CONFIG_GUIDE.md     # 設定ガイド（config.json・設定画面）
                │   ├── USER_RECIPE_GUIDE.md     # 独自レシピ作成ガイド
                │   ├── USER_CONDITIONS_GUIDE.md # カスタム条件ガイド
                │   ├── RECIPES_LIST.md          # 同梱レシピ一覧
                │   ├── IMAGE_TEMPLATES.md       # 画像テンプレート一覧
                │   └── SCRIPTS_GUIDE.md         # 補助スクリプトガイド
                ├── tools/
                │   └── bump_version.py  # 開発用: バージョン更新・チェック
                ├── CHANGELOG.md         # 更新履歴
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
                   ├── docs\
                   ├── ZA_donut_correct.py
                   ├── config.json
                   ├── donut_conditions.json
                   └── README.md
   ```

3. Poke Controller を起動
4. コマンド一覧から「ZA ドーナツ厳選 v<!-- version -->2.1.0<!-- /version -->」を選んで Start
5. 設定画面で条件を選んで「開始」

## 主な機能

### 1. 開始前の設定画面 (v2.1.0)

Start を押すと設定画面が開き、config.json の項目を選んでから実行します。

- **タブで設定**: 狙う条件（色違い／どうぐ）、回数・リセット、認識・カスタム条件
- **config.json に保存**: 選んだ設定をそのまま保存（チェックを外すとその回だけ）
- **自動で開始**: 予約・モニターからの開始用に、一定時間操作がなければ表示中の設定で開始
- **詳細は [docs/USER_CONFIG_GUIDE.md](docs/USER_CONFIG_GUIDE.md#設定画面v210) を参照**

### 2. 設定ファイル外部化機能 (v2.0.0)

全ての設定を `config.json` で管理できます。

- **メインロジック保護**: `ZA_donut_correct.py` を更新しても設定値が上書きされない
- **一元管理**: 全設定項目を単一のJSONファイルで管理
- **詳細は [docs/USER_CONFIG_GUIDE.md](docs/USER_CONFIG_GUIDE.md) を参照**

### 3. レシピ外部ファイル化機能 (v1.9.0)

レシピを外部ファイル（`recipes/` ディレクトリ内の `.py` ファイル）から読み込むことができます。

- **ユーザー独自レシピ**: `recipes/template.py` をコピーして独自のレシピを作成可能
- **自動的レシピ検出**: `recipes/` ディレクトリ内の `.py` ファイルを自動検出
- **詳細は [docs/USER_RECIPE_GUIDE.md](docs/USER_RECIPE_GUIDE.md) を参照**

### 4. 昼夜切り替え機能 (v2.0.0)

指定した時間間隔で自動的に昼夜を切り替える機能です。

- **イベールセンター移動**: 設定間隔ごとにイベールセンターへ移動
- **昼夜自動判定**: 現在時刻（6:00-18:00で昼、それ以外は夜）に応じて自動的に昼夜変更
- **backup_restart**: 昼夜切り替え前にbackup_restartを実行し、その後ベールへ移動して再開
- **間隔調整**: `config.json` の `day_night_interval` で分単位で設定（`0` では無効にならないため、使わない場合は大きい値を指定。[既知の問題](docs/USER_CONFIG_GUIDE.md#既知の問題v200)）
- **デフォルト**: 60分ごとに実行

### 5. タイミング切り替え機能 (Switch1/Switch2)

ハードウェアの読み込み速度に合わせて動作タイミングを最適化できます。

- **Switch2**: 有機ELモデルや高速な読み込み向け
- **Switch1**: 旧型やLiteなどの読み込みが遅いモデル向け

### 6. 多彩な厳選モード

- **色違い厳選 (shiny1~4)**: 指定したタイプの「かがやきパワー」と「サイズ（オヤブン/でかでか/ちびちび）」を同時に狙います。
- **どうぐパワー厳選 (recipe1~3, sour1~2, rainbow1~8)**: 指定した道具クラス（きのみ、ボール等）のパワーと「どっさりパワー」を狙います。
  - `TARGETS = ['tool']` となっており、どうぐパワー獲得が主な目的となります。
  - どうぐ＋どっさりのドーナツにはほかくパワーが付かないため、ほかくパワーの設定は使いません（v2.1.0）。

### 7. 目標達成後ループ機能

目標達成後にポケモンセンター（ベール）へ移動してセーブし、ドーナツ作成を再開する機能です。

- 設定で有効/無効を切り替え可能
- 最大ループ回数を設定可能
- 目標達成回数が最大回数に達すると終了します

**設定項目（config.json）:**

```json
{
  "enable_loop_after_success": false,
  "loop_after_success_max": 1
}
```

**動作例:**

- `enable_loop_after_success: false` または `loop_after_success_max: 1`
  - 1回クリアして終了
- `enable_loop_after_success: true` かつ `loop_after_success_max: 3`
  - 1回クリア → ポケモンセンターへ移動してセーブ → 再開
  - 2回クリア → ポケモンセンターへ移動してセーブ → 再開
  - 3回クリア → 終了

### 8. 連続マッチなし時のバックアップ再開機能

ドーナツの画像比較で指定秒数以上連続して引っかからない状態が続いたら、backup restartから再開する機能です。

- 長時間マッチしない状況で自動的にリセットを行い、効率よく厳選を継続できます
- 0秒に設定すると機能が無効化されます

**設定項目（config.json）:**

```json
{
  "no_match_timeout_seconds": 60
}
```

**動作例:**

- `no_match_timeout_seconds: 60`
  - 連続で60秒間マッチしない場合、backup restartから再開
- `no_match_timeout_seconds: 0`
  - 機能が無効化され、通常動作（backup restartはリトライ失敗時のみ実行）

### 9. カスタム条件機能

外部ファイル（`donut_conditions.json`）から任意の条件を定義し、その条件に一致するドーナツが出現した場合に自動的に終了する機能です。

**詳細な使い方は [docs/USER_CONDITIONS_GUIDE.md](docs/USER_CONDITIONS_GUIDE.md) を参照してください。**

**対応するパワーテンプレート（5種類）:**

| テンプレート | type | 説明 |
|-------------|------|------|
| かがやきパワー | `shiny` | `attribute`でタイプを指定、`null`でタイプ不問 |
| サイズ | `size` | `size`で`oyabun`/`big`/`small`を指定 |
| ほかくパワー | `capture` | `attribute`でタイプを指定、`null`でタイプ不問（色違いモードのみ） |
| どうぐパワー | `tool` | `class`で`kinomi`/`ball`/`coin`等を指定 |
| どっさりパワー | `dosari` | どっさりパワー（引数なし） |

**有効化方法（config.json）:**

```json
{
  "use_custom_conditions": true,
  "conditions_file": "donut_conditions.json"
}
```

### 10. 知能的なエラーリカバリ

- **自動エリア判定 & 移動**: マクロ開始時にピクニックメニューからエリアを判定し、メディオプラザ外であれば自動的に正しい場所へ移動して再開します。
- **動的待機**: 固定秒数の待機ではなく、画面の画像認識によって結果画面を検知し、最適なタイミングで次の操作に移ります。
- **リトライ機能**: 作成に失敗（焦げた等）した場合、自動的にレシピ入力からやり直します。

### 11. デバッグ・可視化

- **進行ログの可視化**: どのボタンを何秒押したか、現在のステップがどこかをリアルタイムでログ出力します。
- **判定スコアの表示**: 画像認識の類似度スコアを表示し、閾値の調整を容易にします。

## 設定方法

### 設定画面（推奨）

v2.1.0 から、Start を押すと開く設定画面で項目を選べます。「config.json に保存する」にチェックがあれば、選んだ内容が `config.json` に保存されます。

### 設定ファイル

`config.json` を直接書くこともできます。

**主な設定項目:**

- `recipe`: 使用するレシピ名
- `type`: ポケモンのタイプ（shiny系用）
- `item_class`: 道具の種類（recipe/rainbow系用）
- `size`: サイズの種類（shiny系用）
- `timing_mode`: 動作タイミングモード（switch1/switch2）
- `day_night_interval`: 昼夜切り替え間隔（分）
- `enable_loop_after_success`: 目標達成後ループを有効にするか
- `no_match_timeout_seconds`: 連続マッチなし時のバックアップ再開秒数
- `show_settings_ui`: Start で設定画面を出すか（v2.1.0）
- など...

**詳細な設定項目と選択肢:** [docs/USER_CONFIG_GUIDE.md](docs/USER_CONFIG_GUIDE.md) を参照してください。

### 環境変数による設定（上書き）

`config.json` の設定は、環境変数で上書きできます。Poke-Controller を起動するシェルで設定してください。設定画面から開始したときは、画面の値が優先されます。

```bash
# レシピ設定
export RECIPE=shiny1
export TYPE="Ghost, Dark"
export ITEM_CLASS=kinomi
export SIZE=small

# 昼夜切り替え設定
export DAY_NIGHT_INTERVAL=60

# その他の設定
export TIMING_MODE=switch2
export DEBUG_LOG=true
```

**優先順位:** 設定画面 > 環境変数 > config.json > デフォルト値

### ほかくパワー検知設定（shiny系モードでのみ有効）

| 設定項目 | 説明 | デフォルト |
|-----------|------|-----------|
| `enable_capture_power` | ほかくパワー検知を有効にするか | `false` |
| `level_capture` | ほかくパワーの目標レベル（1=妥協/2/3=厳選） | `1` |
| `capture_compromise` | ほかくパワー妥協オプション | `true` |

### カスタム条件設定

| 設定項目 | 説明 | デフォルト |
|-----------|------|-----------|
| `use_custom_conditions` | カスタム条件機能を有効にするか（true/false） | `false` |
| `conditions_file` | 条件ファイルのパス | `donut_conditions.json` |

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

| レシピ名 | ドーナツ | きのみと数 | ほかくパワー |
| --- | --- | --- | --- |
| `shiny1` | スイートドーナツ | いじげんタンガのみ4, いじげんハバンのみ4 | 付く |
| `shiny2` | スイートドーナツ | いじげんタンガのみ8 | — |
| `shiny3` | スイートドーナツ | いじげんハバンのみ6, いじげんタンガのみ2 | 付く |
| `shiny4` | ミックスドーナツ | いじげんヤチェのみ1, いじげんウタンのみ1, いじげんハバンのみ6 | 付く |

使用例:

```json
{ "recipe": "shiny1" }
```

##### どうぐパワーを集めたい場合

| レシピ名 | ドーナツ | きのみと数 | TARGETS |
| --- | --- | --- | --- |
| `recipe1` | サワードーナツ | いじげんロゼルのみ4, いじげんカシブのみ4 | `['tool']` |
| `recipe2` | サワードーナツ | いじげんカシブのみ8 | `['tool']` |
| `recipe3` | サワードーナツ | いじげんナモのみ3, いじげんリリバのみ4, いじげんロゼルのみ1 | `['tool']` |
| `sour1` | サワードーナツ | いじげんナモのみ6, いじげんロゼルのみ2 | `['general']` |
| `sour2` | サワードーナツ | いじげんロゼルのみ2, いじげんリリバのみ2, いじげんナモのみ2, いじげんカシブのみ2 | `['general']` |

`sour1`・`sour2` は `TARGETS = ['general']` ですが、`'shiny'` を含まないのでどうぐパワーモードで動作します。

使用例:

```json
{ "recipe": "recipe1" }
```

##### ミックスドーナツ（rainbow）

| レシピ名 | ドーナツ | きのみと数 | TARGETS |
| --- | --- | --- | --- |
| `rainbow1` | ミックスドーナツ | いじげんバコウのみ1, いじげんウタンのみ1, いじげんナモのみ4, いじげんロゼルのみ2 | `['tool']` |
| `rainbow2` | ミックスドーナツ | いじげんバコウのみ1, いじげんヨロギのみ1, いじげんハバンのみ1, いじげんロゼルのみ5 | `['tool']` |
| `rainbow3` | ミックスドーナツ | いじげんウタンのみ1, いじげんヨロギのみ1, いじげんナモのみ4, いじげんロゼルのみ2 | `['tool']` |
| `rainbow4` | ミックスドーナツ | いじげんロゼルのみ6, いじげんウブのみ1, いじげんホズのみ1 | `['tool']` |
| `rainbow5` | ミックスドーナツ | いじげんナモのみ5, いじげんロゼルのみ1, いじげんリリバのみ1, いじげんヤチェのみ1 | `['tool']` |
| `rainbow6` | ミックスドーナツ | いじげんナモのみ5, いじげんカシブのみ1, いじげんヤチェのみ1, いじげんリリバのみ1 | `['tool']` |
| `rainbow7` | ミックスドーナツ | いじげんリリバのみ5, いじげんカシブのみ2, いじげんヨロギのみ1 | `['tool']` |
| `rainbow8` | ミックスドーナツ | いじげんリリバのみ6, いじげんソクノのみ1, いじげんロゼルのみ1 | `['tool']` |

**rainbow レシピの使い方:**

- `TARGETS = ['tool']` となっており、どうぐパワーモードで動作します。

使用例:

```json
{ "recipe": "rainbow1" }
```

Poke-Controller のログや設定画面には、`NAME`（例: `サワードーナツ ロゼル4,カシブ4`。「いじげん」「のみ」を省いた形）で表示されます。各レシピの操作とコメントの見方は [docs/RECIPES_LIST.md](docs/RECIPES_LIST.md) を参照してください。

#### ユーザー独自レシピの作成手順

1. `recipes/template.py` をコピーして名前を変更（例: `my_recipe.py`）
2. `NAME`, `CATEGORY`, `TARGETS`, `STEPS` を編集
3. 設定画面でレシピを選ぶか、config.json で `"recipe": "my_recipe"` を指定

詳細は [docs/USER_RECIPE_GUIDE.md](docs/USER_RECIPE_GUIDE.md) を参照してください。

## バージョンの上げ方（開発者向け）

バージョンは `ZA_donut_correct.py` の `VERSION` と `NAME`、README・docs の版表示、`CHANGELOG.md` にあります。手で書き換えず、次のスクリプトでまとめて更新してください。

```bash
# 1. CHANGELOG.md の「## [Unreleased]」に変更点を書く
# 2. バージョンを上げる（VERSION / NAME / README / docs / CHANGELOG をまとめて更新）
python tools/bump_version.py 2.2.0
# 3. ずれがないか確認（PR では GitHub Actions でも自動で確認されます）
python tools/bump_version.py --check
```

- `NAME` は Poke-Controller Modified Extension 0.2.0 が構文解析だけで読むため、f 文字列にせず文字列リテラルで書きます（スクリプトはそのまま書き換えます）。
- README・docs の版表示は `<!-- version -->2.1.0<!-- /version -->` で囲まれた部分だけが書き換わります。

**リリースの作り方:** main にマージした後、タグと GitHub Release を作ると、上の release バッジに反映されます。

```bash
git checkout main && git pull
V=$(python tools/bump_version.py --print)          # 今のバージョン（例: 2.1.0）
git tag "v$V" && git push origin "v$V"
python tools/bump_version.py --notes > notes.md     # CHANGELOG のこの版の部分
gh release create "v$V" --title "v$V" --notes-file notes.md   # または GitHub の画面から作成
```

## 更新履歴

[CHANGELOG.md](CHANGELOG.md) を参照してください。
