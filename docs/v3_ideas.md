# NeuronBox v3 ideas

Steve wants this kept in mind for the whole v2 campaign: brain-structure
changes that raise the plateau, both the theoretical ceiling and what
evolution reaches in practice, without much extra compute. The brain viewer
already freezes on v2's 1,239 synapses.

**Fixed constraint:** day-one behavior identical to the base bibite. This
was the reason for v2's all-zero start: it prevents mass extinction during
AFK runs.

**Steve has rejected** (at v1/v2 design): weights starting slightly off
zero, and input→L2 or L1→output shortcut connections.

## Claude's ideas (2026-11-01, unverified)

### Computational: raising the ceiling

1. **Mixed neuron types instead of all-sine.** The game already has the
   primitives that sine networks must stumble onto:
   - **Latch / SoftLatch:** a guaranteed 1-bit memory. A sine self-loop
     only latches with weight ~1–2.26.
   - **Integrator:** an accumulator for counting, timing and crude dead
     reckoning. With exact arithmetic, two counters suffice for Turing
     completeness. Floats cap that, but it's beyond "a few stable states".
     The official *Fibonacci turner* template is built on these node types.
   - **Mult:** gating, i.e. context-dependent behavior ("if hungry, steer
     to food"). It is hard to build from sums of sines.
   - **Differential:** rate of change ("food getting closer").

   Neutrality is safe as long as the connections into outputs start at 0:
   nothing internal reaches behavior, whatever its type. Each type's exact
   semantics should be checked in the decompiled code first.
2. **Spend synapses more efficiently.** Cost scales with connection count.
   In v2, 180 are outputs→L1 and 180 are L3→outputs. Sparser connectivity
   with more neurons usually buys more capability per synapse.

### Evolutionary: raising what evolution reaches

3. **Shorter paths from senses to actions.** v2's sense→action signal is a
   product of four weights (input→L1→L2→L3→output), all of which must grow
   before anything shows. That is the main reason sensing is slow. Options:
   - **Fewer, wider layers.** Recurrence already supplies depth over time.
   - **A "reservoir":** non-zero *internal* weights, with only the
     connections into outputs at 0 (cf. echo state networks / liquid state
     machines).
     - It gives rich internal signals and short-term memory from day one,
       so evolution only needs to grow the output connections: one weight
       instead of four.
     - Day-one behavior stays exactly identical, because nothing reaches
       outputs.
     - This differs from the rejected "weights off zero" idea, which put
       non-zero weights on the path to behavior. It still needs Steve's call.
     - Risk: random sine loops can be chaotic noise, so the internal
       weights need scaling into the calm range.
4. **Modularity.** In v2 every L3 neuron feeds every output, so a mutation
   that improves egg laying can disturb steering. Separate small sub-networks
   (movement, eating, reproduction) that share inputs and allow some
   cross-talk mean improvements interfere less. That is known to help
   evolvability when conditions change, and it uses fewer synapses.
5. **Fewer parameters, each mutated more often.** Brain mutations per birth
   are capped at 10 and spread over every weight and bias. Unused synapses
   dilute the mutation rate of useful ones.

## Evidence from v2 (tracked by `tools/run_stats.py`)

- **Latches:** self-loop weights in the 1–2.26 window.
- **Feedback use:** L3→L1 and outputs→L1 weights rising above the background
  drift of the forward connections.
- **What evolves first:** which outputs inputs reach, own-state vs
  surroundings.

**At 11-01 (gen ~64):**
- No latches. The largest self-loop is +0.53 (leaky), out of 18,540 across
  515 bibites.
- Every connection kind sits at a mean |w| of ~0.045–0.053, so feedback
  isn't distinguishable from drift yet.
- Self-loops are a bit higher at 0.066. Unexplained; watch it.
- Inputs reach Want2Attack, the pheromone outputs and Want2Heal most;
  Want2Lay and Rotate least.
