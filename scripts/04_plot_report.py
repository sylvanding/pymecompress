import matplotlib.pyplot as plt
import numpy as np
import csv
import os

LOSSLESS_CSV = "results/02/results_lossless.csv"
QUANT_CSV = "results/03/results_quantization.csv"
VIS_ORIG = "results/03/vis_original.npy"
VIS_DECOMP = "results/03/vis_decompressed.npy"

def read_csv(filepath):
    data = []
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return data
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            for k, v in row.items():
                try:
                    row[k] = float(v)
                except ValueError:
                    pass
            data.append(row)
    return data

def plot_lossless_performance(data):
    if not data: return
    
    datasets = sorted(list(set(d['dataset'] for d in data)))
    
    # Filter for ratio plot (Direct_API usually same as Codecs_API for ratio, pick one)
    ratios = {}
    for ds in datasets:
        for d in data:
            if d['dataset'] == ds and d['method'] == 'Direct_API':
                ratios[ds] = d['ratio']
                break
    
    if not ratios: return

    plt.figure(figsize=(10, 6))
    plt.bar(list(ratios.keys()), list(ratios.values()))
    plt.title("Lossless Compression Ratio by Dataset")
    plt.ylabel("Compression Ratio")
    plt.savefig("results/04/performance_lossless_ratio.png")
    plt.close()
    
    # Speed comparison
    # Group by dataset
    labels = datasets
    comp_speeds = []
    decomp_speeds = []
    
    for ds in datasets:
        found = False
        for d in data:
            if d['dataset'] == ds and d['method'] == 'Direct_API':
                comp_speeds.append(d['comp_speed_mb_s'])
                decomp_speeds.append(d['decomp_speed_mb_s'])
                found = True
                break
        if not found:
            comp_speeds.append(0)
            decomp_speeds.append(0)
    
    x = np.arange(len(labels))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, comp_speeds, width, label='Compression')
    rects2 = ax.bar(x + width/2, decomp_speeds, width, label='Decompression')
    
    ax.set_ylabel('Speed (MB/s)')
    ax.set_title('Lossless Compression/Decompression Speed (Direct API)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    
    plt.savefig("results/04/performance_lossless_speed.png")
    plt.close()

def plot_quantization_tradeoff(data):
    if not data: return
    
    # Filter for Real_Microscopy if available, else Simulated
    target_dataset = "Real_Microscopy"
    subset = [d for d in data if d['dataset'] == target_dataset]
    if not subset:
        target_dataset = "Simulated_Stack"
        subset = [d for d in data if d['dataset'] == target_dataset]
    
    if not subset: return
    
    subset.sort(key=lambda x: x['scale'])
    scales = [d['scale'] for d in subset]
    ratios = [d['ratio'] for d in subset]
    rmses = [d['rmse'] for d in subset]
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    color = 'tab:blue'
    ax1.set_xlabel('Scale Parameter')
    ax1.set_ylabel('Compression Ratio', color=color)
    ax1.plot(scales, ratios, marker='o', color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('RMSE', color=color)
    ax2.plot(scales, rmses, marker='x', color=color, linestyle='--')
    ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title(f"Quantization Trade-off ({target_dataset})")
    plt.grid(True, alpha=0.3)
    plt.savefig("results/04/quantization_tradeoff.png")
    plt.close()

def plot_error_analysis():
    if not os.path.exists(VIS_ORIG) or not os.path.exists(VIS_DECOMP):
        print("Visualization data files not found.")
        return
        
    orig = np.load(VIS_ORIG).astype(float)
    decomp = np.load(VIS_DECOMP).astype(float)
    diff = orig - decomp
    
    plt.figure(figsize=(12, 10))
    
    # Original
    plt.subplot(2, 2, 1)
    plt.imshow(orig, cmap='gray')
    plt.title("Original Image")
    plt.colorbar()
    
    # Decompressed
    plt.subplot(2, 2, 2)
    plt.imshow(decomp, cmap='gray')
    plt.title("Decompressed (Scale=1.0)")
    plt.colorbar()
    
    # Difference
    plt.subplot(2, 2, 3)
    plt.imshow(diff, cmap='bwr') # Blue-White-Red diverging
    plt.title("Difference (Error)")
    plt.colorbar()
    
    # Histogram of errors
    plt.subplot(2, 2, 4)
    plt.hist(diff.ravel(), bins=50, log=True)
    plt.title("Error Distribution")
    plt.xlabel("Error Value")
    plt.ylabel("Count (Log)")
    
    plt.tight_layout()
    plt.savefig("results/04/error_analysis.png")
    plt.close()
    
    # Scatter plot: Signal vs Error
    plt.figure(figsize=(8, 6))
    # Downsample for scatter plot if too large
    flat_orig = orig.ravel()
    flat_diff = diff.ravel()
    if len(flat_orig) > 10000:
        indices = np.random.choice(len(flat_orig), 10000, replace=False)
        flat_orig = flat_orig[indices]
        flat_diff = flat_diff[indices]
        
    plt.scatter(flat_orig, flat_diff, alpha=0.1, s=1)
    plt.xlabel("Original Signal Intensity")
    plt.ylabel("Quantization Error")
    plt.title("Signal Dependent Error Analysis")
    plt.axhline(0, color='r', linestyle='--', linewidth=0.5)
    plt.savefig("results/04/signal_vs_error.png")
    plt.close()

if __name__ == "__main__":
    print("Generating plots...")
    lossless_data = read_csv(LOSSLESS_CSV)
    plot_lossless_performance(lossless_data)
    
    quant_data = read_csv(QUANT_CSV)
    plot_quantization_tradeoff(quant_data)
    
    plot_error_analysis()
    print("Plots generated in results/04/")
