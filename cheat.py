from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Set

import random

from core import Action, ActionOption, Card, PlayerView, FULL_DECK
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
        verbose: bool = True,
    ):
        self.cards = FULL_DECK.copy()
        self.player_one = Player(1, player_one_strategy)
        self.player_two = Player(2, player_two_strategy)

        self.deal(hand_distribution)

        self.starting_player_id = 1
        self.active_player_id = 1

        self.current_claim: Optional[Card] = None

        self.verbose = verbose
        self.round_number = 0

        if self.verbose:
            print("=== NEW GAME: TWO PLAYER CHEAT ===")
            self._print_initial_state()

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
                random.shuffle(list(copy))

                while copy:
                    self.player_one.hand.add(copy.pop())
                    self.player_two.hand.add(copy.pop())

    def perform_action(self, action: Action, active_player_id: int) -> None:
        active_player = self._get_player(active_player_id)
        opponent = self._get_player(active_player_id, opponent=True)

        match action.option:
            case ActionOption.TRUTH:
                assert action.card is not None
                card = action.card

                active_player.hand.remove(card)
                active_player.pile.append(card)
                self.current_claim = action.claimed_card
                self.active_player_id = opponent.id
            case ActionOption.LIE:
                assert action.card is not None
                card = action.card

                active_player.hand.remove(card)
                active_player.pile.append(card)
                self.current_claim = action.claimed_card
                self.active_player_id = opponent.id
            case ActionOption.CALL:
                if self.current_claim is None:
                    raise Exception("Cannot call cheat on first go")

                if self.current_claim != opponent.pile[-1]:
                    opponent.hand.update(opponent.pile)
                    opponent.hand.update(active_player.pile)
                    self.starting_player_id = active_player_id
                else:
                    active_player.hand.update(opponent.pile)
                    active_player.hand.update(active_player.pile)
                    self.starting_player_id = opponent.id

                opponent.pile = []
                active_player.pile = []

    def play(self):
        winner: Optional[Player] = None
        while winner is None:
            active_player = self._get_player(self.active_player_id)
            player_view = self._get_player_view(self.active_player_id)

            action = active_player.strategy(player_view)
            self.perform_action(action, self.active_player_id)
            self._print_state_after_move()

            if len(active_player.hand) == 0:
                winner = active_player
                break

        if winner is not None:
            print("\n=== GAME OVER ===")
            print(f"Player {winner.id} WINS!")
            print(
                f"Final piles: "
                f"P1 = {len(self.player_one.pile)} cards, "
                f"P2 = {len(self.player_two.pile)} cards"
            )

    # --- Visualisation Helpers -------------------

    def _hand_to_str(self, hand: Set[Card]) -> str:
        # For debugging: show actual cards. For less info, just show the count.
        return " ".join(map(str, hand))

    def _print_initial_state(self):
        print(f"Player 1 starts. Each player has {len(self.player_one.hand)} cards.\n")
        print("Player 1 initial hand:")
        print(self._hand_to_str(self.player_one.hand))
        print("\nPlayer 2 initial hand:")
        print(self._hand_to_str(self.player_two.hand))
        print("\n" + "=" * 40)

    def _print_turn_header(self):
        if not self.verbose:
            return
        self.round_number += 1
        print(f"\n----- ROUND {self.round_number} -----")
        print(f"Active player: Player {self.active_player_id}")

    def _print_action(self, action: Action, active_player: Player):
        if not self.verbose:
            return

        if action.card is not None:
            actual_str = action.card
        else:
            actual_str = "None"

        claimed_str = action.claimed_card if action.claimed_card is not None else "None"

        match action.option:
            case ActionOption.TRUTH:
                print(
                    f"Player {active_player.id} plays {actual_str} "
                    f"and TRUTHFULLY claims {claimed_str}"
                )
            case ActionOption.LIE:
                print(
                    f"Player {active_player.id} plays {actual_str} "
                    f"and LIES claiming {claimed_str}"
                )
            case ActionOption.CALL:
                print(f"Player {active_player.id} calls CHEAT on opponent!")

    def _print_state_after_move(self):
        if not self.verbose:
            return

        p1 = self.player_one
        p2 = self.player_two
        print("\nCurrent state:")
        print(
            f"  Player 1: {len(p1.hand)} cards in hand, "
            f"{len(self.player_one.pile)} in pile"
        )
        print(
            f"  Player 2: {len(p2.hand)} cards in hand, "
            f"{len(self.player_two.pile)} in pile"
        )
        if self.current_claim is not None:
            print(f"  Current claimed rank: {self.current_claim}")
        print("-" * 40)
