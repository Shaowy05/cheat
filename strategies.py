from typing import Protocol
import random
from core import PlayerView, Action, ActionOption, FULL_DECK
from dataclasses import dataclass


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


@dataclass
class ParamStrategy:
    bluff_prob: float
    call_prob_uncertain: float

    def __call__(self, player_view: PlayerView) -> Action:
        hand = player_view.hand
        previous_claim = player_view.previous_claim

        can_call = previous_claim is not None and player_view.opponent_pile_size > 0

        # If the previous claim is in your hand then you know they lied
        if can_call and previous_claim in hand:
            return Action(ActionOption.CALL, None, None)

        # Otherwise, we can't be sure and we call based on our uncertainty
        if can_call and previous_claim not in hand:
            if random.random() < self.call_prob_uncertain:
                return Action(ActionOption.CALL, None, None)

        card = random.choice(list(hand))

        if random.random() < self.bluff_prob:
            possible_claims = list(FULL_DECK - {card})
            claimed_card = random.choice(possible_claims)
            return Action(ActionOption.LIE, card, claimed_card)
        else:
            claimed_card = card
            return Action(ActionOption.TRUTH, card, claimed_card)
