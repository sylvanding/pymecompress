import os
import scipy.io
import numpy as np

def analyze_mat_file(file_path):
    """
    分析 .mat 文件的数据结构、类型和统计信息。
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    print(f"Analyzing file: {file_path}")
    print("-" * 50)

    try:
        mat_data = scipy.io.loadmat(file_path)
    except Exception as e:
        print(f"Error loading .mat file: {e}")
        return

    # 过滤掉系统自带的 key
    keys = [k for k in mat_data.keys() if not k.startswith('__')]
    print(f"Found variables: {keys}")
    print("-" * 50)

    for key in keys:
        data = mat_data[key]
        print(f"Variable: {key}")
        
        if isinstance(data, np.ndarray):
            print(f"  Type: {type(data)}")
            print(f"  Dtype: {data.dtype}")
            print(f"  Shape: {data.shape}")
            
            # 如果是数值类型，计算统计信息
            if np.issubdtype(data.dtype, np.number):
                print(f"  Min: {np.min(data)}")
                print(f"  Max: {np.max(data)}")
                print(f"  Mean: {np.mean(data):.4f}")
                print(f"  Std: {np.std(data):.4f}")
                
                unique_vals = np.unique(data)
                if len(unique_vals) < 20:
                    print(f"  Unique values: {unique_vals}")
                else:
                    print(f"  Unique values count: {len(unique_vals)}")
            else:
                print("  (Non-numeric data)")
        else:
            print(f"  Type: {type(data)} (Not a numpy array)")
        
        print("-" * 30)

if __name__ == "__main__":
    # 获取当前脚本所在目录的上一级目录的上一级目录 (项目根目录)
    # scripts/real_data_handler/real_data_analysis.py -> scripts/real_data_handler -> scripts -> root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    data_path = os.path.join(project_root, 'test_data', '13um_1_im_561_005_002.mat')
    
    analyze_mat_file(data_path)

