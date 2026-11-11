from checks import run


def test_the_walkthrough():
    """Prints the split, five epochs of history, the curve, three learning rates, two batch sizes and Adam."""
    assert run() == 'rows: 240 to train on, 60 held out | classes in the validation set: [22, 20, 18]\nepoch  1 | train loss 0.446 ######### | val loss 0.480 | val accuracy 0.78\nepoch  5 | train loss 0.323 ###### | val loss 0.346 | val accuracy 0.83\nepoch 10 | train loss 0.254 ##### | val loss 0.281 | val accuracy 0.87\nepoch 20 | train loss 0.187 #### | val loss 0.221 | val accuracy 0.90\nepoch 30 | train loss 0.151 ### | val loss 0.186 | val accuracy 0.92\nthe curve is converging | steps taken: 240\nlearning rate 5e-05: the training loss goes from 0.705 to 0.663: stalled\nlearning rate 0.05: the training loss goes from 0.446 to 0.151: converging\nlearning rate 30.0: the training loss goes from over a thousand to nan: diverging\nbatch size 8: 900 steps in 30 epochs, final validation accuracy 0.97\nbatch size 240: 30 steps in 30 epochs, final validation accuracy 0.83\nAdam at 0.01, batch 32: final train loss 0.044, validation accuracy 0.97\n'
