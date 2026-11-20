# スイートドーナツ かがやきパワー オヤブンパワー/でかでかパワー/ちびちびパワー/かがやきパワー/ほかくパワー/そうぐうパワー
# いじげんハバンのみ6,いじげんタンガのみ2
from Commands.Keys import Button, Hat

NAME = "スイートドーナツ ハバン6,タンガ2"
CATEGORY = "sweet"
TARGETS = ["shiny"]

STEPS = [
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 5, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 6, 'duration': 0.1, 'interval': 0.1},
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 3, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 2, 'duration': 0.1, 'interval': 0.1},
]