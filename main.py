from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt



# Step 1: Prepare the entangled state
def prepare_entangled_state():
    qc = QuantumCircuit(4, 4)  # 4 qubits and 4 classical bits

    # Prepare the first pair (a1, b1) in the (|+> + |->) state
    qc.h(0)  # Apply H to a1 (Alice's first qubit)
    qc.h(2)  # Apply H to b1 (Bob's first qubit)
    qc.cx(0, 2)  # Entangle a1 and b1 with a CNOT gate

    # Prepare the second pair (a2, b2) in the (|+> + |->) state
    qc.h(1)  # Apply H to a2 (Alice's second qubit)
    qc.h(3)  # Apply H to b2 (Bob's second qubit)
    qc.cx(1, 3)  # Entangle a2 and b2 with a CNOT gate

    return qc


# Step 2: Apply Alice's measurement based on the row
def apply_alice_measurement(qc, row):
    if row == 0:
        # Measure in Z basis
        qc.measure([0, 1], [0, 1])  # Alice's first and second qubits in Z basis
    elif row == 1:
        # Measure in X basis
        qc.h(0)  # Alice's first qubit
        qc.h(1)  # Alice's second qubit
        qc.measure([0, 1], [0, 1])
    elif row == 2:
        # Measure in the entangled basis
        qc.cx(0, 1)  # Entangle Alice's qubits
        qc.h(1)  # Apply Hadamard to second qubit
        qc.measure([0, 1], [0, 1])


# Step 3: Apply Bob's measurement based on the column
def apply_bob_measurement(qc, col):
    if col == 0:
        # Measure Bob's qubits in X and Z basis
        qc.h(2)  # Bob's first qubit
        qc.measure([2], [2])  # Measure Bob's first qubit in X basis
        qc.measure([3], [3])  # Measure Bob's second qubit in Z basis
    elif col == 1:
        # Measure Bob's qubits in Z and X basis
        qc.measure([2], [2])  # Measure Bob's first qubit in Z basis
        qc.h(3)  # Bob's second qubit
        qc.measure([3], [3])  # Measure Bob's second qubit in X basis
    elif col == 2:
        # Measure Bob's qubits in the entangled basis
        qc.cx(2, 3)  # Entangle Bob's qubits
        qc.h(3)  # Apply Hadamard to second qubit
        qc.measure([2, 3], [2, 3])


# Step 4: Simulate the circuit
def run_simulation(qc):
    # Draw and show the quantum circuit
    print("Quantum Circuit:")
    qc.draw(output='mpl')
    plt.show()

    # Run the circuit
    simulator = Aer.get_backend('aer_simulator')
    qc = qc.copy()  # Avoid modifying original
    qc.measure_all()
    result = simulator.run(qc, shots=1024).result()
    counts = result.get_counts()

    # Show histogram of measurement outcomes
    print("Measurement Results:")
    plot_histogram(counts)
    plt.show()

    return counts

# Example: Prepare the entangled state and apply measurements
qc = prepare_entangled_state()

# Apply Alice's and Bob's measurements
apply_alice_measurement(qc, row=0)  # Row 0 for Alice
apply_bob_measurement(qc, col=0)  # Column 0 for Bob

# Run the simulation and visualize the results
run_simulation(qc)
