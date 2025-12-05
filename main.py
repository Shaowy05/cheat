from cheat import TwoPlayerCheat
from strategies import Strategy, ParamStrategy
from collections import defaultdict
import numpy as np
from typing import Tuple


def estimate_payoff(
    strategy_one: Strategy, strategy_two: Strategy, n_games=10000
) -> float:
    score = 0
    for _ in range(n_games):
        game = TwoPlayerCheat(
            player_one_strategy=strategy_one,
            player_two_strategy=strategy_two,
            verbose=False,
        )
        winner = game.play()
        if winner.id == 1:
            score += 1
        else:
            score -= 1
    return score / n_games


def best_response_to(
    p_opp: float,
    q_opp: float,
    grid_step=0.1,
    n_games=10000,
) -> Tuple[float, float, float]:
    opp = ParamStrategy(bluff_prob=p_opp, call_prob_uncertain=q_opp)

    best_val = -1e9
    best_p, best_q = None, None

    for p in np.arange(0.0, 1.0 + 1e-9, grid_step):
        for q in np.arange(0.0, 1.0 + 1e-9, grid_step):
            me = ParamStrategy(bluff_prob=p, call_prob_uncertain=q)
            val = estimate_payoff(me, opp, n_games=n_games)
            if val > best_val:
                best_val = val
                best_p, best_q = p, q

    return best_p, best_q, best_val


def find_symmetric_equilibrium(start_p=0.3, start_q=0.3, iters=5):
    p, q = start_p, start_q
    for i in range(iters):
        br_p, br_q, val = best_response_to(p, q, grid_step=0.2, n_games=300)
        print(
            f"Iter {i}: BR to (p={p:.2f}, q={q:.2f}) is (p={br_p:.2f}, q={br_q:.2f}), val={val:.3f}"
        )
        if abs(br_p - p) < 0.05 and abs(br_q - q) < 0.05:
            print("Approximate symmetric equilibrium found.")
            break
        p, q = br_p, br_q
    return p, q


def main():
    counter = defaultdict(int)

    for _ in range(10000):
        game = TwoPlayerCheat(
            player_one_strategy=ParamStrategy(0.1, 0.1),
            player_two_strategy=ParamStrategy(0.0, 0.0),
            verbose=False,
        )
        # game = TwoPlayerCheat(
        #     player_one_strategy=random_strategy,
        #     player_two_strategy=random_strategy,
        #     verbose=False
        # )
        winner = game.play()

        counter[winner.id] += 1

    print(counter)
    # print(find_symmetric_equilibrium())


if __name__ == "__main__":
    main()
