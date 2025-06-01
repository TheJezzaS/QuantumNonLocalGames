import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np

NUM_RUNS = 10

# Convert bitstrings to eigenvalues so that results of code are equivilant to theory described in the latex
def _bit_to_eigen(bit): return +1 if bit == '0' else -1

def plot_statevector_latex(qc):
    """
    Given a `qc`,
    converts it to LaTeX bra-ket notation, and prints it.
    """
    psi = Statevector.from_instruction(qc)
    latex_obj = psi.draw('latex')

    # Clean up LaTeX string for matplotlib
    latex_str = latex_obj.data.strip('$')
    latex_str = f"${latex_str}$"

    plt.figure(figsize=(8, 2))
    plt.text(0.1, 0.5, latex_str, fontsize=20)
    plt.axis('off')
    plt.show()


def check_parity_condition(alice_out, bob_out, row, column):
    """
    Check that Alice's outputs multiply to +1 (even parity),
    Bob's outputs multiply to -1 (odd parity),
    and their outputs agree on the intersection (row, column).
    """
    alice_parity_check = np.prod(alice_out) == +1
    bob_parity_check = np.prod(bob_out) == -1
    intersection_check = alice_out[row - 1] == bob_out[column - 1]
    return alice_parity_check and bob_parity_check and intersection_check

def _apply_basis_and_measure(qc, qubit, cbit, basis):
    """Apply basis change before measurement on qubit, then measure to classical bit"""
    if basis == 'X':
        qc.h(qubit)
    elif basis == 'Y':
        qc.sdg(qubit)
        qc.h(qubit)
    # Z basis: no gate

    qc.measure(qubit, cbit)

def prepare_entangled_state():
    qc = QuantumCircuit(4, 4)  # 4 qubits and 4 classical bits

    # create beta_00 from bits 0 and 1 (a1 and b1)
    qc.h(0)  # Apply H to a1 (Alice's first qubit)
    qc.cx(0, 1)  # Entangle a1 and b1 with a CNOT gate

    # create beta_00 from bits 2 and 3 (a2 and b2)
    qc.h(2)  # Apply H to b1 (Bob's first qubit)
    qc.cx(2, 3)  # Entangle a2 and b3 with a CNOT gate

    # plot_statevector_latex(qc)
    return qc


# Alice measures row (1, 2, or 3) on q0, q2 and stores in c0, c2
def alice_measure_row(qc, row):
    if row == 1:
        _apply_basis_and_measure(qc, 0, 0, 'Z')  # IZ
        _apply_basis_and_measure(qc, 2, 2, 'Z')  # ZI
    elif row == 2:
        _apply_basis_and_measure(qc, 0, 0, 'X')  # XI
        _apply_basis_and_measure(qc, 2, 2, 'X')  # IX
    elif row == 3:
        _apply_basis_and_measure(qc, 0, 0, 'Y')  # -XZ
        _apply_basis_and_measure(qc, 2, 2, 'Y')  # -ZX
    else:
        raise ValueError("Row must be 1, 2, or 3")

# Bob measures column (1, 2, or 3) on q1, q3 and stores in c1, c3
def bob_measure_column(qc, column):
    if column == 1:
        _apply_basis_and_measure(qc, 1, 1, 'Z')  # IZ
        _apply_basis_and_measure(qc, 3, 3, 'Z')  # ZI
    elif column == 2:
        _apply_basis_and_measure(qc, 1, 1, 'Z')  # ZI
        _apply_basis_and_measure(qc, 3, 3, 'X')  # IX
    elif column == 3:
        _apply_basis_and_measure(qc, 1, 1, 'Y')  # -XZ
        _apply_basis_and_measure(qc, 3, 3, 'Y')  # -ZX
    else:
        raise ValueError("Column must be 1, 2, or 3")


def run_game(r, c):
    qc = prepare_entangled_state()
    alice_measure_row(qc, r)
    bob_measure_column(qc, c)

    simulator = Aer.get_backend('qasm_simulator')
    compiled_circuit = transpile(qc, simulator)
    result = simulator.run(compiled_circuit, shots=1).result()
    counts = result.get_counts()
    bitstring = list(counts.keys())[0]

    # Reverse bitstring to match classical bits order c0,c1,c2,c3, this seems to be an oddity of quiskit
    reversed_bits = bitstring[::-1]
    bits = {
        'a1': int(reversed_bits[0]),
        'b1': int(reversed_bits[1]),
        'a2': int(reversed_bits[2]),
        'b2': int(reversed_bits[3]),
    }

    a1 = _bit_to_eigen(bits['a1'])
    a2 = _bit_to_eigen(bits['a2'])
    a3 = - (a1 * a2)  # always enforce even parity (product +1)
    alice_out = [a1, a2, a3]

    b1 = _bit_to_eigen(bits['b1'])
    b2 = _bit_to_eigen(bits['b2'])
    b3 = - (b1 * b2)  # always enforce odd parity (product -1)
    bob_out = [b1, b2, b3]

    outcome = 'WIN' if alice_out[r - 1] == bob_out[c - 1] and check_parity_condition(alice_out, bob_out, r, c) else 'LOSS'
    return outcome, alice_out, bob_out


def run_all_combinations(n=NUM_RUNS):
    all_results = {}
    for r in [1, 2, 3]:
        for c in [1, 2, 3]:
            results = {'WIN': 0, 'LOSS': 0}
            for _ in range(n):
                outcome, _, _ = run_game(r, c)
                results[outcome] += 1
            all_results[(r, c)] = results
    return all_results


def plot_win_loss_grid(all_results, n):
    fig, axes = plt.subplots(3, 3, figsize=(12, 12), sharey=True)

    for r in range(1, 4):
        for c in range(1, 4):
            ax = axes[r - 1, c - 1]
            res = all_results[(r, c)]
            ax.bar(res.keys(), res.values(), color=['green', 'red'])
            ax.set_ylim(0, n)
            ax.set_title(f"Row {r}, Col {c}")
            if c == 1:
                ax.set_ylabel('Counts')
            if r == 3:
                ax.set_xlabel('Outcome')

    plt.suptitle("Magic Square Game Win/Loss Counts")
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()


def main():
    all_results = run_all_combinations(n=NUM_RUNS)
    plot_win_loss_grid(all_results, NUM_RUNS)


if __name__ == "__main__":
    main()
