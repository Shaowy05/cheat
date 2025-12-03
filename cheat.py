from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Set

import random

from core import Action, ActionOption, Card, PlayerView, Suit
from strategies import Strategy, random_strategy


@dataclass(eq=True, frozen=True)
class TwoPlayerCheatGameState:
    active_player_id: int
    waiting_player_id: int
    previous_winner_id: int
    active_pile: List[Card]
    waiting_pile: List[Card]


class Player:
    def __init__(self, id: int, strategy: Strategy):
        self.id: int = id
        self.strategy: Strategy = strategy
        self.hand: Set[Card] = set()
        self.pile: List[Card] = []


class HandDistribution(Enum):
    RANDOM = 0
    MIRROR = 1


class TwoPlayerCheat:
    def __init__(
        self,
        hand_distribution: HandDistribution = HandDistribution.RANDOM,
        player_one_strategy: Strategy = random_strategy,
        player_two_strategy: Strategy = random_strategy,
    ):
        self.cards = [Card(n, s) for n in range(1, 14) for s in Suit]
        self.player_one = Player(1, player_one_strategy)
        self.player_two = Player(2, player_two_strategy)

        self.deal(hand_distribution)

        self.player_one_pile = []
        self.player_two_pile = []

        self.starting_player_id = 1
        self.active_player_id = 1

        self.current_claim: Optional[Card] = None

    def _get_player(self, player_id: int, opponent=False) -> Player:
        if player_id == 1:
            return self.player_one if not opponent else self.player_two
        else:
            return self.player_two if not opponent else self.player_one

    def _get_player_view(self, player_id: int) -> PlayerView:
        player = self._get_player(player_id)
        opponent = self._get_player(player_id, opponent=True)

        player_view = PlayerView(
            hand=player.hand,
            pile=player.pile,
            previous_claim=self.current_claim,
            opponent_pile_size=len(opponent.pile),
            start_player_id=self.starting_player_id,
        )

        return player_view

    def deal(self, hand_distribution: HandDistribution):
        assert len(self.cards) % 2 == 0

        match hand_distribution:
            case HandDistribution.RANDOM:
                copy = self.cards
                random.shuffle(copy)

                while copy:
                    self.player_one.hand.add(copy.pop())
                    self.player_two.hand.add(copy.pop())

    def perform_action(self, action: Action, active_player_id: int) -> None:
        active_player = self._get_player(active_player_id)

        match action.option:
            case ActionOption.TRUTH:
                assert action.card is not None
                card = action.card

                active_player.hand.remove(card)
                self.player_one_pile.append(card)
                self.current_claim = action.claimed_card

    def play(self):
        winner = None
        while not winner:
            active_player = self._get_player(self.active_player_id)
            player_view = self._get_player_view(self.active_player_id)

            action = active_player.strategy(player_view)
            self.perform_action(action, self.active_player_id)

            if not active_player.hand:
                print(f"Player {active_player.id} Wins!")
                return
