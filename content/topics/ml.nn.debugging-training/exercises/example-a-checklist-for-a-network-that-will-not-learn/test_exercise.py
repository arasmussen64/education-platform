from checks import run


def test_the_walkthrough():
    """Prints the eight checks."""
    assert run() == '1. loss at the start: 1.10 with a small output layer (guessing one of three: log 3 = 1.10) | 1.38 with the default scale\n2. overfit one batch of 8 rows: loss 1.11 -> 0.02 in 500 steps: passes\n3. gradient check: passes\n4. learning rate | 0.0001: 1.10 -> 1.03, stalled | 0.05: 1.10 -> 0.17, converging | 30: 1.10 -> nan, diverging\n5. dead ReLUs | hidden bias -20: 16 of 16 dead, loss 1.10 -> 1.10, stalled | after a run at rate 10: 12 of 16 dead, stalled | the healthy run at 0.05: 0 of 16 dead, converging, validation accuracy 0.90\n6. exploding gradients, six layers | scale 1.0, rate 0.05: gradient norm about 10^3 at step 1, overflowed by step 6: diverging | He scale, rate 0.05: converging, 0.93 | He scale, rate 1.0: diverging | He scale, rate 1.0, gradients clipped to 1: converging, 0.98\n7. data | labels shuffled: one batch of 8 still overfits (0.02), but 30 epochs go 1.10 -> 1.09 and validation accuracy is 0.35: stalled | inputs times 1000: diverging | standardized: converging, 0.93\n8. one word each, from diagnose: learning, stalled, diverging, stalled\n'
