import numpy as np

num_games = 10240

def classical_strategy(x, y):
    """
    Best classical deterministic strategy:
    Always output 0 for both Alice and Bob.
    This wins in all cases except when x = y = 1.
    """
    a = 0  # Alice's output
    b = 0  # Bob's output
    return a, b

def chsh_game_round():
    """
    Simulate one round of the CHSH game with random inputs (x, y).
    Returns True if the round is won.
    """
    x = np.random.randint(0, 2)  # Alice's input: 0 or 1
    y = np.random.randint(0, 2)  # Bob's input: 0 or 1
    a, b = classical_strategy(x, y)
    return (a ^ b) == (x & y)  # Win condition

def simulate_chsh_classical(n_rounds):
    """
    Simulate many rounds of the CHSH game using the classical strategy.
    Returns the average win rate.
    """
    wins = sum(chsh_game_round() for _ in range(n_rounds))
    return wins / n_rounds

win_rate = simulate_chsh_classical(num_games)
print(f"Classical strategy win percentage: {win_rate*100:.5f}")
