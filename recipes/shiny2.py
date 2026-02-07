# 色違い厳選レシピ2 (タンガのみ×8)
from Commands.Keys import Button, Hat

NAME = "色違い厳選レシピ2 (タンガのみ×8)"
CATEGORY = "shiny"
TARGETS = ['shiny']  # 対象: 色違い

STEPS = [
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 8, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 8, 'duration': 0.1, 'interval': 0.1},
]
