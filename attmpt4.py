import math
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from math import pi
from qiskit import transpile
from qiskit_aer import Aer
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt
import numpy as np
import random

# Observable table
observables = [
    ['I_Z', 'X_I', 'X_Z'],
    ['Z_I', 'I_X', 'Z_X'],
    ['-Z_Z', '-X_X', '-Y_Y']
]

def apply_observable_measurement(circ, observable, qa, qb, ca, cb):
    """Measure a 2-qubit observable by rotating into Z basis and measuring."""
    negate = observable.startswith('-')
    if negate:
        observable = observable[1:]  # Strip minus sign

    # Single-qubit observables
    if observable == 'I_Z':
        circ.barrier()
        measure_basis(circ, qb, 'Z')
        circ.measure(qb, cb)
    elif observable == 'Z_I':
        circ.barrier()
        measure_basis(circ, qa, 'Z')
        circ.measure(qa, ca)
    elif observable == 'X_I':
        circ.barrier()
        measure_basis(circ, qa, 'X')
        circ.measure(qa, ca)
    elif observable == 'I_X':
        circ.barrier()
        measure_basis(circ, qb, 'X')
        circ.measure(qb, cb)

    # Two-qubit observables
    elif observable == 'Z_Z':
        circ.barrier()
        circ.cz(qa, qb)
        circ.h(qa)
        circ.h(qb)
        circ.measure(qa, ca)
        circ.measure(qb, cb)
    elif observable == 'X_X':
        circ.barrier()
        circ.h(qa)
        circ.h(qb)
        circ.cx(qa, qb)
        circ.h(qa)
        circ.h(qb)
        circ.measure(qa, ca)
        circ.measure(qb, cb)
    elif observable == 'Y_Y':
        circ.barrier()
        circ.sdg(qa)
        circ.h(qa)
        circ.sdg(qb)
        circ.h(qb)
        circ.cz(qa, qb)
        circ.h(qa)
        circ.h(qb)
        circ.measure(qa, ca)
        circ.measure(qb, cb)
    elif observable == 'X_Z':
        circ.barrier()
        circ.h(qa)
        circ.cz(qa, qb)
        circ.h(qa)
        circ.measure(qa, ca)
        circ.measure(qb, cb)
    elif observable == 'Z_X':
        circ.barrier()
        circ.h(qb)
        circ.cz(qa, qb)
        circ.h(qb)
        circ.measure(qa, ca)
        circ.measure(qb, cb)

    # Negate result if needed
    if negate:
        circ.x(ca)
        circ.x(cb)

def measure_basis(circ, qubit, basis):
    if basis == 'X':
        circ.h(qubit)
    elif basis == 'Y':
        circ.sdg(qubit)
        circ.h(qubit)
    # Z: do nothing

def simulate_magic_square_game(row, col):
    qc = QuantumCircuit(4, 4)

    # Prepare two Bell pairs: (0,1) and (2,3)
    qc.h(0)
    qc.cx(0, 1)
    qc.h(2)
    qc.cx(2, 3)

    obs = observables[row][col]
    apply_observable_measurement(qc, obs, 0, 1, 0, 1)  # Alice: q0, Bob: q1

    # Run the circuit
    simulator = Aer.get_backend('qasm_simulator')
    compiled_circuit = transpile(qc, simulator)
    result = simulator.run(compiled_circuit, shots=1, memory=True).result()

    bits = result.get_memory()[0]  # bits[0] = c0, bits[1] = c1
    a = int(bits[1])
    b = int(bits[0])

    # Measurement outcomes: +1 ↔ 0, −1 ↔ 1
    outcome = 1 if a == b else -1

    # Parity expectations
    expected_sign = 1
    if col == 2:
        expected_sign *= -1
    if obs.startswith('-'):
        expected_sign *= -1

    return outcome == expected_sign

# Run trials
shots = 100
wins = sum(simulate_magic_square_game(random.randint(0, 2), random.randint(0, 2)) for _ in range(shots))
print(f"Quantum strategy win rate: {wins}/{shots} = {wins/shots:.2%}")
