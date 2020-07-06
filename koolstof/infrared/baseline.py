import numpy as np
from scipy import sparse


def als(y, lam, p, niter=10):
    """Baseline correction."""
    # https://stackoverflow.com/questions/29156532/python-baseline-correction-library
    L = len(y)
    D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L - 2))
    D = lam * D.dot(D.transpose())
    w = np.ones(L)
    W = sparse.spdiags(w, 0, L, L)
    for _ in range(niter):
        W.setdiag(w)
        Z = W + D
        z = sparse.linalg.spsolve(Z, w * y)
        w = p * (y > z) + (1.0 - p) * (y < z)
    return z
