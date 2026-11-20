# ミックスドーナツ どうぐパワー どっさりパワー/どうぐパワー/メガパワー/ほかくパワー/そうぐうパワー/めんえきパワー/ぼうぎょパワー/とくぼうパワー
# いじげんナモのみ5,いじげんロゼルのみ1,いじげんリリバのみ1,いじげんヤチェのみ1
# サワー、フレッシュ 480
from Commands.Keys import Button, Hat

NAME = "ミックスドーナツ ナモ5,ロゼル1,リリバ1,ヤチェ1"
CATEGORY = "rainbow"
TARGETS = ["tool"]

STEPS = [
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 1, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 2, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 1, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 5, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 10, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
]