import numpy as np
from scipy.io import loadmat
from scipy.linalg import pinv
import matplotlib.pyplot as plt
import logging

# Set the logging level
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def omp_algorithm(A, y, residue_limit):
    N = A.shape[1]
    x_rec = np.zeros((N, 1))
    A_new = np.empty((A.shape[0], 0))
    r = y.copy()
    max_index_array = set()
    for _ in range(N):
        w = A.T @ r
        new_sp_idx = np.argmax(np.abs(w))
        max_index_array.add(new_sp_idx)
        max_index_array_list = list(max_index_array)
        A_new = np.linalg.lstsq(A[:, max_index_array_list], y, rcond=None)[0]
        x_rec[max_index_array_list] = A_new
        r = y - A @ x_rec
        if np.linalg.norm(r) < residue_limit:
            break
    
    return x_rec

# Load the MAT file
data = loadmat('Pr5\\Data\\Data.mat')  
A1, A2, A3 = data['A1'], data['A2'], data['A3']
Y1, Y2, Y3 = data['y1'], data['y2'], data['y3']


tolerance = 1e-6
new_shape = (160, 90)

# Recover X from Y1, Y2, Y3 using OMP
logging.info('Recovering X from Y1, Y2, Y3 using OMP')
X1_rec = omp_algorithm(A1, Y1, tolerance).reshape(new_shape).T
X2_rec = omp_algorithm(A2, Y2, tolerance).reshape(new_shape).T
X3_rec = omp_algorithm(A3, Y3, tolerance).reshape(new_shape).T
logging.info('Recovery complete')

# Least Squares Solution
def least_squares(A, y):
    """Compute the least squares solution to a linear matrix equation."""
    x, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
    return x
logging.info('Recovering X from Y1, Y2, Y3 using Least Squares')
X1_rec_ls = least_squares(A1,Y1).reshape(new_shape).T  
X2_rec_ls = least_squares(A2,Y2).reshape(new_shape).T
X3_rec_ls = least_squares(A3,Y3).reshape(new_shape).T
logging.info('Recovery complete')



# Directory paths for saving images
ls_dir = 'img//part5//ls//'  
omp_dir = 'img//part5//omp//'  

# Save the recovered images from Least Squares
plt.figure()
plt.imshow(X1_rec_ls, cmap='gray')
plt.title('Recovered Image from Y1 using Least Squares')
plt.savefig(ls_dir + 'X1_rec_ls.png')
plt.close()

plt.figure()
plt.imshow(X2_rec_ls, cmap='gray')
plt.title('Recovered Image from Y2 using Least Squares')
plt.savefig(ls_dir + 'X2_rec_ls.png')
plt.close()

plt.figure()
plt.imshow(X3_rec_ls, cmap='gray')
plt.title('Recovered Image from Y3 using Least Squares')
plt.savefig(ls_dir + 'X3_rec_ls.png')
plt.close()

# Save the recovered images using OMP
plt.figure()
plt.imshow(X1_rec, cmap='gray')
plt.title('Recovered Image from Y1')
plt.savefig(omp_dir + 'X1_rec_omp.png')
plt.close()

plt.figure()
plt.imshow(X2_rec, cmap='gray')
plt.title('Recovered Image from Y2')
plt.savefig(omp_dir + 'X2_rec_omp.png')
plt.close()

plt.figure()
plt.imshow(X3_rec, cmap='gray')
plt.title('Recovered Image from Y3')
plt.savefig(omp_dir + 'X3_rec_omp.png')
plt.close()

logging.info('Images saved successfully')