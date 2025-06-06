from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt
import numpy as np
import random

qc = QuantumCircuit(4, 4)

# Run the circuit
simulator = Aer.get_backend('qasm_simulator')
compiled_circuit = transpile(qc, simulator)
result = simulator.run(compiled_circuit, shots=1, memory=True).result()
bits = result.get_memory()[0]  # format: 'c3c2c1c0'

print('hello world')