# ユーザー独自レシピの作成ガイド

## 概要

`recipes/` ディレクトリ内に `.py` ファイルを追加するだけで、独自のレシピを作成・使用できます。

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

| 項目 | 説明 | 例 |
|------|------|-----|
| `NAME` | レシピの表示名 | `"色違い厳選レシピ"` |
| `CATEGORY` | レシピのカテゴリ | `"shiny"`, `"tool"`, `"rainbow"`, `"custom"` |
| `TARGETS` | 対象とするもの | `['shiny']`, `['tool']` |
| `STEPS` | 操作ステップのリスト | `[...]` |

### TARGETS について

`TARGETS` は、そのレシピのどちらのパワーが強いかを指定します：

| 値 | 説明 | 対応する既存レシピ |
|----|------|------------------|
| `['shiny']` | 色違いパワーが強い | shiny1-4 |
| `['tool']` | どうぐパワーが強い | recipe1-3, rainbow1-3 |

**重要**: プログラムの動作は `TARGETS` の値に基づいて決定されます。
- 色違い厳選モードとして動作させたい場合は `TARGETS = ['shiny']`
- どうぐパワー重視モードとして動作させたい場合は `TARGETS = ['tool']`

**rainbow レシピについて**:
- rainbow レシピは素材の組み合わせを示すテンプレートです
- 現在登録されている rainbow1-3 は `TARGETS = ['tool']` に設定されています
- 新規に追加する場合は、どちらのパワーが強いかによって `TARGETS` を `['shiny']` か `['tool']` のどちらかに指定してください

### STEPS の書き方

各ステップは辞書形式で記述します:

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

| 十字キー | ボタン | LRボタン | その他 |
|----------|--------|----------|--------|
| `Hat.TOP` | `Button.A` | `Button.L` | `Button.PLUS` |
| `Hat.BTM` | `Button.B` | `Button.R` | `Button.MINUS` |
| `Hat.LEFT` | `Button.X` |  |  |
| `Hat.RIGHT` | `Button.Y` |  |  |

### パラメータの意味

| パラメータ | 説明 | 単位 | 典型的な値 |
|-----------|------|------|-----------|
| `repeat` | 繰り返し回数 | 回 | 1〜10 |
| `duration` | 1回の押下時間 | 秒 | 0.05〜0.2 |
| `interval` | 押下間隔 | 秒 | 0.05〜0.2 |

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
- `rainbow` → `rainbow1`, `rainbow2`, `rainbow3`（TARGETS はデフォルトで `['shiny']`）
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
