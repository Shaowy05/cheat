from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Set


class Suit(Enum):
    CLUBS = 0
    DIAMONDS = 1
    HEARTS = 2
    SPADES = 3

    def __str__(self):
        match self.value:
            case 0:
                return "♣︎"
            case 1:
                return "♦︎"
            case 2:
                return "♥︎"
            case 3:
                return "♠︎"

    __repr__ = __str__


@dataclass(eq=True, frozen=True)
class Card:
    number: int
    suit: Suit

    def __str__(self):
        return f"({self.number} {self.suit})"

    __repr__ = __str__


FULL_DECK: Set[Card] = set(Card(n, s) for n in range(1, 14) for s in Suit)


@dataclass(eq=True, frozen=True)
class PlayerView:
    hand: Set[Card]
    pile: List[Card]
    previous_claim: Card
    opponent_pile_size: int
    start_player_id: int


class ActionOption(Enum):
    TRUTH = 0
    LIE = 1
    CALL = 2


@dataclass(eq=True, frozen=True)
class Action:
    option: ActionOption
    card: Optional[Card]
    claimed_card: Optional[Card]
