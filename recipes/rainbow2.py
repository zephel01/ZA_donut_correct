# バコウ1,ヨロギ1,ハバン1,ロゼル5
from Commands.Keys import Button, Hat

NAME = "バコウ1,ヨロギ1,ハバン1,ロゼル5"
CATEGORY = "rainbow"
# TARGETS = ['shiny']  # 対象: 色違い（色違いの方がパワーが強い場合）
# TARGETS = ['tool']   # 対象: どうぐパワー（どうぐパワーの方がパワーが強い場合）
TARGETS = ['tool']  # デフォルト: どうぐパワー

STEPS = [
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 1, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 5, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 4, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 2, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 3, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
]
