import numpy as np
import os

OUTPUT_DIR = "test_data/simulated"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_random_uint8(shape, entropy_level='high'):
    if entropy_level == 'high':
        return np.random.randint(0, 256, size=shape, dtype=np.uint8)
    elif entropy_level == 'low':
        # Create a gradient or simple pattern
        xv, yv = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
        data = (xv + yv) % 256
        return data.astype(np.uint8)
    elif entropy_level == 'medium':
        # Some structure + noise
        xv, yv = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
        data = (np.sin(xv/10.0) * np.cos(yv/10.0) * 127 + 128).astype(np.uint8)
        noise = np.random.randint(0, 20, size=shape, dtype=np.uint8)
        return np.clip(data + noise, 0, 255).astype(np.uint8)

def generate_simulated_microscopy(shape=(512, 512), n_frames=10, background=100, peak_intensity=1000, n_peaks=50):
    """
    Generate a stack of images simulating microscopy data with Poisson noise.
    """
    stack = []
    for _ in range(n_frames):
        # Base background
        img = np.full(shape, background, dtype=np.float32)
        
        # Add random peaks
        for _ in range(n_peaks):
            x = np.random.randint(0, shape[1])
            y = np.random.randint(0, shape[0])
            # Simple Gaussian-like spot (3x3 for simplicity)
            img[max(0, y-1):min(shape[0], y+2), max(0, x-1):min(shape[1], x+2)] += peak_intensity
            
        # Add Poisson noise
        noisy_img = np.random.poisson(img)
        
        # Clip to uint16 range
        noisy_img = np.clip(noisy_img, 0, 65535).astype(np.uint16)
        stack.append(noisy_img)
        
    return np.array(stack)

if __name__ == "__main__":
    ensure_dir(OUTPUT_DIR)
    
    print("Generating simulated data...")
    
    # 1. uint8 random data
    print("Generating uint8 data...")
    size_2d = (2048, 2048)
    np.save(f"{OUTPUT_DIR}/uint8_high_entropy.npy", generate_random_uint8(size_2d, 'high'))
    np.save(f"{OUTPUT_DIR}/uint8_medium_entropy.npy", generate_random_uint8(size_2d, 'medium'))
    np.save(f"{OUTPUT_DIR}/uint8_low_entropy.npy", generate_random_uint8(size_2d, 'low'))
    
    # 2. Simulated microscopy stack
    print("Generating microscopy stack (uint16)...")
    stack = generate_simulated_microscopy(shape=(256, 256), n_frames=2000)
    np.save(f"{OUTPUT_DIR}/microscopy_stack.npy", stack)
    
    print(f"Data generated in {OUTPUT_DIR}")
