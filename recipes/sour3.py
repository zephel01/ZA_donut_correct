# サワードーナツ どっさりパワー/どうぐパワー/メガパワー/めんえきパワー/ぼうぎょパワー/とくぼうパワー
# いじげんリリバのみ1,いじげんナモのみ1,ナモのみ6（店売り）
# サワー250, ビター145, フレッシュ85（パワーはすべて Lv1 相当）
from Commands.Keys import Button, Hat

NAME = "サワードーナツ リリバ1,ナモ1,店売りナモ6"
CATEGORY = "sour"
TARGETS = ["tool"]

STEPS = [
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 3, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 1, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 33, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 6, 'duration': 0.1, 'interval': 0.1},
]
