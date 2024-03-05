import numpy as np
import scipy.io
from scipy.linalg import lstsq
import sounddevice as sd
from PIL import Image
from load_data import loading_data

address = 'pr6//data//'
compressedSignal, D, compressionMatrix = loading_data(address)
fps = 7350  
sd.play(compressedSignal, fps)
sd.wait()  

# least squares solution
def least_squares(A, y):
    """Compute the least squares solution to a linear matrix equation."""
    x, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
    return x
x = least_squares(compressionMatrix, compressedSignal)
sd.play(x,fps)
sd.wait()  

def omp(A, y, sparsity):
    """Orthogonal Matching Pursuit algorithm to recover sparse signals."""
    x_rec = np.zeros(A.shape[1])
    idx = []
    residual = y

    while len(idx) < sparsity:
        correlations = A.T @ residual
        i = np.argmax(np.abs(correlations))
        idx.append(i)
        A_selected = A[:, idx]
        x_est = np.linalg.lstsq(A_selected, y, rcond=None)[0]
        residual = y - A_selected @ x_est

    x_rec[idx] = x_est.flatten()
    return x_rec

K = [10, 50, 100, 200, 300, 1000, 2000, 3000]  
for k in K:
    yk = compressedSignal[:k]
    Ak = compressionMatrix[:k, :]
    ADk = Ak @ D
    sk = omp(ADk, yk, 100) 
    xk = D @ sk
    sd.play(xk, fps)
    sd.wait()  
