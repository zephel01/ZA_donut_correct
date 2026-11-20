# ミックスドーナツ かがやきパワー オヤブンパワー/でかでかパワー/ちびちびパワー/かがやきパワー/ほかくパワー/そうぐうパワー
# いじげんヤチェのみ1,いじげんウタンのみ1,いじげんハバンのみ6
from Commands.Keys import Button, Hat

NAME = "ミックスドーナツ ヤチェ1,ウタン1,ハバン6"
CATEGORY = "shiny"
TARGETS = ['shiny']  # 対象: 色違い

STEPS = [
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 5, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 6, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 4, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 5, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
]
