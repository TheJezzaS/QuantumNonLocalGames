import math
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from math import pi
from qiskit import transpile
from qiskit_aer import Aer
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt
import numpy as np
import random

def measure_pauli(circ, qubit, basis):
    if basis == 'X':
        circ.h(qubit)
    elif basis == 'Y':
        circ.sdg(qubit)
        circ.h(qubit)
    # Z or I: do nothing

def apply_alice_measurement(circ, row, q0, q2, c0, c2):
    if row == 0:  # I⊗X, X⊗I, X⊗X
        measure_pauli(circ, q0, 'X')
        measure_pauli(circ, q2, 'X')
    elif row == 1:  # I⊗Z, Z⊗I, Z⊗Z
        measure_pauli(circ, q0, 'Z')
        measure_pauli(circ, q2, 'Z')
    elif row == 2:  # X⊗Z, Z⊗X, Y⊗Y
        circ.h(q0)
        circ.h(q2)
        circ.cz(q0, q2)
        circ.h(q0)
        circ.h(q2)
    circ.measure(q0, c0)
    circ.measure(q2, c2)

def apply_bob_measurement(circ, col, q1, q3, c1, c3):
    if col == 0:  # I⊗X, I⊗Z, X⊗Z
        measure_pauli(circ, q1, 'X')
        measure_pauli(circ, q3, 'Z')
    elif col == 1:  # X⊗I, Z⊗I, Z⊗X
        measure_pauli(circ, q1, 'Z')
        measure_pauli(circ, q3, 'X')
    elif col == 2:  # X⊗X, Z⊗Z, Y⊗Y
        circ.h(q1)
        circ.h(q3)
        circ.cz(q1, q3)
        circ.h(q1)
        circ.h(q3)
    circ.measure(q1, c1)
    circ.measure(q3, c3)

def simulate_round(row, col):
    qc = QuantumCircuit(4, 4)

    # Prepare two Bell pairs: (q0, q1) and (q2, q3)
    qc.h(0)
    qc.cx(0, 1)
    qc.h(2)
    qc.cx(2, 3)

    # Alice: qubits q0 and q2 → classical bits c0 and c2
    apply_alice_measurement(qc, row, 0, 2, 0, 2)

    # Bob: qubits q1 and q3 → classical bits c1 and c3
    apply_bob_measurement(qc, col, 1, 3, 1, 3)

    # Run the circuit
    simulator = Aer.get_backend('qasm_simulator')
    compiled_circuit = transpile(qc, simulator)
    result = simulator.run(compiled_circuit, shots=1, memory=True).result()
    bits = result.get_memory()[0]  # format: 'c3c2c1c0'

    c0 = int(bits[3])
    c1 = int(bits[2])
    c2 = int(bits[1])
    c3 = int(bits[0])

    # Alice outputs: a0 = c0, a1 = ?, a2 = c2
    # Bob outputs:   b0 = c1, b1 = ?, b2 = c3

    alice_outputs = [None, None, None]
    bob_outputs   = [None, None, None]

    # Place outputs in correct positions
    if row == 0:
        alice_outputs = [c2, c0 ^ c2, c0]
    elif row == 1:
        alice_outputs = [c2, c0 ^ c2, c0]
    elif row == 2:
        alice_outputs = [c2, c0 ^ c2, c0]

    if col == 0:
        bob_outputs = [c1, c1 ^ c3, c3]
    elif col == 1:
        bob_outputs = [c1, c1 ^ c3, c3]
    elif col == 2:
        bob_outputs = [c1, c1 ^ c3, c3]

    # Parity checks
    row_parity = sum(alice_outputs) % 2  # Should be 0
    col_parity = sum(bob_outputs) % 2    # Should be 1

    # Consistency check: shared cell
    shared_output_equal = (alice_outputs[col] == bob_outputs[row])

    win = (row_parity == 0) and (col_parity == 1) and shared_output_equal
    return win

# Run many rounds
rounds = 100
wins = 0

for _ in range(rounds):
    row = random.randint(0, 2)
    col = random.randint(0, 2)
    if simulate_round(row, col):
        wins += 1

print(f"Quantum strategy win rate: {wins}/{rounds} = {wins/rounds:.2%}")
