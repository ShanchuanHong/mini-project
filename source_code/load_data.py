import numpy as np
import scipy.io
from scipy.linalg import lstsq
import sounddevice as sd
from PIL import Image

Image.MAX_IMAGE_PIXELS = None 

def loading_data(address):
    # Load compressed signal from .mat file
    compressedSignal = scipy.io.loadmat(f'{address}compressedSignal.mat')['compressedSignal']
    compressedSignal = compressedSignal.astype(np.float64)
    
    # Load compression matrix from .mat file
    compressionMatrix = scipy.io.loadmat(f'{address}compressionMatrix.mat')['compressionMatrix']
    
    # Load and process D_compressed from .tiff file
    D_compressed = Image.open(f'{address}CompressedBasis.tiff')
    D_compressed = np.array(D_compressed).astype(np.float64)
    D = D_compressed / 255.0 * 0.1284 - 0.0525
    
    return compressedSignal, D, compressionMatrix

if __name__ == "__main__":
    address = 'pr6//data//'
    compressedSignal, D, compressionMatrix = loading_data(address)
    print(compressedSignal.shape, D.shape, compressionMatrix.shape)
    sd.play(compressedSignal, 7350)
    sd.wait()
    