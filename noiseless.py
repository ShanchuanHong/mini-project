import numpy as np
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
import time
import logging

os.makedirs('logs', exist_ok=True)
logging.basicConfig(filename='logs/noiseless.log', level=logging.INFO, filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Ensure the img directory exists
img_folder = 'img'
os.makedirs(img_folder, exist_ok=True)

def generate_matrix_A(M, N, mu_A, sigma_A):
    A = mu_A + sigma_A * np.random.randn(M, N)
    A /= np.linalg.norm(A, axis=0, keepdims=True)
    return A

def generate_sparse_x(N, support_length):
    support_A = np.random.choice(N, support_length, replace=False)
    sp1_length = np.random.randint(1, len(support_A) + 1)
    sp_values = np.concatenate([-10 + 9 * np.random.rand(sp1_length), 
                                 1 + 9 * np.random.rand(len(support_A) - sp1_length)])
    x = np.zeros(N)
    x[support_A] = np.random.permutation(sp_values)
    return x

def omp_algorithm(A, y, N, residue_limit):
    x_rec = np.zeros(N)
    A_new = np.empty((A.shape[0], 0))
    r = y.copy()
    max_index_array = []

    while np.max(np.abs(r)) > residue_limit and A_new.shape[1] <= N:
        w = A.T @ r
        new_sp_idx = np.argmax(np.abs(w))
        max_index_array.append(new_sp_idx)
        A_new = np.c_[A_new, A[:, new_sp_idx]]
        l_p = np.linalg.pinv(A_new) @ y
        r = y - A_new @ l_p

    x_rec[max_index_array] = l_p
    return x_rec

def plot_results(data, title, xlabel, ylabel, fig_num):
    plt.figure(fig_num)
    plt.imshow(data, extent=[1, data.shape[1], 1, data.shape[0]], aspect='auto', origin='lower', cmap='gray')
    plt.colorbar()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(f'{img_folder}/{title.replace(" ", "_").replace(",", "").replace("-", "_")}.png')
    plt.close()

# Main experimental setup
n_iter = 2000
N_set = [20, 50, 100]
mu_A = 0
sigma_A = 1
residue_limit = 1e-6
success_limit = 0.001

logging.info(f"Starting noiseless case with {n_iter} iterations for each N in {N_set}")

for num_fig, N in enumerate(N_set, 1):
    M_lim = int(np.ceil(0.75 * N))
    smax = int(np.floor(N / 4))
    norm_error_noiseless = np.zeros((M_lim, smax))
    esr_noiseless = np.zeros((M_lim, smax))
    start_time = time.time()
    for M in range(1, M_lim + 1):
        for support_length in range(1, smax + 1):
            for _ in range(n_iter):
                A = generate_matrix_A(M, N, mu_A, sigma_A)
                x = generate_sparse_x(N, support_length)
                y = A @ x
                x_rec = omp_algorithm(A, y, N, residue_limit)
                
                error = np.linalg.norm(x - x_rec) / np.linalg.norm(x)
                norm_error_noiseless[M-1, support_length-1] += error / n_iter
                if error <= success_limit:
                    esr_noiseless[M-1, support_length-1] += 1 / n_iter
    end_time = time.time()
    logging.info(f'Elapsed time for N={N}: {end_time - start_time}')

    plot_results(esr_noiseless, f'Probability of ESR - Noiseless case - N={N}', 'Sparsity', 'M rows', 2 * num_fig - 1)
    plot_results(norm_error_noiseless, f'Average Normalized Error - Noiseless case - N={N}', 'Sparsity', 'M rows', 2 * num_fig)
