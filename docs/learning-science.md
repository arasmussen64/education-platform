# Learning science

The methods Switchback is built on, and the features they drive. Rule of thumb: if a feature doesn't trace back to one of these, question it.

## Principles → features

| Principle                        | What the research says                                                                                                                                                                                  | Where it shows up                                                                                                                                                                                                     |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Retrieval practice**           | Pulling knowledge out of memory strengthens it far more than re-reading it                                                                                                                              | Quizzes, recall prompts, reviews; very little passive re-reading                                                                                                                                                      |
| **Spacing**                      | Practice spread out over time beats cramming for long-term retention                                                                                                                                    | The review scheduler (FSRS)                                                                                                                                                                                           |
| **Successive relearning**        | Retrieve until correct, then repeat across spaced sessions; this produces durable knowledge                                                                                                             | "Mastered" only after a delayed review. A missed question comes back as a fresh one on the same skill, after 1, 3 and 7 days, until it's right on 3 different days ([ADR-0011](decisions/0011-mistakes-come-back.md)) |
| **Interleaving**                 | Mixing problem types teaches you to _choose_ the right method, not just apply the one you just saw                                                                                                      | Practice and reviews mix current and older topics                                                                                                                                                                     |
| **Mastery learning**             | Move on only when the prerequisites are solid; after a check, corrective practice on what was missed, then a fresh, parallel check                                                                      | Gating with test-out. A missed checkpoint test brings its skill back, and a stuck learner proves the checkpoint on a fresh version ([ADR-0012](decisions/0012-checkpoint-support.md))                                 |
| **Worked examples, then fading** | Novices learn more from studying solutions than from solving problems; help should fade as skill grows                                                                                                  | The practice ladder: worked example → half-finished code → blank file. A checkpoint's way through: a solved sibling → the build in steps → a fresh version from a blank editor                                        |
| **Whole-task learning (4C/ID)**  | Complex skills transfer best when you practice whole, realistic tasks, simple to complex, with fading support                                                                                           | Projects and "prove it" builds, not just isolated drills                                                                                                                                                              |
| **Self-explanation**             | Explaining _why_ in your own words deepens understanding and exposes gaps                                                                                                                               | Explain-it-back checks                                                                                                                                                                                                |
| **Desirable difficulties**       | Some struggle (recall, spacing, variation) slows practice but improves long-term learning                                                                                                               | Blank-editor challenges; no answer-giving AI                                                                                                                                                                          |
| **Feedback on confident errors** | Mistakes made with high confidence, once corrected, are remembered especially well                                                                                                                      | Immediate, specific feedback. Candidate feature: ask for confidence before revealing answers                                                                                                                          |
| **Dual coding / multimedia**     | Words plus well-designed visuals beat words alone                                                                                                                                                       | Diagrams, execution visualizations, embedded videos                                                                                                                                                                   |
| **Deliberate practice**          | Expertise tracks hours of focused, effortful practice on tasks just beyond current skill, with feedback (Ericsson et al., 1993); the "10,000 hours" figure is a popularization of that work, not a rule | The practice-hours tracker on the Today page counts only time spent on graded attempts, Checks, explanations and reviews, never time with the site open, and marks milestones from 1 hour to 10,000                   |

## Programming-specific methods

| Method                     | What it is                                                                                                                                       | Where it shows up                                                                                                        |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| **Tracing before writing** | Novices who can't trace code by hand rarely write it well; reading skill comes first                                                             | "Predict the output" exercises early in each topic                                                                       |
| **Parsons problems**       | Rearrange scrambled lines into a working program; teaches structure with less mental load                                                        | Early practice steps                                                                                                     |
| **PRIMM**                  | Predict → Run → Investigate → Modify → Make                                                                                                      | The order of the practice ladder                                                                                         |
| **Notional machine**       | A mental model of what the computer actually does as code runs                                                                                   | Step-through visualizations of variables, memory and the call stack                                                      |
| **Subgoal labels**         | Worked examples whose steps are labeled by purpose transfer better                                                                               | Worked examples show labeled steps                                                                                       |
| **Debugging as a skill**   | Reading and fixing unfamiliar code is a core, trainable skill                                                                                    | Debug-unfamiliar-code checks                                                                                             |
| **The notional machine**   | Novices need a working model of what each line does to the variables; tracing is the skill that builds it (du Boulay, 1986; Lister et al., 2004) | Predict-the-output questions, then Step through ([ADR-0022](decisions/0022-step-through.md)) to watch the machine's view |

## AI and learning

Unrestricted, answer-giving AI can make practice look better while hurting real learning. In a large field study, students with unrestricted GPT-4 access did better on practice problems but worse on later exams taken without AI; a tutor version with guardrails largely avoided the harm (Bastani et al., 2025). That's why our tutor only gives hints and why "prove it" checks are AI-free ([ADR-0003](decisions/0003-ai-roles-and-guardrails.md)).

## Myths we avoid

