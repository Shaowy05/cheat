from typing import Protocol
import random
from core import PlayerView, Action, ActionOption, FULL_DECK


class Strategy(Protocol):
    def __call__(self, player_view: PlayerView) -> Action: ...


def random_strategy(player_view: PlayerView) -> Action:
    allowed_options = [ActionOption.TRUTH, ActionOption.LIE]
    if player_view.previous_claim is not None and player_view.opponent_pile_size > 0:
        allowed_options.append(ActionOption.CALL)

    random_option: ActionOption = random.choice(allowed_options)

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
