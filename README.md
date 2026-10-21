# Mealy ↔ Moore Machine Conversion Simulator

**Course:** CSET302 – Automata Theory and Computability  
**Topic 14:** Mealy ↔ Moore Conversion  
**Author:** Kartikkk  
**Evaluation Dates:** 2–6 November 2026  

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/frontend-Streamlit-red.svg)](https://streamlit.io/)
[![Pytest](https://img.shields.io/badge/tests-Pytest-green.svg)](https://pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 1. Project Overview

The **Mealy ↔ Moore Machine Conversion Simulator** is an interactive, mathematically rigorous web application built for the **CSET302 – Automata Theory and Computability** project. 

It provides an end-to-end laboratory where students and faculty can:
- Define arbitrary finite-state transducers (FSTs) dynamically.
- Convert **Mealy machines** to equivalent **Moore machines** via standard state-splitting construction.
- Convert **Moore machines** to equivalent **Mealy machines** via destination-state output mapping.
- Trace intermediate algorithmic calculations step-by-step.
- Visualize dynamic state diagrams using **Graphviz** (with a graceful Mermaid.js fallback).
- Simulate input strings with real-time transition logs, state paths, and output strings.
- Verify behavioral equivalence using representative test suites and bounded exhaustive testing ($\Sigma^{\le k}$).

The simulator is built entirely with custom Python algorithms without relying on third-party conversion libraries, ensuring full transparency for viva voce evaluations.

---

## 2. Problem Statement

In automata theory and digital circuit design, finite-state transducers generate output sequences corresponding to input sequences. There are two canonical models:
1. **Mealy Machine:** Outputs are tied to transitions ($\lambda: Q \times \Sigma \to \Gamma$).
2. **Moore Machine:** Outputs are tied exclusively to states ($\lambda: Q \to \Gamma$).

Converting between these two formalisms requires:
- Handling the **asymmetry in state complexity**: Mealy states often need to be split into multiple Moore states when transitions entering them carry differing outputs.
- Accounting for the **output length discrepancy**: An input of length $n$ yields an output of length $n$ in a Mealy machine, but length $n + 1$ in a Moore machine due to the initial state output at time $t = 0$.
- Ensuring **deterministic completeness**: Machines must have valid, unique transitions for every state-symbol pair.

Existing tools often act as black boxes or support only basic DFAs without transducers, making it difficult for students to visualize why state splitting occurs and how the output alignment theorem operates.

---

## 3. Objectives

1. **Pedagogical Clarity:** Provide an intuitive step-by-step trace showing incoming transition outputs, splitting decisions, and transition remappings.
2. **Mathematical Correctness:** Implement verified conversion algorithms adhering to standard automata theory (Hopcroft & Ullman, Linz).
3. **Interactive Visualization:** Generate clean state-transition diagrams and interactive transition tables.
4. **Behavioral Equivalence Verification:** Validate conversions via bounded exhaustive testing ($\Sigma^{\le k}$) and string simulators.
5. **Academic Deliverables:** Deliver a production-quality, tested codebase with unit test coverage, full documentation, and viva preparation resources.

---

## 4. Scope and Limitations

### In Scope
- Complete deterministic finite transducers (Mealy and Moore).
- Bidirectional conversions: Mealy $\to$ Moore and Moore $\to$ Mealy.
- Dynamic machine input (user-defined states, alphabets, transitions, and outputs).
- Built-in verified presets (2's complement generator, sequence splitters, modulo counters).
- String execution simulation with path tracing and empty string ($\epsilon$) support.
- Bounded exhaustive testing up to length $k=4$.
- CSV export for transition tables and simulation traces.
- JSON import and export for machine definitions.

### Out of Scope / Limitations
- Non-deterministic transducers (NFTs) or transducers with $\epsilon$-transitions.
- Infinite-length formal verification (bounded testing is empirical up to $\Sigma^{\le k}$).
- Minimization of transducers (conversion produces standard canonical state-splitting models; minimization is a post-processing optimization).

---

## 5. Theory of Mealy and Moore Machines

| Dimension | Mealy Machine | Moore Machine |
|---|---|---|
| **Output Function** | $\lambda_M: Q \times \Sigma \to \Gamma$ | $\lambda_O: Q \to \Gamma$ |
| **Output Association** | Associated with transitions | Associated with states |
| **Output Length ($|w|=n$)** | $n$ symbols | $n + 1$ symbols (includes $t=0$ initial output) |
| **State Complexity** | Typically fewer states | Often requires state splitting ($|Q'| \le |Q| \cdot |\Gamma|$) |
| **Hardware Timing** | Reacts within current clock cycle | Reacts after clock edge (synchronous flip-flop) |
| **Circuit Susceptibility** | Prone to input noise glitches | Glitch-free; outputs isolated by registers |

---

## 6. Mathematical Notation

A deterministic finite transducer is a 6-tuple:
$$\mathcal{M} = (Q, \Sigma, \Gamma, \delta, \lambda, q_0)$$
- $Q = \{q_0, q_1, \dots, q_{m-1}\}$: Finite set of states.
- $\Sigma = \{a_1, a_2, \dots, a_k\}$: Finite input alphabet.
- $\Gamma = \{z_1, z_2, \dots, z_l\}$: Finite output alphabet.
- $\delta: Q \times \Sigma \to Q$: State transition function.
- $\lambda$: Output function ($\lambda_M: Q \times \Sigma \to \Gamma$ for Mealy, $\lambda_O: Q \to \Gamma$ for Moore).
- $q_0 \in Q$: Designated start state.

### Output Alignment Theorem
For any input string $w \in \Sigma^*$:
$$\text{Output}_{Moore}(w) = y_0 \cdot \text{Output}_{Mealy}(w)$$
where $y_0 = \lambda_O(q_0')$ is the initial state output emitted at $t=0$.

---

## 7. Conversion Algorithms

### 7.1 Mealy → Moore (State Splitting)
1. **Analyze Incoming Outputs:** For each destination state $p \in Q$:
   $$\text{incoming\_outputs}(p) = \{ \lambda_M(q, a) \mid q \in Q, a \in \Sigma, \delta_M(q, a) = p \}$$
2. **State Splitting:**
   - If $|\text{incoming\_outputs}(p)| > 1$: State $p$ splits into copies $(p, z)$ for each $z \in \text{incoming\_outputs}(p)$.
   - If $|\text{incoming\_outputs}(p)| = 1$: State $p$ forms $(p, z)$ where $z$ is the sole incoming output.
   - If $|\text{incoming\_outputs}(p)| = 0$ (e.g. initial state with no self-loops): State $p$ forms $(p, y_0)$ with initial output $y_0$.
3. **Transition Re-mapping:** For each Moore state $(p, z)$ and input $a \in \Sigma$:
   $$\delta'((p, z), a) = (\delta_M(p, a), \lambda_M(p, a))$$
   $$\lambda'((p, z)) = z$$
4. **Initial State:** Set $q_0' = (q_0, y_0)$.

### 7.2 Moore → Mealy (Direct Destination Output Mapping)
1. **State Preservation:** $Q' = Q$, $q_0' = q_0$.
2. **Transition Output Assignment:** For every state $q \in Q$ and input $a \in \Sigma$:
   $$\delta'(q, a) = \delta(q, a) = p$$
   $$\lambda'(q, a) = \lambda_O(p) \quad (\text{Output of destination state } p)$$

---

## 8. System Architecture

```text
mealy-moore-simulator/
├── app.py                     # Streamlit frontend & interactive orchestration
├── requirements.txt           # Virtual environment package dependencies
├── README.md                  # Comprehensive project documentation
├── pytest.ini                 # Pytest configuration
├── .gitignore                 # Version control exclusions
├── src/
│   ├── __init__.py
│   ├── models.py              # MealyMachine, MooreMachine, ValidationResult data models
│   ├── validation.py          # Deterministic completeness & reachability checks
│   ├── mealy_to_moore.py      # State-splitting conversion algorithm & step traces
│   ├── moore_to_mealy.py      # Destination-state output mapping conversion algorithm
│   ├── simulation.py          # String simulation engine with step traces and paths
│   ├── equivalence.py         # Behavioral verification & bounded exhaustive testing
│   ├── visualization.py       # Graphviz DOT generator and Mermaid fallback
│   ├── examples.py            # Built-in presets (2's complement, splitters, counters)
│   └── ui_helpers.py          # Custom CSS, card layout, and diagram renderers
├── tests/
│   ├── test_validation.py     # Structural validation unit tests
│   ├── test_mealy_to_moore.py # State splitting & Mealy->Moore tests
│   ├── test_moore_to_mealy.py # State preservation & Moore->Mealy tests
│   ├── test_simulation.py     # String execution and path tracing tests
│   └── test_equivalence.py    # Equivalence & bounded verification tests
└── docs/
    ├── algorithm.md           # Formal pseudocode and worked examples
    └── viva_questions.md      # 22 curated viva voce questions and answers
```

### Existing Tools & Feasibility Analysis
- **Streamlit:** Chosen for its reactive state management, interactive data editors, and rapid web deployment without heavy Node.js toolchains.
- **Graphviz:** Industry standard for directed graphs. In Streamlit, `st.graphviz_chart` utilizes client-side WebAssembly/Viz.js, ensuring diagrams render seamlessly even on machines without system-level `dot` CLI binaries installed.
- **Mermaid.js Fallback:** Built into the simulator to guarantee 100% visualization uptime if browser rendering issues occur.

---

## 9. Data Structures

The system uses standard, typed Python data structures for transparency and serialization:
- **State Sets & Alphabets:** `List[str]` with order and uniqueness preservation.
- **Mealy Transitions:** `Dict[Tuple[str, str], str]` mapping `(current_state, symbol) -> next_state`.
- **Mealy Outputs:** `Dict[Tuple[str, str], str]` mapping `(current_state, symbol) -> output_symbol`.
- **Moore Outputs:** `Dict[str, str]` mapping `state -> output_symbol`.
- **Step Traces:** `List[ConversionStep]` carrying step numbers, titles, mathematical descriptions, and Pandas DataFrames.

---

## 10. Installation Instructions

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14.
- Git (optional, for version control).

### Step-by-Step Setup
1. **Clone or navigate to the project directory:**
   ```bash
   cd MEALY_TO_MOORE_SIMULATOR
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate    # On macOS/Linux
   # or .venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 11. Execution Instructions

### Running the Application
Launch the Streamlit web application:
```bash
streamlit run app.py
```
Or with explicit virtual environment binary:
```bash
.venv/bin/streamlit run app.py
```

The application will open automatically in your browser at `http://localhost:8501`.

### Running the Pytest Test Suite
To execute the automated unit test suite:
```bash
pytest -v
```
Or:
```bash
.venv/bin/pytest -v
```

---

## 12. Example Inputs and Expected Outputs

### Manual Validation Example: Two's Complement Generator (Mealy → Moore)
- **Input Mealy Machine:**
  - $Q = \{q_0, q_1\}$, $\Sigma = \{0, 1\}$, $\Gamma = \{0, 1\}$, $q_0$ initial.
  - $\delta(q_0, 0) = q_0, \lambda(q_0, 0) = 0$
  - $\delta(q_0, 1) = q_1, \lambda(q_0, 1) = 1$
  - $\delta(q_1, 0) = q_1, \lambda(q_1, 0) = 1$
  - $\delta(q_1, 1) = q_1, \lambda(q_1, 1) = 0$
- **Expected Converted Moore Machine:**
  - States: $Q' = \{q_{0\_0}, q_{1\_0}, q_{1\_1}\}$ (3 states; $q_1$ was split!).
  - State Outputs: $\lambda(q_{0\_0}) = 0, \lambda(q_{1\_0}) = 0, \lambda(q_{1\_1}) = 1$.
  - Start State: $q_{0\_0}$ with initial output `0`.
- **Behavioral Test on `0011`:**
  - Mealy Output: `0010`
  - Moore Output: `00010` = `0` $\cdot$ `0010` (Equivalent under suffix alignment).

---

## 13. Testing and Validation Methodology

The project incorporates a two-layer validation framework:
1. **Automated Unit Testing (`pytest`):**
   - 23 tests verifying structural validation, state splitting, destination mapping, edge cases, string simulations, and suite equivalence.
2. **Interactive Bounded Exhaustive Testing:**
   - In the web app, students can verify bounded equivalence for all strings in $\Sigma^{\le k}$ ($k \in \{1, 2, 3, 4\}$).
   - Verifies that $\text{Moore}(w) = y_0 \cdot \text{Mealy}(w)$ holds for 100% of generated test cases.

---

## 14. Known Limitations

- **Bounded vs Universal Proof:** Bounded exhaustive verification demonstrates empirical equivalence up to length $k$, but is not a replacement for mathematical induction.
- **Transducer Minimization:** The state-splitting algorithm creates canonical split states. If redundant equivalent states emerge, Moore machine minimization (partition refinement) can be applied as a future extension.

---

## 15. Future Enhancements

- Transducer state minimization algorithm (Hopcroft's partition refinement for Moore machines).
- Support for non-deterministic finite transducers (NFTs).
- Direct export of Verilog / VHDL HDL code for hardware synthesis of the converted FSMs.

---

## 16. Assessment Compliance Matrix (CSET302)

| Assessment Criterion | Implementation Location | Evidence |
|---|---|---|
| **Problem Definition & Formal Specs** | Section 1, 2, 5, 6 | 6-tuple mathematical formulation, output function contrast |
| **Existing Tools & Feasibility Analysis** | Section 8 | Streamlit, Graphviz WebAssembly, and Mermaid fallback analysis |
| **Architecture & Workflow** | Section 8, `app.py`, `src/` | 5-stage pipeline, modular directory structure |
| **Independent Algorithm Implementation** | `src/mealy_to_moore.py`, `src/moore_to_mealy.py` | State-splitting & destination mapping implemented without 3rd-party automata packages |
| **Dynamic User Input** | `app.py` (Tab 1) | Dynamic table editor, custom state/alphabet inputs, JSON import/export |
| **Step-by-Step Visualization** | `app.py` (Tab 3), `docs/algorithm.md` | 8-step Mealy trace, 6-step Moore trace with intermediate DataFrames |
| **Automata Diagrams** | `src/visualization.py`, `app.py` | Graphviz DOT and Mermaid dual-rendering engine |
| **Results & Tables** | `app.py` (Tab 2) | Comparative metrics cards, transition tables, CSV downloads |
| **Validation & Equivalence** | `src/equivalence.py`, `tests/` | Bounded exhaustive testing, 23 passing pytest tests |
| **Preliminary Prototype** | `app.py` | Runnable, responsive Streamlit web application |
| **Manual Worked Example** | Section 12, `docs/algorithm.md` | 2's complement Mealy $\to$ Moore and Modulo 3 Moore $\to$ Mealy |
| **Viva Voce Preparation** | `docs/viva_questions.md`, `app.py` | 22 comprehensive Q&As for assessment |
