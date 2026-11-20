# スイートドーナツ かがやきパワー オヤブンパワー/でかでかパワー/ちびちびパワー/かがやきパワー
# いじげんタンガのみ8
from Commands.Keys import Button, Hat

NAME = "スイートドーナツ タンガ8"
CATEGORY = "sweet"
TARGETS = ["shiny"]

STEPS = [
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 8, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 8, 'duration': 0.1, 'interval': 0.1},
]