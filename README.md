# ZA ドーナツ厳選マクロ v1.9.0

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
                ├── USER_RECIPE_GUIDE.md  # 独自レシピ作成ガイド
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

### 0. レシピ外部ファイル化機能 (v1.9.0)
レシピを外部ファイル（`recipes/` ディレクトリ内の `.py` ファイル）から読み込むことができます。
- **ユーザー独自レシピ**: `recipes/template.py` をコピーして独自のレシピを作成可能
- **動的レシピ検出**: `recipes/` ディレクトリ内の `.py` ファイルを自動検出
- **詳細は `USER_RECIPE_GUIDE.md` を参照**

### 1. タイミング切り替え機能 (Switch1/Switch2)
ハードウェアの読み込み速度に合わせて動作タイミングを最適化できます。
- **Switch2**: 有機ELモデルや高速な読み込み向け
- **Switch1**: 旧型やLiteなどの読み込みが遅いモデル向け

### 2. 多彩な厳選モード
- **色違い厳選 (shiny1~4)**: 指定したタイプの「かがやきパワー」と「サイズ（オヤブン/でかでか/ちびちび）」を同時に狙います。
- **どうぐパワー厳選 (recipe1~3)**: 指定した道具クラス（きのみ、ボール等）のパワーを効率よく集めます。
- **レインボードーナツ (rainbow1~3)**: 特殊な組み合わせのレシピに対応。
  - `TARGETS = ['tool']` を指定し、どうぐパワー優先で動作します。
  - ユーザーが `TARGETS = ['shiny']` に変更することで色違い優先としても使用可能。

### 3. 高度な判定・妥協機能
- **サイズ相互互換 (CrossSize)**: 目標のタイプが出た際、指定した別のサイズでも採用する機能。
- **道具クラス相互互換 (CrossMatch)**: ボールときのみを相互に妥協採用する機能。
- **ほかくパワー検知**: shinyモードにおいて「ほかくパワー」のレベルやタイプを判定し、条件に合致する場合のみ採用します。
- **Jackpot判定**: 特定のタイプを狙っている際でも「オヤブンLv3 + かがやきLv3」が出た場合に特別に終了するオプション。

### 4. 知能的なエラーリカバリ
- **自動エリア判定 & 移動**: マクロ開始時にピクニックメニューからエリアを判定し、メディオプラザ外であれば自動的に正しい場所へ移動して再開します。
- **動的待機**: 固定秒数の待機ではなく、画面の画像認識によって結果画面を検知し、最適なタイミングで次の操作に移ります。
- **リトライ機能**: 作成に失敗（焦げた等）した場合、自動的にレシピ入力からやり直します。

### 5. デバッグ・可視化
- **進行ログの可視化**: どのボタンを何秒押したか、現在のステップがどこかをリアルタイムでログ出力します。
- **判定スコアの表示**: 画像認識の類似度スコアを表示し、しきい値の調整を容易にします。

## 設定方法

### 基本設定

`ZA_donut_correct.py` 内の「ユーザー設定エリア」を書き換えて使用してください。

- `SETTING_RECIPE`: 実行するレシピを選択
    - `shiny1`: 色違い厳選（節約版）
    - `shiny2`: 色違い厳選（タンガのみx8）
    - `shiny3`: 色違い厳選（ほかくパワー付与）
    - `shiny4`: 色違い厳選（ほかくパワー付与・最新版）
    - `recipe1`: どうぐパワー節約レシピ
    - `recipe2`: どうぐパワー重視（カシブx8）
    - `recipe3`: 節約レシピ3
    - `rainbow1~3`: 特殊なレインボードーナツレシピ（`recipes/` ディレクトリから自動検出）
    - `my_recipe`: ユーザーが `recipes/` ディレクトリに追加した独自レシピ
- `SETTING_TYPE`: 狙うポケモンのタイプ（複数指定可能、例: 'Ghost, Dark'）
    - Normal, Fire, Water, Grass, Electric, Ice, Fighting, Poison, Ground, Flying, Psychic, Bug, Rock, Ghost, Dragon, Dark, Steel, Fairy, All
