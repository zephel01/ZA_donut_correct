# ミックスドーナツ どうぐパワー どっさりパワー/どうぐパワー/メガパワー/ほかくパワー/そうぐうパワー/めんえきパワー/ぼうぎょパワー/とくぼうパワー
# いじげんナモのみ5,いじげんカシブのみ1,いじげんヤチェのみ1,いじげんリリバのみ1
# サワー、フレッシュ 490
from Commands.Keys import Button, Hat

NAME = "ミックスドーナツ ナモ5,カシブ1,ヤチェ1,リリバ1"
CATEGORY = "rainbow"
TARGETS = ["tool"]

STEPS = [
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 3, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 1, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 5, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 2, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 8, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
]