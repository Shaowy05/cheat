from typing import Protocol
import random
from core import PlayerView, Action, ActionOption, FULL_DECK


class Strategy(Protocol):
    def __call__(self, player_view: PlayerView) -> Action: ...


def random_strategy(player_view: PlayerView) -> Action:
    random_option: ActionOption = random.choice(list(ActionOption))

    if random_option is ActionOption.CALL:
        return Action(random_option, None, None)

    card = random.choice(list(player_view.hand))

    if random_option is ActionOption.TRUTH:
        return Action(random_option, card, card)

    if random_option is ActionOption.LIE:
        excluded = FULL_DECK.difference([card])
        claim = random.choice(list(excluded))

        assert claim != card

        return Action(random_option, card, claim)
