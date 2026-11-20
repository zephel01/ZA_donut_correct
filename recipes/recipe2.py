# サワードーナツ どうぐパワー どっさりパワー/どうぐパワー/メガパワー
# いじげんカシブのみ8
from Commands.Keys import Button, Hat

NAME = "サワードーナツ カシブ8"
CATEGORY = "sour"
TARGETS = ["tool"]

STEPS = [
    {'action': 'pressRep', 'type': Hat.TOP, 'repeat': 6, 'duration': 0.05, 'interval': 0.1},
    {'action': 'pressRep', 'type': Button.A, 'repeat': 8, 'duration': 0.1, 'interval': 0.1},
]