# ミックスドーナツ どうぐパワー こうげきパワー/とくこうパワー/すばやさパワー/わざパワー/どっさりパワー/どうぐパワー/メガパワー
# いじげんロゼルのみ6,いじげんウブのみ1,いじげんホズのみ1
# サワー,スパイシー535
from Commands.Keys import Button, Hat

NAME = "ミックスドーナツ ロゼル6,ウブ1,ホズ1"
CATEGORY = "rainbow"
TARGETS = ["tool"]

STEPS = [
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 1, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 6, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 1, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 18, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
]