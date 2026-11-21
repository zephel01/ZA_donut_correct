# サワードーナツ どうぐパワー どっさりパワー/どうぐパワー/メガパワー/めんえきパワー/ぼうぎょパワー/とくぼうパワー
# いじげんリリバのみ1,いじげんナモのみ1,いじげんカシブのみ1,ナモのみ5（店売り）
# サワー325, ビター135, フレッシュ95（シミュレーター計算でサワー系 Lv2。どうぐの種類は抽選）
from Commands.Keys import Button, Hat

NAME = "サワードーナツ リリバ1,ナモ1,カシブ1,店売りナモ5"
CATEGORY = "sour"
TARGETS = ["tool"]

STEPS = [
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 3, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 1, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 2, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 31, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 5, 'duration': 0.1, 'interval': 0.1},
]