- `SETTING_ITEM_CLASS`: 狙う道具の種類（recipe/rainbow系用）
    - kinomi (きのみ), ball (ボール), coin (コイン), treasure (おたから), special (とくべつ), candy (アメ)
- `SETTING_SIZE`: 狙うサイズ（shiny系用）
    - oyabun (オヤブン), big (でかでか), small (ちびちび)
- `SETTING_TIMING_MODE`: 本体のモデルに合わせて `switch1` または `switch2` を指定
    - switch2: 高速読み込み（有機EL等）
    - switch1: 低速読み込み（旧型・Lite等）

### 独自レシピの作成方法

`recipes/` ディレクトリ内に `.py` ファイルを追加するだけで、独自のレシピを作成・使用できます。

#### レシピ名の決まり方

- **レシピ名 = ファイル名**（`.py` を除外）
- 例: `my_recipe.py` → レシピ名は `my_recipe`
- 例: `shiny1.py` → レシピ名は `shiny1`

#### レシピの選び方

##### 色違い厳選したい場合

| レシピ名 | 説明 | 特徴 |
|---------|------|------|
| `shiny1` | 色違い厳選（節約版） | 比較的少ない素材で作成 |
| `shiny2` | 色違い厳選（タンガのみx8） | タンガの実を8つ使用 |
| `shiny3` | 色違い厳選（ほかくパワー付与） | ほかくパワーが付与されるレシピ |
| `shiny4` | 色違い厳選（最新版） | ほかくパワー付与レシピの改良版 |

使用例:
```python
SETTING_RECIPE = 'shiny1'  # 色違い厳選をしたい場合
```

##### どうぐパワーを集めたい場合

| レシピ名 | 説明 | 特徴 |
|---------|------|------|
| `recipe1` | どうぐパワー節約レシピ | 効率よくパワーを集める |
| `recipe2` | どうぐパワー重視（カシブx8） | カシブの実を8つ使用 |
| `recipe3` | 節約レシピ3 | 別の素材組み合わせ |

使用例:
```python
SETTING_RECIPE = 'recipe1'  # どうぐパワーを集めたい場合
```

##### 特定の素材組み合わせを使いたい場合（rainbow）

| レシピ名 | 素材の組み合わせ | TARGETS（デフォルト） |
|---------|------------------|---------------------|
| `rainbow1` | バコウ1, ウタン1, ナモ4, ロゼル2 | `['tool']` |
| `rainbow2` | バコウ1, ヨロギ1, ハバン1, ロゼル5 | `['tool']` |
| `rainbow3` | ウタン1, ヨロギ1, ナモ4, ロゼル2 | `['tool']` |

**rainbow レシピの使い方:**
- `TARGETS = ['tool']` のまま → どうぐパワーモードで動作
- `TARGETS = ['shiny']` に書き換え → 色違いモードで動作

使用例:
```python
SETTING_RECIPE = 'rainbow1'  # 特定の素材組み合わせでどうぐパワーを集めたい場合
```

#### 独自レシピの作成手順

1. `recipes/template.py` をコピーして名前を変更（例: `my_recipe.py`）
2. `NAME`, `CATEGORY`, `TARGETS`, `STEPS` を編集
3. `SETTING_RECIPE = 'my_recipe'` で指定

詳細は `USER_RECIPE_GUIDE.md` を参照してください。

## 更新履歴

### v1.9.0
- レシピを外部ファイル化（`recipes/` ディレクトリ内の `.py` ファイルから読み込み）
- ユーザーが独自レシピを作成できる機能を追加
- レシピの動的検出機能を実装
- `TARGETS` フィールドを追加して、レシピが対象とするもの（色違い・どうぐパワー）を明確化
- `USER_RECIPE_GUIDE.md` を追加して、独自レシピ作成ガイドを提供

### v1.8.14 (以前)
- 色違い厳選レシピ4 (shiny4) を追加
- recipe3レシピを追加
- デバック機能の修正
- エリア判定を追加
