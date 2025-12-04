import numpy as np
import os
import csv
import pymecompress
from pymecompress import codecs
from benchmark_utils import TimerObj, load_mat_data, calculate_metrics

RESULTS_FILE = "results/03/results_quantization.csv"
REAL_DATA_PATH = "test_data/13um_1_im_561_005_002.mat"
SIM_DATA_PATH = "test_data/simulated/microscopy_stack.npy"

def test_on_data(data, name, results_list):
    scales = [0.1, 0.5, 0.8, 1.0, 1.5, 2.0, 4.0]
    
    # Determine offset safely
    min_val = float(np.min(data))
    offset = min_val # Use min value as offset to ensure non-negative for sqrt
    
    print(f"Testing on {name} (Shape: {data.shape}, Type: {data.dtype}, Min: {min_val}, Offset: {offset})...")
    
    # Ensure data is C-contiguous
    if not data.flags['C_CONTIGUOUS']:
        # print(f"Warning: Converting {name} to C-contiguous array")
        data = np.ascontiguousarray(data)

    # Ensure data is uint16
    if data.dtype != np.uint16:
        print(f"Warning: Converting {name} from {data.dtype} to uint16")
        data = data.astype(np.uint16)
        
    orig_size = data.nbytes
    
    for scale in scales:
        print(f"  Testing scale={scale}...")
        
        # Use Codecs API for convenience
        codec = codecs.HuffmanQuant16(offset=offset, scale=scale)
        
        with TimerObj() as t_comp:
            compressed = codec.encode(data)
        comp_time = t_comp.interval
        
        comp_size = len(compressed)
        ratio = orig_size / comp_size if comp_size > 0 else 0
        
        with TimerObj() as t_decomp:
            decompressed = codec.decode(compressed).reshape(data.shape)
        decomp_time = t_decomp.interval
        
        metrics = calculate_metrics(data, decompressed)
        
        results_list.append({
            "dataset": name,
            "scale": scale,
            "offset": offset,
            "orig_mb": orig_size / 1024**2,
            "comp_mb": comp_size / 1024**2,
            "ratio": ratio,
            "rmse": metrics['rmse'],
            "psnr": metrics['psnr'],
            "max_error": metrics['max_error'],
            "comp_speed_mb_s": (orig_size / 1024**2) / comp_time,
            "decomp_speed_mb_s": (orig_size / 1024**2) / decomp_time
        })

def run_tests():
    results = []
    
    # 1. Simulated Data
    if os.path.exists(SIM_DATA_PATH):
        sim_data = np.load(SIM_DATA_PATH)
        test_on_data(sim_data, "Simulated_Stack", results)
    else:
        print(f"Simulated data not found at {SIM_DATA_PATH}. Run 01_gen_sim_data.py first.")
        
    # 2. Real Data
    if os.path.exists(REAL_DATA_PATH):
        try:
            real_data = load_mat_data(REAL_DATA_PATH)
            # Take a subset if too large to speed up testing? Or test full.
            # Real data might be 3D.
            test_on_data(real_data, "Real_Microscopy", results)
            
            # Save a slice for visualization (Original vs Decompressed at scale 1.0)
            # Re-run for scale=1.0 specifically to save images
            # Take middle frame
            if real_data.ndim == 3:
                # Heuristic: if last dim is significantly larger than others or simply large, assume (H, W, T)
                # In this case (256, 256, 2000), T is likely last.
                if real_data.shape[2] > real_data.shape[0] and real_data.shape[2] > real_data.shape[1]:
                    slice_idx = real_data.shape[2] // 2
                    slice_data = real_data[:, :, slice_idx]
                else:
                    slice_idx = real_data.shape[0] // 2
                    slice_data = real_data[slice_idx]
            else:
                slice_data = real_data
            
            if not slice_data.flags['C_CONTIGUOUS']:
                slice_data = np.ascontiguousarray(slice_data)
                
            # Update codec with correct offset for the slice (though we decode the whole thing below?)
            # Wait, line 86 encodes slice_data. We should use the SAME offset as determined in test_on_data?
            # test_on_data doesn't return the offset it used. 
            # We should re-calculate offset for this specific test or just use min(slice_data)
            slice_min = float(np.min(slice_data))
            codec = codecs.HuffmanQuant16(offset=slice_min, scale=1.0)
            
            comp_slice = codec.encode(slice_data)
            decomp_slice = codec.decode(comp_slice).reshape(slice_data.shape)
            
            np.save("results/03/vis_original.npy", slice_data)
            np.save("results/03/vis_decompressed.npy", decomp_slice)
            print("Saved visualization slices.")
            
        except Exception as e:
            print(f"Failed to process real data: {e}")
    else:
        print(f"Real data not found at {REAL_DATA_PATH}")

    # Save results
    fieldnames = ["dataset", "scale", "offset", "orig_mb", "comp_mb", "ratio", "rmse", "psnr", "max_error", "comp_speed_mb_s", "decomp_speed_mb_s"]
    with open(RESULTS_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Results saved to {RESULTS_FILE}")

if __name__ == "__main__":
    run_tests()
