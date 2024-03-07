import numpy as np
import matplotlib.pyplot as plt
import os
import logging
import time

os.makedirs('logs', exist_ok=True)
logging.basicConfig(filename='logs/noise.log', level=logging.INFO, filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def generate_matrix_A(M, N, mu_A, sigma_A):
    """Generate the measurement matrix A with normalized columns."""
    A = mu_A + sigma_A * np.random.randn(M, N)
    A /= np.linalg.norm(A, axis=0, keepdims=True)
    return A

def generate_sparse_x(N, support_length):
    """Generate a sparse vector x with given support length."""
    support_indices = np.random.choice(N, support_length, replace=False)
    sp1_length = np.random.randint(1, len(support_indices) + 1)
    sp_values = np.concatenate([
        -10 + 9 * np.random.rand(sp1_length),
        1 + 9 * np.random.rand(len(support_indices) - sp1_length)
    ])
    x = np.zeros(N)
    x[support_indices] = np.random.permutation(sp_values)
    return x

def generate_noise(M, n_sigma):
    """Generate noise vector n."""
    return n_sigma * np.random.randn(M, 1)

def omp_with_known_sparsity(A, y, x, noisy_residue_limit, max_iterations):
    """OMP algorithm for the sparsity known case."""
    N = len(x)
    x_rec = np.zeros(N)
    A_new = np.empty((A.shape[0], 0))
    residual = y.copy()
    selected_indices = []

    while np.max(np.abs(residual)) > noisy_residue_limit and len(selected_indices) < np.count_nonzero(x) and len(selected_indices) <= max_iterations:
        proj = A.T @ residual
        new_idx = np.argmax(np.abs(proj))
        selected_indices.append(new_idx)
        A_new = np.c_[A_new, A[:, new_idx]]
        x_est = np.linalg.pinv(A_new) @ y
        residual = y - A_new @ x_est

    x_rec[selected_indices] = x_est.flatten()
    return np.linalg.norm(x - x_rec) / np.linalg.norm(x)

def omp_with_unknown_sparsity(A, y, n_norm, max_iterations):
    """OMP algorithm for the sparsity unknown case."""
    N = A.shape[1]
    x_rec = np.zeros(N)
    A_new = np.empty((A.shape[0], 0))
    residual = y.copy()
    selected_indices = []
    x_est = np.zeros((0, 1))  # Initialize x_est to ensure it has a value

    while np.max(np.abs(residual)) > n_norm and len(selected_indices) < max_iterations:
        proj = A.T @ residual
        new_idx = np.argmax(np.abs(proj))
        selected_indices.append(new_idx)
        A_new = np.c_[A_new, A[:, new_idx]]
        if A_new.shape[1] > 0:  # Ensure A_new is not empty
            x_est = np.linalg.pinv(A_new) @ y
            residual = y - A_new @ x_est

    if len(selected_indices) > 0:  # Check to prevent index error if selected_indices is empty
        x_rec[selected_indices] = x_est.flatten()
    return np.linalg.norm(y - A_new @ x_est) / np.linalg.norm(y) if A_new.size else 0


# Set up directories
img_folder = 'img//noise'
os.makedirs(img_folder, exist_ok=True)

# Set up Seed
np.random.seed(7)

# Main experimental setup
n_iter = 20
N_set = [20, 50, 100]
mu_A = 0
sigma_A = 1
residue_limit = 1e-6
noisy_residue_limit = residue_limit * 100
success_limit = 0.001
n_sigma_set = [1e-3, 0.1]
sparsity_flag_set = [0, 1]  # 0 for known sparsity, 1 for unknown sparsity
sparsity_flag_map = {0: 'Known', 1: 'Unknown'}

for sparsity_flag in sparsity_flag_set:
    os.makedirs(f'{img_folder}/{sparsity_flag_map[sparsity_flag]}', exist_ok=True)

logging.info(f"Starting noisy case with {n_iter} iterations for each N in {N_set}")

for n_sigma in n_sigma_set:
    for N in N_set:
        M_lim = int(np.ceil(0.75 * N))
        smax = int(np.floor(N / 2))
        
        for sparsity_flag in sparsity_flag_set:

            start_time = time.time()

            norm_error_noisy = np.zeros((M_lim, smax))
            esr_noisy = np.zeros((M_lim, smax))

            for M in range(1, M_lim + 1):
                for support_length in range(1, smax + 1):
                    for _ in range(n_iter):
                        A = generate_matrix_A(M, N, mu_A, sigma_A)
                        x = generate_sparse_x(N, support_length)
                        n = generate_noise(M, n_sigma)
                        y = A @ x[:, np.newaxis] + n

                        if sparsity_flag == 0:  # Sparsity known
                            error = omp_with_known_sparsity(A, y, x, noisy_residue_limit, 100)
                        else:  # Sparsity unknown
                            n_norm = np.linalg.norm(n)
                            error = omp_with_unknown_sparsity(A, y, n_norm, 100)

                        norm_error_noisy[M-1, support_length-1] += error / n_iter
                        esr_noisy[M-1, support_length-1] += (error <= success_limit) / n_iter

            # Plotting and saving results
            for data, title in zip([esr_noisy, norm_error_noisy], ['ESR', 'Average Normalized Error']):
                plt.figure()
                plt.imshow(data, extent=[1, smax, 1, M_lim], aspect='auto', origin='lower', cmap='gray')
                plt.colorbar()
                plt.title(f'{title} - Noisy case - N={N} - Sigma={n_sigma} - Sparsity flag={sparsity_flag_map[sparsity_flag]}')
                plt.xlabel('Sparsity Level')
                plt.ylabel('M (Measurements)')
                plt.savefig(f'{img_folder}/{sparsity_flag_map[sparsity_flag]}/{title.replace(" ", "_")}_N={N}_Sigma={n_sigma}_Flag={sparsity_flag_map[sparsity_flag]}.png')
                plt.close()
            
            end_time = time.time()
            logging.info(f'Elapsed time for N={N}, Sigma={n_sigma}, Sparsity flag={sparsity_flag_map[sparsity_flag]}: {end_time - start_time}')
