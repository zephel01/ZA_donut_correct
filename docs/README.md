# ドキュメント一覧

ZA ドーナツ厳選マクロ（`ZA_donut_correct.py` v2.0.0）のマニュアルです。概要とインストール手順は、ルートの [README.md](../README.md) を参照してください。

## まず読むもの

| ドキュメント | 内容 |
|---|---|
| [USER_CONFIG_GUIDE.md](USER_CONFIG_GUIDE.md) | **config.json の全設定項目**：書き方、**選択肢一覧（タイプ・サイズ・どうぐ・レシピ等の値と日本語名）**、環境変数、不正な値を入れたときの挙動、既知の問題、設定例 |
| [RECIPES_LIST.md](RECIPES_LIST.md) | 同梱レシピの一覧：モード、入力操作、レシピ別の推奨設定 |

## 目的別

| やりたいこと | ドキュメント |
|---|---|
| 狙う条件を細かく決めたい（複数条件、3パワーなど） | [USER_CONDITIONS_GUIDE.md](USER_CONDITIONS_GUIDE.md) |
| 自分でレシピを作りたい | [USER_RECIPE_GUIDE.md](USER_RECIPE_GUIDE.md) |
| 認識がうまくいかない／画像を差し替えたい | [IMAGE_TEMPLATES.md](IMAGE_TEMPLATES.md) |
| 補助スクリプトの使い方、処理の流れ、コマンド一覧に表示されない | [SCRIPTS_GUIDE.md](SCRIPTS_GUIDE.md) |

## ファイルと設定の対応

| ファイル | 置き場所 | 説明しているドキュメント |
|---|---|---|
| `config.json` | 本体と同じフォルダ | USER_CONFIG_GUIDE.md |
| `donut_conditions.json` | 本体と同じフォルダ（`conditions_file` で変更可） | USER_CONDITIONS_GUIDE.md |
| `recipes/*.py` | `recipes/` | RECIPES_LIST.md / USER_RECIPE_GUIDE.md |
| `LegendsZA/*.png` | `LegendsZA/` | IMAGE_TEMPLATES.md |
| `ZA_backupRestart.py` / `ZA_day_night.py` | 本体と同じフォルダ | SCRIPTS_GUIDE.md |

> 設定ファイルなどは `docs/` ではなく、`ZA_donut_correct.py` と同じフォルダに置いてください。
