import math
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from math import pi
from qiskit import transpile
from qiskit_aer import Aer
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt
import numpy as np

# Create the entangled shared state circuit
N = 4  # 4 qubits (Alice=2, Bob=2)

qr = QuantumRegister(N, 'qr')
cr = ClassicalRegister(N, 'cr')

sharedEntangled = QuantumCircuit(qr, cr, name="sharedEntangled")

# Create uniform superposition of first two qubits
for i in range(2):
    sharedEntangled.h(qr[i])
# Add Z gates (amplitude minus for odd number of 1s)
for i in range(2):
    sharedEntangled.z(qr[i])
# Copy first two qubits to last two qubits
for i in range(2):
    sharedEntangled.cx(qr[i], qr[i + 2])
# Flip last two qubits
for i in range(2, 4):
    sharedEntangled.x(qr[i])

from qiskit import QuantumCircuit

def combine_circuits(*circuits):
    """Return a new QuantumCircuit that sequentially applies all given circuits."""
    # Assume all circuits have the same qubits and classical bits registers
    combined = QuantumCircuit(circuits[0].num_qubits, circuits[0].num_clbits)
    for circ in circuits:
        combined.compose(circ, inplace=True)
    return combined

# Controlled gates definitions (operating on QuantumCircuit)
def ch(qc, a, b):
    """ Controlled-Hadamard gate """
    qc.h(b)
    qc.sdg(b)
    qc.cx(a, b)
    qc.h(b)
    qc.t(b)
    qc.cx(a, b)
    qc.t(b)
    qc.h(b)
    qc.s(b)
    qc.x(b)
    qc.s(a)
    return qc


def cu1pi2(qc, c, t):
    """ Controlled-u1(pi/2) gate """
    qc.p(pi/ 4.0, c)
    qc.cx(c, t)
    qc.p(-pi / 4.0, t)
    qc.cx(c, t)
    qc.p(pi/ 4.0, t)
    return qc


def cu3pi2(qc, c, t):
    """ Controlled-u3(pi/2, -pi/2, pi/2) gate """
    qc.p(pi/ 2.0, t)
    qc.cx(c, t)
    qc.u(-pi / 4.0, 0, 0, t)
    qc.cx(c, t)
    qc.u(pi / 4.0, -pi / 2.0, 0, t)
    return qc


# Build Alice's circuits
aliceCircuits = {}

for idx in range(1, 4):
    alice = QuantumCircuit(qr, cr, name=f"Alice{idx}")

    if idx == 1:
        alice.x(qr[1])
        alice.cx(qr[1], qr[0])
        cu1pi2(alice, qr[1], qr[0])
        alice.x(qr[0])
        alice.x(qr[1])
        cu1pi2(alice, qr[0], qr[1])
        alice.x(qr[0])
        cu1pi2(alice, qr[0], qr[1])
        cu3pi2(alice, qr[0], qr[1])
        alice.x(qr[0])
        ch(alice, qr[0], qr[1])
        alice.x(qr[0])
        alice.x(qr[1])
        alice.cx(qr[1], qr[0])
        alice.x(qr[1])
    elif idx == 2:
        alice.x(qr[0])
        alice.x(qr[1])
        cu1pi2(alice, qr[0], qr[1])
        alice.x(qr[0])
        alice.x(qr[1])
        cu1pi2(alice, qr[0], qr[1])
        alice.x(qr[0])
        alice.h(qr[0])
        alice.h(qr[1])
    elif idx == 3:
        alice.cz(qr[0], qr[1])
        alice.swap(qr[0], qr[1])
        alice.h(qr[0])
        alice.h(qr[1])
        alice.x(qr[0])
        alice.x(qr[1])
        alice.cz(qr[0], qr[1])
        alice.x(qr[0])
        alice.x(qr[1])

    alice.measure(qr[0], cr[0])
    alice.measure(qr[1], cr[1])
    aliceCircuits[f"Alice{idx}"] = alice


# Build Bob's circuits
bobCircuits = {}

for idx in range(1, 4):
    bob = QuantumCircuit(qr, cr, name=f"Bob{idx}")

    if idx == 1:
        bob.x(qr[2])
        bob.x(qr[3])
        bob.cz(qr[2], qr[3])
        bob.x(qr[3])
        bob.p(pi / 2.0, qr[2])
        bob.x(qr[2])
        bob.z(qr[2])
        bob.cx(qr[2], qr[3])
        bob.cx(qr[3], qr[2])
        bob.h(qr[2])
        bob.h(qr[3])
        bob.x(qr[3])
        cu1pi2(bob, qr[2], qr[3])
        bob.x(qr[2])
        bob.cz(qr[2], qr[3])
        bob.x(qr[2])
        bob.x(qr[3])
    elif idx == 2:
        bob.x(qr[2])
        bob.x(qr[3])
        bob.cz(qr[2], qr[3])
        bob.x(qr[3])
        bob.p(pi / 2.0, qr[3])
        bob.cx(qr[2], qr[3])
        bob.h(qr[2])
        bob.h(qr[3])
    elif idx == 3:
        bob.cx(qr[3], qr[2])
        bob.x(qr[3])
        bob.h(qr[3])

    bob.measure(qr[2], cr[2])
    bob.measure(qr[3], cr[3])
    bobCircuits[f"Bob{idx}"] = bob


# Function to run all rounds on the backend
def all_rounds(backend, shots=1024, real_dev=False):
    nWins = 0
    nLost = 0

    for a in range(1, 4):
        for b in range(1, 4):
            print(f"Asking Alice and Bob with a={a} and b={b}")

            # Compose the circuits: sharedEntangled + Alice + Bob
            combined = QuantumCircuit(qr, cr)
            combined = combine_circuits(sharedEntangled, aliceCircuits[f"Alice{a}"], bobCircuits[f"Bob{b}"])

            b = combined.draw(output="mpl", idle_wires=False, style="iqp")
            plt.show()

            # Run the circuit
            simulator = Aer.get_backend('qasm_simulator')
            compiled_circuit = transpile(combined, simulator)
            result = simulator.run(compiled_circuit, shots=1, memory=True).result()

            counts = result.get_counts()

            rWins = 0
            rLost = 0
            for key, count in counts.items():
                # The measurement string corresponds to cr bits [3..0],
                # but note the order of bits in Qiskit results is little-endian by default,
                # so key[0] is cr[3], key[3] is cr[0].
                # We need to reverse the string to match cr indices:
                reversed_key = key[::-1]

                # Extract bits for Alice (cr0, cr1) and Bob (cr2, cr3)
                aliceAnswer = [int(reversed_key[0]), int(reversed_key[1])]
                bobAnswer = [int(reversed_key[2]), int(reversed_key[3])]

                # Parities for Alice and Bob
                aliceAnswer.append(0 if sum(aliceAnswer) % 2 == 0 else 1)
                bobAnswer.append(0 if sum(bobAnswer) % 2 == 1 else 1)

                if aliceAnswer[b - 1] != bobAnswer[a - 1]:
                    nLost += count
                    rLost += count
                else:
                    nWins += count
                    rWins += count

            print(f"\t#wins = {rWins} out of {shots} shots")

    print(f"Number of Games = {nWins + nLost}")
    print(f"Number of Wins = {nWins}")
    print(f"Winning probability = {(nWins * 100.0) / (nWins + nLost):.2f}%")


if __name__ == "__main__":

    backend = Aer.get_backend('qasm_simulator')  # Local simulator backend
    real_device = False

    all_rounds(backend, shots=1024, real_dev=real_device)
