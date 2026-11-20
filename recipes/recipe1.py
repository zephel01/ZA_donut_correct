# サワードーナツ どうぐパワー どっさりパワー/どうぐパワー/メガパワー/こうげきパワー/とくこうパワー/すばやさパワー/わざパワー
# いじげんロゼルのみ4,いじげんカシブのみ4
from Commands.Keys import Button, Hat

NAME = "サワードーナツ ロゼル4,カシブ4"
CATEGORY = "sour"
TARGETS = ["tool"]

STEPS = [
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 1, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 4, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 5, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 4, 'duration': 0.1, 'interval': 0.1},
]