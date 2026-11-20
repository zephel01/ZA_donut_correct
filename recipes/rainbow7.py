# ミックスドーナツ どうぐパワー どっさりパワー/どうぐパワー/メガパワー/めんえきパワー/ぼうぎょパワー/とくぼうパワー
# いじげんリリバのみ5,いじげんカシブのみ2,いじげんヨロギのみ1
# サワー、ビター 520
from Commands.Keys import Button, Hat

NAME = "ミックスドーナツ リリバ5,カシブ2,ヨロギ1"
CATEGORY = "rainbow"
TARGETS = ["tool"]

STEPS = [
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 3, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 5, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 3, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 2, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 1, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
]