import numpy as np

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

PLANE = np.array(
    [[1.0, 2.0, 3.0], [2.0, 1.0, 3.0], [3.0, 5.0, 8.0], [4.0, 3.0, 7.0], [5.0, 6.0, 11.0], [6.0, 4.0, 10.0]]
)
SIX = np.array([[2.0, 1.0], [3.0, 2.0], [4.0, 2.0], [5.0, 4.0], [6.0, 4.0], [7.0, 5.0]])


def test_the_output():
    """Prints the explained shares and the reconstruction error."""
    assert run() == "[0.984 0.016]\n0.695\n"


def test_data_in_a_plane():
    """Three features that lie in a plane: two components rebuild them exactly, and the third share is zero."""
    pca = function("pca")
    reconstruct = function("reconstruct")
    scores, components, explained = pca(PLANE, 2)
    assert scores.shape == (6, 2) and components.shape == (3, 2)
    assert np.allclose(reconstruct(scores, components, PLANE.mean(axis=0)), PLANE)
    assert np.allclose(np.round(explained, 4), [0.9355, 0.0645, 0.0])
    assert np.allclose(components.T @ components, np.eye(2))


def test_all_components_rebuild_exactly():
    """With every component kept, 2-D data comes back exactly, and the components have positive first entries."""
    pca = function("pca")
    reconstruct = function("reconstruct")
    scores, components, explained = pca(SIX, 2)
    assert np.allclose(reconstruct(scores, components, SIX.mean(axis=0)), SIX)
    assert (components[0] > 0).all()
    assert np.allclose(components[:, 0], [0.772, 0.635], atol=1e-3)
