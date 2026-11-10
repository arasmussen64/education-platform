from checks import run


def test_the_walkthrough():
    """Prints the edge, the shapes, the counts, the checks, the pooling and the bars."""
    assert run() == 'row 0 of the image: [0.0, 0.0, 0.0, 1.0, 1.0, 1.0]\nvertical-edge kernel, row 0 of the output: [0.0, 3.0, 3.0, 0.0]\nhorizontal-edge kernel, row 0 of the output: [0.0, 0.0, 0.0, 0.0]\nvalid: (4, 4) | padded by 1: (6, 6) | stride 2: (2, 2)\na dense layer from a 28x28 image to a 28x28 output: 615,440 parameters | eight 3x3 kernels: 80 | ratio 7,693\nConv2D output shape: (5, 4, 6, 6) | kernel 1 on image 2 matches correlate2d: True\na bar two rows lower gives the feature map two rows lower: True\ngradient check of the parameters: passes | of the input: passes\nmax pooling a 4x4: [[4.0, 8.0], [12.0, 16.0]]\nwhere a gradient of 1 per pooled cell goes back: [[0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 1.0], [0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 1.0]]\nbars: training loss 0.89 -> 0.03 after 300 steps | held-out accuracy 0.96 | 114 parameters\n'