- **Learning styles.** There's no good evidence that matching teaching to "visual" or "auditory" learners helps (Pashler et al., 2008). We personalize by what you _know_, not by a preferred format.
- **Re-reading and highlighting** feel productive but do little for retention. We use retrieval instead.

## Adaptive engine background

- **Knowledge tracing** estimates what a learner knows from their answers (Corbett & Anderson, 1994). Modern variants use machine learning.
- **Knowledge space theory** models a subject as a prerequisite structure and uses it for efficient placement tests (Doignon & Falmagne; it powers ALEKS). Our placement test ([ADR-0021](decisions/0021-placement-test.md)) is the one-dimensional case: a track's topics in order are close to a chain, so what a learner knows is near enough a prefix, and finding its end is a binary search with the topic's own review questions as probes.
- **FSRS** is an open-source scheduler that predicts when you'll forget something and schedules the review just before then (Ye et al., 2022; used by Anki).
- **Implicit repetition** (Math Academy's "FIRe"): practicing an advanced topic counts as partial review of the simpler topics it uses (Skycak).

## References

- Bastani, H., et al. (2025). Generative AI without guardrails can harm learning: Evidence from high school mathematics. _PNAS_.
- Bjork, R. A. (1994). Memory and metamemory considerations in the training of human beings. In _Metacognition: Knowing about Knowing_. MIT Press.
- Bloom, B. S. (1968). Learning for mastery. _Evaluation Comment_. And (1984). The 2 sigma problem. _Educational Researcher_.
- Butterfield, B., & Metcalfe, J. (2001). Errors committed with high confidence are hypercorrected. _Journal of Experimental Psychology: Learning, Memory, and Cognition_.
- Cepeda, N. J., et al. (2006). Distributed practice in verbal recall tasks: A review and quantitative synthesis. _Psychological Bulletin_.
- Cepeda, N. J., Vul, E., Rohrer, D., Wixted, J. T., & Pashler, H. (2008). Spacing effects in learning: A temporal ridgeline of optimal retention. _Psychological Science_.
- Chi, M. T. H., et al. (1989). Self-explanations: How students study and use examples in learning to solve problems. _Cognitive Science_.
- Corbett, A. T., & Anderson, J. R. (1994). Knowledge tracing: Modeling the acquisition of procedural knowledge. _User Modeling and User-Adapted Interaction_.
- Doignon, J.-P., & Falmagne, J.-C. (1999). _Knowledge Spaces_. Springer.
- du Boulay, B. (1986). Some difficulties of learning to program. _Journal of Educational Computing Research_.
- Guskey, T. R. (2007). Closing achievement gaps: Revisiting Benjamin S. Bloom's "Learning for Mastery". _Journal of Advanced Academics_.
- Lister, R., et al. (2004). A multi-national study of reading and tracing skills in novice programmers. _ITiCSE Working Group Reports_.
- Margulieux, L. E., Guzdial, M., & Catrambone, R. (2012). Subgoal-labeled instructional material improves performance and transfer in learning to develop mobile applications. _ICER_.
- Mayer, R. E. _Multimedia Learning_. Cambridge University Press.
- Parsons, D., & Haden, P. (2006). Parson's programming puzzles: A fun and effective learning tool for first programming courses. _ACE_.
- Pashler, H., et al. (2008). Learning styles: Concepts and evidence. _Psychological Science in the Public Interest_.
- Rawson, K. A., & Dunlosky, J. (2011). Optimizing schedules of retrieval practice for durable and efficient learning: How much is enough? _Journal of Experimental Psychology: General_.
- Rawson, K. A., Dunlosky, J., & Sciartelli, S. M. (2013). The power of successive relearning: Improving performance on course exams and long-term retention. _Educational Psychology Review_.
- Renkl, A., & Atkinson, R. K. (2003). Structuring the transition from example study to problem solving in cognitive skill acquisition. _Educational Psychologist_.
- Roediger, H. L., & Karpicke, J. D. (2006). Test-enhanced learning: Taking memory tests improves long-term retention. _Psychological Science_.
- Rohrer, D., & Taylor, K. (2007). The shuffling of mathematics problems improves learning. _Instructional Science_.
- Sentance, S., Waite, J., & Kallia, M. (2019). Teaching computer programming with PRIMM: A sociocultural perspective. _Computer Science Education_.
- Skycak, J. Individualized spaced repetition in hierarchical knowledge structures. justinmath.com.
- Sweller, J. (1988). Cognitive load during problem solving: Effects on learning. _Cognitive Science_.
- van Gog, T., Kester, L., & Paas, F. (2011). Effects of worked examples, example-problem, and problem-example pairs on novices' learning. _Contemporary Educational Psychology_.
- van Merriënboer, J. J. G., & Kirschner, P. A. _Ten Steps to Complex Learning_. Routledge.
- Ye, J., Su, J., & Cao, Y. (2022). A stochastic shortest path algorithm for optimizing spaced repetition scheduling. _KDD_.
