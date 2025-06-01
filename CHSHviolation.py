from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt
import numpy as np
import random

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


def referee_choose_xy():
    return random.choice([(0, 0), (0, 1), (1, 0), (1, 1)])

def Alice_response(x):
    if x:
        return np.pi / 2
    else:
        return 0

def Bob_response(y):
    if y:
        return -np.pi / 4
    else:
        return np.pi / 4

shots = 1024
simulator = Aer.get_backend('qasm_simulator')
num_wins = 0


### create bell state beta_00 ####
qc = QuantumCircuit(2, 2)
qc.h(0)

qc.cx(0, 1)
#--------------------------------#
plot_statevector_latex(qc)
#### Game begins #######
# generates two random input from the refree, x and y, to be given to Alice and Bob
x,y = referee_choose_xy()

#### Quantum stratagy ####
theta = Alice_response(x)  # Alice chooses her angle
phi = Bob_response(y)  # Bob chooses his angle
qc.ry(theta, 0)  # Alice rotates her qbit
qc.ry(phi, 1)  # Bob rotates his qbit


qc.measure(0, 0)
qc.measure(1, 1)

compiled_circuit = transpile(qc, simulator)
result = simulator.run(compiled_circuit, shots=1024, memory=True).result()

data = result.get_counts()  # count number of each output

# calc win stats
for key in data.keys():
    b, a = int(key[0]), int(key[1])

    # check success
    if (x * y == a ^ b):
        num_wins += data[key]


print('Probability of success: ', num_wins / shots * 100, '%')
b=qc.draw(output="mpl", idle_wires=False, style="iqp")
plt.savefig('CHSH_Q_circuit.png')
plt.show()
