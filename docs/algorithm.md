# Formal Algorithms & Worked Examples: Mealy ↔ Moore Machine Conversion

**Course:** CSET302 – Automata Theory and Computability  
**Topic 14:** Mealy ↔ Moore Machine Conversion Simulator  
**Author:** Kartikkk  

---

## 1. Theoretical Foundations

A **finite-state transducer (FST)** is an extension of a finite automaton that generates an output sequence based on state transitions.

### 1.1 Formal Definitions

A **Mealy Machine** is formally defined as a 6-tuple:
$$\mathcal{M}_{Mealy} = (Q, \Sigma, \Gamma, \delta, \lambda_M, q_0)$$
where:
- $Q$ is a non-empty finite set of states.
- $\Sigma$ is a non-empty finite input alphabet.
- $\Gamma$ is a non-empty finite output alphabet.
- $\delta: Q \times \Sigma \to Q$ is the state transition function.
- $\lambda_M: Q \times \Sigma \to \Gamma$ is the transition output function.
- $q_0 \in Q$ is the designated initial state.

A **Moore Machine** is formally defined as a 6-tuple:
$$\mathcal{M}_{Moore} = (Q', \Sigma, \Gamma, \delta', \lambda_O, q_0')$$
where:
- $Q'$ is a non-empty finite set of states.
- $\Sigma$ is the input alphabet.
- $\Gamma$ is the output alphabet.
- $\delta': Q' \times \Sigma \to Q'$ is the state transition function.
- $\lambda_O: Q' \to \Gamma$ is the state output function.
- $q_0' \in Q'$ is the initial state.

### 1.2 Output Alignment Theorem
For any input string $w = a_1 a_2 \dots a_n \in \Sigma^*$:
- The Mealy machine produces output:
  $$\lambda_M(q_0, a_1) \lambda_M(q_1, a_2) \dots \lambda_M(q_{n-1}, a_n) \quad (\text{length } n)$$
- The Moore machine produces output:
  $$\lambda_O(q_0') \lambda_O(q_1') \dots \lambda_O(q_n') \quad (\text{length } n + 1)$$
where $q_0'$ emits output $y_0 = \lambda_O(q_0')$ at time $t = 0$ before consuming any input symbol.
Two machines are **behaviorally equivalent** if and only if for all $w \in \Sigma^*$:
$$\text{Output}_{Moore}(w) = y_0 \cdot \text{Output}_{Mealy}(w)$$

---

## 2. Mealy → Moore Conversion Algorithm

### 2.1 State-Splitting Pseudocode

```text
Algorithm: Convert_Mealy_To_Moore
Input: Complete Deterministic Mealy Machine M = (Q, Sigma, Gamma, delta, lambda, q0)
Output: Equivalent Moore Machine M' = (Q', Sigma, Gamma, delta', lambda', q0')

1. Validate M:
     Ensure Q, Sigma, Gamma are non-empty.
     Ensure for every q in Q and a in Sigma, delta(q, a) and lambda(q, a) are defined.

2. Determine Incoming Outputs:
     Initialize incoming_outputs[p] = empty set for all p in Q.
     For each state q in Q:
         For each symbol a in Sigma:
             p = delta(q, a)
             z = lambda(q, a)
             incoming_outputs[p] = incoming_outputs[p] U {z}

3. Determine Initial State Output y0:
     If incoming_outputs[q0] is non-empty:
         y0 = min(incoming_outputs[q0])
     Else:
         y0 = first_element(Gamma)

4. Generate Moore State Set Q':
     Initialize Q' = empty set.
     For each state p in Q:
         If incoming_outputs[p] is empty:
             Add (p, y0 if p == q0 else first_element(Gamma)) to Q'
         Else:
             For each z in incoming_outputs[p]:
                 Add (p, z) to Q'
     If (q0, y0) not in Q':
         Add (q0, y0) to Q'

5. Assign Moore State Outputs:
     For each Moore state (p, z) in Q':
         lambda'((p, z)) = z

6. Construct Moore Transitions:
     For each Moore state (p, z) in Q':
         For each input symbol a in Sigma:
             next_p = delta(p, a)
             next_z = lambda(p, a)
             delta'((p, z), a) = (next_p, next_z)

7. Designate Initial State:
     q0' = (q0, y0)

8. Return M' = (Q', Sigma, Gamma, delta', lambda', q0')
```

### 2.2 Worked Example: Two's Complement Generator (LSB First)

#### Input Mealy Machine
- $Q = \{q_0, q_1\}$, $\Sigma = \{0, 1\}$, $\Gamma = \{0, 1\}$, start state: $q_0$.
- Transition Table:

| State | Input `0`: Next State / Output | Input `1`: Next State / Output |
|---|---|---|
| $\to q_0$ | $q_0$ / `0` | $q_1$ / `1` |
| $q_1$ | $q_1$ / `1` | $q_1$ / `0` |

#### Step 1: Incoming Outputs Analysis
- Destination $q_0$: Entered by $(q_0, 0) \to q_0$ with output `0`.
  $$\text{incoming\_outputs}[q_0] = \{0\}$$
- Destination $q_1$: Entered by $(q_0, 1) \to q_1$ (out `1`), $(q_1, 0) \to q_1$ (out `1`), and $(q_1, 1) \to q_1$ (out `0`).
  $$\text{incoming\_outputs}[q_1] = \{0, 1\}$$

#### Step 2: State Splitting
- $q_0$ has 1 incoming output: forms $(q_0, 0) \to q_{0\_0}$.
- $q_1$ has 2 incoming outputs $\{0, 1\}$: **SPLITS** into $(q_1, 0) \to q_{1\_0}$ and $(q_1, 1) \to q_{1\_1}$.

#### Step 3: Converted Moore Machine
- $Q' = \{q_{0\_0}, q_{1\_0}, q_{1\_1}\}$
- Initial State: $q_{0\_0}$ with initial output $\lambda_O(q_{0\_0}) = 0$.
- Moore Transition Table:

| State | State Output $\lambda_O$ | Next State on `0` | Next State on `1` |
|---|---|---|---|
| $\to q_{0\_0}$ | `0` | $q_{0\_0}$ | $q_{1\_1}$ |
| $q_{1\_0}$ | `0` | $q_{1\_1}$ | $q_{1\_0}$ |
| $q_{1\_1}$ | `1` | $q_{1\_1}$ | $q_{1\_0}$ |

#### Step 4: Verification on Input `0011`
- Mealy trace:
  - $(q_0, 0) \to q_0$ emits `0`
  - $(q_0, 0) \to q_0$ emits `0`
  - $(q_0, 1) \to q_1$ emits `1`
  - $(q_1, 1) \to q_1$ emits `0`
  - Total Mealy output: `0010`
- Moore trace:
  - Initial state $q_{0\_0}$ emits `0` (at $t=0$)
  - on `0`: moves to $q_{0\_0}$, emits `0`
  - on `0`: moves to $q_{0\_0}$, emits `0`
  - on `1`: moves to $q_{1\_1}$, emits `1`
  - on `1`: moves to $q_{1\_0}$, emits `0`
  - Total Moore output: `00010` = `0` $\cdot$ `0010` (Exact Match!).

---

## 3. Moore → Mealy Conversion Algorithm

### 3.1 Pseudocode

```text
Algorithm: Convert_Moore_To_Mealy
Input: Complete Deterministic Moore Machine M = (Q, Sigma, Gamma, delta, lambda, q0)
Output: Equivalent Mealy Machine M' = (Q, Sigma, Gamma, delta', lambda', q0)

1. Validate M:
     Ensure Q, Sigma, Gamma are non-empty.
     Ensure every state in Q has a defined output lambda(q) in Gamma.
     Ensure every transition delta(q, a) is defined.

2. State preservation:
     Q' = Q
     q0' = q0

3. Assign Mealy Transitions and Outputs:
     For each state q in Q:
         For each symbol a in Sigma:
             p = delta(q, a)             # Destination state
             delta'(q, a) = p
             lambda'(q, a) = lambda(p)   # Destination state output

4. Return M' = (Q', Sigma, Gamma, delta', lambda', q0')
```

### 3.2 Worked Example: Residue Modulo 3 Counter

#### Input Moore Machine
- $Q = \{q_0, q_1, q_2\}$, $\Sigma = \{0, 1\}$, $\Gamma = \{0, 1, 2\}$, initial state $q_0$.
- State outputs: $\lambda(q_0) = 0, \lambda(q_1) = 1, \lambda(q_2) = 2$.
- Moore Transition Table:

| State | Output $\lambda$ | Next on `0` | Next on `1` |
|---|---|---|---|
| $\to q_0$ | `0` | $q_0$ | $q_1$ |
| $q_1$ | `1` | $q_2$ | $q_0$ |
| $q_2$ | `2` | $q_1$ | $q_2$ |

#### Transition Mapping
For each transition $q \xrightarrow{a} p$, set $\lambda_M(q, a) = \lambda_O(p)$:
- From $q_0$: on `0` goes to $q_0$ (output $\lambda_O(q_0) = 0$), on `1` goes to $q_1$ (output $\lambda_O(q_1) = 1$).
- From $q_1$: on `0` goes to $q_2$ (output $\lambda_O(q_2) = 2$), on `1` goes to $q_0$ (output $\lambda_O(q_0) = 0$).
- From $q_2$: on `0` goes to $q_1$ (output $\lambda_O(q_1) = 1$), on `1` goes to $q_2$ (output $\lambda_O(q_2) = 2$).

#### Converted Mealy Machine

| State | Input `0`: Next / Output | Input `1`: Next / Output |
|---|---|---|
| $\to q_0$ | $q_0$ / `0` | $q_1$ / `1` |
| $q_1$ | $q_2$ / `2` | $q_0$ / `0` |
| $q_2$ | $q_1$ / `1` | $q_2$ / `2` |

- State count is preserved: $|Q_{Mealy}| = |Q_{Moore}| = 3$.
- Output sequence equivalence holds for any binary input stream.
