from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt
import numpy as np

NUM_RUNS = 20

# Convert bitstrings to eigenvalues so that results of code are equivilant to theory described in the latex
def _bit_to_eigen(bit):
    return +1 if bit == '0' else -1

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


def check_parity_condition(alice_out, bob_out):
    """
    Check that Alice's outputs multiply to +1 (even parity),
    Bob's outputs multiply to -1 (odd parity),
    """
    alice_parity_check = np.prod(alice_out) == +1
    bob_parity_check = np.prod(bob_out) == -1
    return alice_parity_check and bob_parity_check


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


def _apply_basis(circ, qubit, basis):
    """Rotate qubit into measurement basis before measuring in Z."""
    if basis == 'X':
        circ.h(qubit)
    elif basis == 'Y':
        circ.sdg(qubit)
        circ.h(qubit)
    # if 'Z' or 'I', do nothing for basis rotation

def alice_measure_row(circ, row, q0, q2, c0, c2):
    """Apply Alice's measurement for given row on qubits q0, q2."""
    if row == 1:  # I⊗X, X⊗I, X⊗X
        _apply_basis(circ, q0, 'X')
        _apply_basis(circ, q2, 'X')
    elif row == 2:  # I⊗Z, Z⊗I, Z⊗Z
        _apply_basis(circ, q0, 'Z')
        _apply_basis(circ, q2, 'Z')
    elif row == 3:  # X⊗Z, Z⊗X, Y⊗Y
        circ.sdg(q0)
        circ.h(q0)
        circ.sdg(q2)
        circ.h(q2)
        circ.cx(q0, q2)


    circ.measure(q0, c0)
    circ.measure(q2, c2)

def bob_measure_column(circ, col, q1, q3, c1, c3):
    """Apply Bob's measurement for given column on qubits q1, q3."""
    if col == 1:  # I⊗X, I⊗Z, X⊗Z
        _apply_basis(circ, q1, 'X')
        _apply_basis(circ, q3, 'Z')
    elif col == 2:  # X⊗I, Z⊗I, Z⊗X
        _apply_basis(circ, q1, 'Z')
        _apply_basis(circ, q3, 'X')
    elif col == 3:  # X⊗X, Z⊗Z, Y⊗Y
        # do the opposite of a bell circuit to make the entangles basis for measurement
        circ.cx(q1, q3)  # Entangle a1 and b1 with a CNOT gate
        circ.h(q1)  # Apply H to a1 (Alice's first qubit)

        _apply_basis(circ, q1, 'Z')
        _apply_basis(circ, q3, 'Z')

    circ.measure(q1, c1)
    circ.measure(q3, c3)



def run_game(r, c):
    qc = prepare_entangled_state()
    alice_measure_row(qc, row=r, q0=0, q2=2, c0=0, c2=2)
    bob_measure_column(qc, col=c, q1=1, q3=3, c1=1, c3=3)

    simulator = Aer.get_backend('qasm_simulator')
    compiled_circuit = transpile(qc, simulator)
    result = simulator.run(compiled_circuit, shots=1, memory=True).result()
    memory = result.get_memory()[0]  # bitstring in c3 c2 c1 c0 order

    bits = {
        'a1': int(memory[3]),  # q0 → c0
        'b1': int(memory[2]),  # q1 → c1
        'a2': int(memory[1]),  # q2 → c2
        'b2': int(memory[0]),  # q3 → c3
    }

# TODO: i added a minus sign, not sure if this should be there
    if r == 1 or r == 2:
        a1 = _bit_to_eigen(bits['a1'])  #if r != 3 else -_bit_to_eigen(bits['a1'])  # -X⊗Z
        a2 = _bit_to_eigen(bits['a2'])  #if r != 3 else -_bit_to_eigen(bits['a2'])  # -Z⊗X
    else: # r=3
        a1 = -_bit_to_eigen(bits['a1'])
        a2 = _bit_to_eigen(bits['a2'])
    a3 = a1 * a2  #   (guarantees even parity)



    b1 = _bit_to_eigen(bits['b1'])  # from c1
    b2 = _bit_to_eigen(bits['b2'])  # from c3
    # odd parity (zz·xx·yy = –1)
    b3 = -b1 * b2

    alice_out = [a1, a2, a3]
    bob_out = [b1, b2, b3]


    outcome = 'WIN' if alice_out[r - 1] == bob_out[c - 1] and check_parity_condition(alice_out, bob_out) else 'LOSS'
    #print('equal',alice_out[r - 1] == bob_out[c - 1])
    #print('parity',check_parity_condition(alice_out, bob_out))
    print(alice_out,bob_out, r,c)
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
    # print(run_game(3,3))
    all_results = run_all_combinations(n=NUM_RUNS)
    plot_win_loss_grid(all_results, NUM_RUNS)


if __name__ == "__main__":
    main()
