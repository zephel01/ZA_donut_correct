# サワードーナツ どっさりパワー/どうぐパワー/メガパワー/めんえきパワー/ぼうぎょパワー/とくぼうパワー/ほかくパワー/そうぐうパワー
# いじげんナモのみ3,いじげんリリバのみ4,いじげんロゼルのみ1
from Commands.Keys import Button, Hat

NAME = "サワードーナツ ナモ3,リリバ4,ロゼル1"
CATEGORY = "tool"
TARGETS = ['tool']  # 対象: どうぐパワー

STEPS = [
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 1, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 2, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 4, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 1, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 3, 'duration': 0.1, 'interval': 0.1},
]
