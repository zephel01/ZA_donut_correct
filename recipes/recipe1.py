# どうぐパワー節約レシピ
from Commands.Keys import Button, Hat

NAME = "どうぐパワー節約レシピ"
CATEGORY = "tool"
TARGETS = ['tool']  # 対象: どうぐパワー

STEPS = [
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 1, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 3, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 2, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 3, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 4, 'duration': 0.1, 'interval': 0.1},
]
