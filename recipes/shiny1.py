# スイートドーナツ かがやきパワー オヤブンパワー/でかでかパワー/ちびちびパワー/かがやきパワー/ほかくパワー/そうぐうパワー
# いじげんタンガのみ4,いじげんハバンのみ4
from Commands.Keys import Button, Hat

NAME = "スイートドーナツ タンガ4,ハバン4"
CATEGORY = "sweet"
TARGETS = ["shiny"]

STEPS = [
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 5, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 4, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 3, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 4, 'duration': 0.1, 'interval': 0.1},
]