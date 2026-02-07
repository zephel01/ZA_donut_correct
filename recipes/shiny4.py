# 色違い厳選レシピ4 (ほかくパワー付与レシピ2 New)
from Commands.Keys import Button, Hat

NAME = "色違い厳選レシピ4 (ほかくパワー付与レシピ2 New)"
CATEGORY = "shiny"
TARGETS = ['shiny']  # 対象: 色違い

STEPS = [
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 5, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 6, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 4, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 5, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 1, 'duration': 0.1, 'interval': 0.1},
]
