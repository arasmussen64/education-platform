from checks import run


def test_the_walkthrough():
    """Prints the shapes, the passing checks, the softmax numbers and a falling loss."""
    assert run() == 'loss 0.9568 | gradient shapes: [(3, 4), (4,), (4, 2), (2,)] | gradient for the input: (5, 3)\nevery gradient matches its numeric check: True\ndW[0, 0] is the sum over the batch of input 0 times the gradient at output 0: True\na Dense layer does 1 matrix multiply forward and 2 backward: X.T @ grad_out -> (3, 4) and grad_out @ W.T -> (5, 3)\nsoftmax cross-entropy: 0.3143 | probabilities: [[0.659, 0.242, 0.099], [0.11, 0.809, 0.081]]\nits gradient is (p - onehot) / n: [[-0.17, 0.121, 0.049], [0.055, -0.095, 0.041]] | numeric check: True\nlogits of 1,000 stay finite: 0.3133\nstep 0 loss 0.957\nstep 30 loss 0.065\nstep 59 loss 0.04\n'
