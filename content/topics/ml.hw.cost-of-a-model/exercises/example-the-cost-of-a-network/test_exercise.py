from checks import run


def test_the_walkthrough():
    """Prints the parameters, the three FLOP counts, the three byte counts and the two time estimates."""
    assert run() == 'layers [784, 256, 128, 10]: 235,146 parameters; a forward pass is 469,504 FLOPs per example, 2.00 per parameter\nthe backward pass is about twice that, 939,008 (a gradient for the inputs and one for the weights), so a training step is 1,408,512 per example, about 6 per parameter\na batch of 64: 90,144,768 FLOPs\nweights in float32: 940,584 bytes | in float16: 470,292\nactivations kept for the backward pass: 1,178 values per example; a batch of 64 is 301,568 bytes in float32, 150,784 in float16\ntraining state with Adam in float32 (weights, gradients, two moments): 16 bytes per parameter, 3,762,336 bytes | mixed precision (float16 weights and gradients, float32 master weights and moments): 16 bytes per parameter\none epoch of 60,000 examples: 8.47e+10 FLOPs, 8.5 ms on a 10 TFLOP/s GPU at full speed, 28 ms at a realistic 30 percent\na 7 billion parameter model on a trillion tokens: 4.2e+22 FLOPs, 133 years on that GPU, 122 days on 1,000 of them at 40 percent\n'
