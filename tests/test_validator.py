import numpy as np
from rsc_t.index import rsc_t_index
from rsc_t.temporal import directional_coherence

def test_index_mean():
    assert np.isclose(rsc_t_index(0.8, 0.6), 0.7)

def test_directional_coherence():
    tracks = [
        np.array([[0,0],[1,0],[2,0]]),
        np.array([[0,1],[1,1],[2,1]]),
    ]
    assert directional_coherence(tracks) > 0.99
