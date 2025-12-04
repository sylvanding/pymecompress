import numpy as np
import os
import csv
import pymecompress
from pymecompress import codecs
from benchmark_utils import TimerObj

# Ensure simulated data exists
SIM_DATA_DIR = "test_data/simulated"
RESULTS_FILE = "scripts/results_lossless.csv"

def run_tests():
    files = [f for f in os.listdir(SIM_DATA_DIR) if f.startswith("uint8_") and f.endswith(".npy")]
    if not files:
        print("No test data found. Please run scripts/01_gen_sim_data.py first.")
        return

    results = []
    
    for fname in files:
        fpath = os.path.join(SIM_DATA_DIR, fname)
        data = np.load(fpath)
        name = fname.replace(".npy", "")
        
        print(f"Testing {name} (Shape: {data.shape}, Size: {data.nbytes/1024/1024:.2f} MB)...")
        
        # Method 1: pymecompress.HuffmanCompress (Direct)
        with TimerObj() as t_comp:
            compressed = pymecompress.HuffmanCompress(data)
        comp_time = t_comp.interval
        
        comp_size = compressed.nbytes
        orig_size = data.nbytes
        ratio = orig_size / comp_size if comp_size > 0 else 0
        
        with TimerObj() as t_decomp:
            decompressed = pymecompress.HuffmanDecompress(compressed, orig_size)
        decomp_time = t_decomp.interval
        
        # Verify correctness
        assert np.array_equal(data, decompressed), "Decompression failed verification!"
        
        results.append({
            "dataset": name,
            "method": "Direct_API",
            "orig_mb": orig_size / 1024**2,
            "comp_mb": comp_size / 1024**2,
            "ratio": ratio,
            "comp_speed_mb_s": (orig_size / 1024**2) / comp_time,
            "decomp_speed_mb_s": (orig_size / 1024**2) / decomp_time
        })
        
        # Method 2: codecs.Huffman (Numcodecs)
        huff = codecs.Huffman()
        with TimerObj() as t_comp_c:
            compressed_c = huff.encode(data)
        comp_time_c = t_comp_c.interval
        
        with TimerObj() as t_decomp_c:
            decompressed_c = huff.decode(compressed_c, out=np.empty_like(data))
        decomp_time_c = t_decomp_c.interval
        
        assert np.array_equal(data, decompressed_c), "Codecs Decompression failed verification!"
        
        results.append({
            "dataset": name,
            "method": "Codecs_API",
            "orig_mb": orig_size / 1024**2,
            "comp_mb": len(compressed_c) / 1024**2,
            "ratio": orig_size / len(compressed_c),
            "comp_speed_mb_s": (orig_size / 1024**2) / comp_time_c,
            "decomp_speed_mb_s": (orig_size / 1024**2) / decomp_time_c
        })

    # Save results
    with open(RESULTS_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["dataset", "method", "orig_mb", "comp_mb", "ratio", "comp_speed_mb_s", "decomp_speed_mb_s"])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Results saved to {RESULTS_FILE}")

if __name__ == "__main__":
    run_tests()
