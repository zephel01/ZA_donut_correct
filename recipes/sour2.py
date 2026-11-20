# サワードーナツ どっさりパワー/どうぐパワー/メガパワー/ほかくパワー/そうぐうパワー/めんえきパワー/ぼうぎょパワー/とくぼうパワー/こうげきパワー/とくこうパワー/すばやさパワー/わざパワー
# いじげんロゼルのみ2,いじげんリリバのみ2,いじげんナモのみ2,いじげんカシブのみ2
from Commands.Keys import Button, Hat

NAME = "サワードーナツ ロゼル2,リリバ2,ナモ2,カシブ2"
CATEGORY = "sour"
TARGETS = ["general"]

STEPS = [
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 1, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 2, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 2, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 2, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 1, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 2, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 2, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 2, 'duration': 0.1, 'interval': 0.1},
]