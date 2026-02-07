# テンプレート: カスタムレシピ
# このファイルをコピーして、新しいレシピを作成してください
#
# 使い方:
# 1. このファイルをコピーして名前を変更（例: my_recipe.py）
# 2. NAME, CATEGORY, TARGETS, STEPS を編集
# 3. プログラム実行時に RECIPE=my_recipe を指定
#
# 利用可能なボタン:
#   - Hat.TOP, Hat.BTM, Hat.LEFT, Hat.RIGHT (十字キー)
#   - Button.A, Button.B, Button.X, Button.Y (ボタン)
#   - Button.L, Button.R (LRボタン)
#   - Button.PLUS, Button.MINUS (プラス/マイナス)
#
# パラメータ:
#   - repeat: 繰り返し回数
#   - duration: 1回の押下時間（秒）
#   - interval: 押下間隔（秒）

from Commands.Keys import Button, Hat

NAME = "カスタムレシピ名"
CATEGORY = "custom"  # shiny, tool, rainbow, custom など
# TARGETS = ['shiny']  # 対象: 色違い（色違いの方がパワーが強い場合）
# TARGETS = ['tool']   # 対象: どうぐパワー（どうぐパワーの方がパワーが強い場合）
TARGETS = ['tool']  # デフォルト: どうぐパワー（必要に応じて変更してください）

STEPS = [
    # ステップ1: カーソル移動（上）
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 1, 'duration': 0.05, 'interval': 0.1},

    # ステップ2: 決定ボタン押下
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},

    # 必要に応じてステップを追加してください
    # {'action': 'pressRep', 'type': Hat.BTM, 'repeat': 1, 'duration': 0.05, 'interval': 0.1},
]
