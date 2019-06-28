from __future__ import absolute_import

import pytest

from tempfile import NamedTemporaryFile
from os import getenv

import numpy as np

from navec import Navec
from navec.pq import PQ
from navec.vocab import Vocab


CI = getenv('CI')


@pytest.fixture
def emb():
    pq = PQ(
        vectors=3,
        dim=6,
        subdim=2,
        # 1 0 0 | 1 0 0
        # 0 1 1 | 0 0 0
        # 0 0 0 | 0 1 0
        centroids=3,
        indexes=np.array([  # vectors x subdim
            [0, 1],
            [1, 0],
            [2, 2]
        ]).astype(np.uint8),
        codes=np.array([  # subdim x centroids x chunk
            [[1, 0, 0], [0, 1, 1], [0, 0, 0]],
            [[0, 0, 0], [1, 0, 0], [0, 1, 0]],
        ]).astype(np.float32),
    )
    vocab = Vocab(['a', 'b', 'c'])
    return Navec(vocab, pq)


def test_dump_load(emb):
    with NamedTemporaryFile() as file:
        path = file.name
        emb.dump(path)
        Navec.load(path)


def test_get(emb):
    assert np.array_equal(
        emb.get('a'),
        np.array([1., 0., 0., 1., 0., 0.])
    )
    assert emb.get('d') is None


def test_sim(emb):
    assert emb.sim('a', 'b') == 0.


@pytest.mark.skipif(CI, reason='gensim + scipy are heavy')
def test_gensim(emb):
    model = emb.as_gensim
    assert model.most_similar('a') == [
        ('b', 0.),
        ('c', 0.)
    ]


@pytest.mark.skipif(CI, reason='No torch for pypy, torch package is heavy')
def test_torch(emb):
    import torch

    model = emb.as_torch
    input = torch.tensor([[0, 1]]).long()
    assert torch.all(torch.eq(
        model(input),
        torch.tensor([[
            [1., 0., 0., 1., 0., 0.],
            [0., 1., 1., 0., 0., 0.]
        ]])
    ))