# どうぐパワー重視レシピ/カシブx8
from Commands.Keys import Button, Hat

NAME = "どうぐパワー重視レシピ/カシブx8"
CATEGORY = "tool"
TARGETS = ['tool']  # 対象: どうぐパワー

STEPS = [
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 6, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 8, 'duration': 0.1, 'interval': 0.1},
]
