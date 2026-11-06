# Learning science

The methods Switchback is built on, and the features they drive. Rule of thumb: if a feature doesn't trace back to one of these, question it.

## Principles → features

| Principle | What the research says | Where it shows up |
|---|---|---|
| **Retrieval practice** | Pulling knowledge out of memory strengthens it far more than re-reading it | Quizzes, recall prompts, reviews; very little passive re-reading |
| **Spacing** | Practice spread out over time beats cramming for long-term retention | The review scheduler (FSRS) |
| **Successive relearning** | Retrieve until correct, then repeat across spaced sessions; this produces durable knowledge | "Mastered" only after a delayed review. A missed question comes back as a fresh one on the same skill until it's right on 2 different days ([ADR-0011](decisions/0011-mistakes-come-back.md)) |
| **Interleaving** | Mixing problem types teaches you to *choose* the right method, not just apply the one you just saw | Practice and reviews mix current and older topics |
| **Mastery learning** | Move on only when the prerequisites are solid | Gating with test-out |
| **Worked examples, then fading** | Novices learn more from studying solutions than from solving problems; help should fade as skill grows | The practice ladder: worked example → half-finished code → blank file |
| **Whole-task learning (4C/ID)** | Complex skills transfer best when you practice whole, realistic tasks, simple to complex, with fading support | Projects and "prove it" builds, not just isolated drills |
| **Self-explanation** | Explaining *why* in your own words deepens understanding and exposes gaps | Explain-it-back checks |
| **Desirable difficulties** | Some struggle (recall, spacing, variation) slows practice but improves long-term learning | Blank-editor challenges; no answer-giving AI |
| **Feedback on confident errors** | Mistakes made with high confidence, once corrected, are remembered especially well | Immediate, specific feedback. Candidate feature: ask for confidence before revealing answers |
| **Dual coding / multimedia** | Words plus well-designed visuals beat words alone | Diagrams, execution visualizations, embedded videos |

## Programming-specific methods

| Method | What it is | Where it shows up |
|---|---|---|
| **Tracing before writing** | Novices who can't trace code by hand rarely write it well; reading skill comes first | "Predict the output" exercises early in each topic |
| **Parsons problems** | Rearrange scrambled lines into a working program; teaches structure with less mental load | Early practice steps |
| **PRIMM** | Predict → Run → Investigate → Modify → Make | The order of the practice ladder |
| **Notional machine** | A mental model of what the computer actually does as code runs | Step-through visualizations of variables, memory and the call stack |
| **Subgoal labels** | Worked examples whose steps are labeled by purpose transfer better | Worked examples show labeled steps |
| **Debugging as a skill** | Reading and fixing unfamiliar code is a core, trainable skill | Debug-unfamiliar-code checks |

## AI and learning

Unrestricted, answer-giving AI can make practice look better while hurting real learning. In a large field study, students with unrestricted GPT-4 access did better on practice problems but worse on later exams taken without AI; a tutor version with guardrails largely avoided the harm (Bastani et al., 2025). That's why our tutor only gives hints and why "prove it" checks are AI-free ([ADR-0003](decisions/0003-ai-roles-and-guardrails.md)).

## Myths we avoid

- **Learning styles.** There's no good evidence that matching teaching to "visual" or "auditory" learners helps (Pashler et al., 2008). We personalize by what you *know*, not by a preferred format.
- **Re-reading and highlighting** feel productive but do little for retention. We use retrieval instead.

## Adaptive engine background

- **Knowledge tracing** estimates what a learner knows from their answers (Corbett & Anderson, 1994). Modern variants use machine learning.
- **Knowledge space theory** models a subject as a prerequisite structure and uses it for efficient placement tests (Doignon & Falmagne; it powers ALEKS).
- **FSRS** is an open-source scheduler that predicts when you'll forget something and schedules the review just before then (Ye et al., 2022; used by Anki).
- **Implicit repetition** (Math Academy's "FIRe"): practicing an advanced topic counts as partial review of the simpler topics it uses (Skycak).

## References

- Bastani, H., et al. (2025). Generative AI without guardrails can harm learning: Evidence from high school mathematics. *PNAS*.
- Bjork, R. A. (1994). Memory and metamemory considerations in the training of human beings. In *Metacognition: Knowing about Knowing*. MIT Press.
- Bloom, B. S. (1968). Learning for mastery. *Evaluation Comment*. And (1984). The 2 sigma problem. *Educational Researcher*.
- Butterfield, B., & Metcalfe, J. (2001). Errors committed with high confidence are hypercorrected. *Journal of Experimental Psychology: Learning, Memory, and Cognition*.
- Cepeda, N. J., et al. (2006). Distributed practice in verbal recall tasks: A review and quantitative synthesis. *Psychological Bulletin*.
- Chi, M. T. H., et al. (1989). Self-explanations: How students study and use examples in learning to solve problems. *Cognitive Science*.
- Corbett, A. T., & Anderson, J. R. (1994). Knowledge tracing: Modeling the acquisition of procedural knowledge. *User Modeling and User-Adapted Interaction*.
- Doignon, J.-P., & Falmagne, J.-C. (1999). *Knowledge Spaces*. Springer.
- du Boulay, B. (1986). Some difficulties of learning to program. *Journal of Educational Computing Research*.
- Lister, R., et al. (2004). A multi-national study of reading and tracing skills in novice programmers. *ITiCSE Working Group Reports*.
- Margulieux, L. E., Guzdial, M., & Catrambone, R. (2012). Subgoal-labeled instructional material improves performance and transfer in learning to develop mobile applications. *ICER*.
- Mayer, R. E. *Multimedia Learning*. Cambridge University Press.
- Parsons, D., & Haden, P. (2006). Parson's programming puzzles: A fun and effective learning tool for first programming courses. *ACE*.
- Pashler, H., et al. (2008). Learning styles: Concepts and evidence. *Psychological Science in the Public Interest*.
- Rawson, K. A., & Dunlosky, J. (2011). Optimizing schedules of retrieval practice for durable and efficient learning: How much is enough? *Journal of Experimental Psychology: General*.
- Renkl, A., & Atkinson, R. K. (2003). Structuring the transition from example study to problem solving in cognitive skill acquisition. *Educational Psychologist*.
- Roediger, H. L., & Karpicke, J. D. (2006). Test-enhanced learning: Taking memory tests improves long-term retention. *Psychological Science*.
- Rohrer, D., & Taylor, K. (2007). The shuffling of mathematics problems improves learning. *Instructional Science*.
- Sentance, S., Waite, J., & Kallia, M. (2019). Teaching computer programming with PRIMM: A sociocultural perspective. *Computer Science Education*.
- Skycak, J. Individualized spaced repetition in hierarchical knowledge structures. justinmath.com.
- Sweller, J. (1988). Cognitive load during problem solving: Effects on learning. *Cognitive Science*.
- van Merriënboer, J. J. G., & Kirschner, P. A. *Ten Steps to Complex Learning*. Routledge.
- Ye, J., Su, J., & Cao, Y. (2022). A stochastic shortest path algorithm for optimizing spaced repetition scheduling. *KDD*.
