# ミックスドーナツ どうぐパワー どっさりパワー/どうぐパワー/メガパワー/めんえきパワー/ぼうぎょパワー/とくぼうパワー
# いじげんリリバのみ6,いじげんソクノのみ1,いじげんロゼルのみ1
# サワー、ビター 535
from Commands.Keys import Button, Hat

NAME = "ミックスドーナツ リリバ6,ソクノ1,ロゼル1"
CATEGORY = "rainbow"
TARGETS = ["tool"]

STEPS = [
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 1, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 2, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 6, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 13, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
]