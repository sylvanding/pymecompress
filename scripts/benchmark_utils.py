import numpy as np
import time
import os
import contextlib
import scipy.io

@contextlib.contextmanager
def Timer(name="Task"):
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    print(f"[{name}] Executed in {end - start:.4f} seconds")

class TimerObj:
    def __init__(self):
        self.start = 0
        self.end = 0
        self.interval = 0

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.end = time.perf_counter()
        self.interval = self.end - self.start

def load_mat_data(filepath: str, variable_name: str = None) -> np.ndarray:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    mat = scipy.io.loadmat(filepath)
    
    if variable_name:
        if variable_name not in mat:
            raise KeyError(f"Variable {variable_name} not found in {filepath}")
        return mat[variable_name]
    
    # Auto-detect the largest variable (usually the image data)
    # Filter out internal variables starting with '__'
    vars_info = []
    for key, value in mat.items():
        if key.startswith('__'):
            continue
        if isinstance(value, np.ndarray):
            vars_info.append((key, value.nbytes, value))
            
    if not vars_info:
        raise ValueError(f"No valid numpy arrays found in {filepath}")
        
    # Sort by size descending
    vars_info.sort(key=lambda x: x[1], reverse=True)
    best_var_name, size, data = vars_info[0]
    print(f"Loaded variable '{best_var_name}' ({size/1024/1024:.2f} MB) from {filepath}")
    return data

def calculate_metrics(original: np.ndarray, decompressed: np.ndarray) -> dict:
    if original.shape != decompressed.shape:
        raise ValueError(f"Shape mismatch: {original.shape} vs {decompressed.shape}")
        
    original = original.astype(np.float64)
    decompressed = decompressed.astype(np.float64)
    
    diff = original - decompressed
    mse = np.mean(diff ** 2)
    rmse = np.sqrt(mse)
    max_err = np.max(np.abs(diff))
    
    # PSNR calculation
    # Assuming dynamic range based on data type max value or actual max?
    # Usually for uint16 it is 65535, or max of signal. Let's use max of signal for better range estimation or standard type max.
    # Standard PSNR uses type max.
    data_range = 65535.0 # Assuming uint16 for quantization tests usually
    if original.max() <= 255:
        data_range = 255.0
        
    if mse == 0:
        psnr = float('inf')
    else:
        psnr = 20 * np.log10(data_range / rmse)
        
    return {
        'rmse': rmse,
        'psnr': psnr,
        'max_error': max_err,
        'mse': mse
    }

def verify_quantization_error(original, decompressed, scale, offset=0):
    """
    Verify if error is consistent with quantization noise.
    Quantization noise variance is roughly (scale^2)/12 + Poisson noise considerations.
    This is a complex check, for now we might just return the error stats.
    """
    # Placeholder for more complex verification if needed
    pass
