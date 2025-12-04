# PYMECompress 测试方案与计划

## 1. 测试目标
本测试计划旨在全面评估 `pymecompress` 库的压缩性能、准确性及稳定性。测试将覆盖底层的 C/Cython 接口以及上层的 `numcodecs` 接口，重点关注无损压缩的效率和有损（量化）压缩在保留生物显微图像特征方面的表现。

## 2. 测试环境
- **操作系统**: Linux (WSL2)
- **Python环境**: Python 3.x
- **依赖库**: 
    - `numpy`: 数据处理
    - `scipy`: 读取 .mat 文件
    - `matplotlib`: 绘图
    - `pandas`: 结果统计与表格生成
    - `zarr` / `numcodecs`: 接口兼容性测试

## 3. 数据准备

### 3.1 模拟数据 (Simulated Data)
为了控制变量评估算法，将生成以下类型的模拟数据：
- **纯随机噪声**: 均匀分布的 `uint8` 和 `uint16` 数组。
- **模拟显微图像**: 
    - 背景 + 稀疏亮点（模拟荧光分子）。
    - 包含泊松噪声 (Poisson Noise)。
    - 尺寸: 512x512, 2048x2048。
    - 帧数: 单帧及多帧堆栈 (Stack)。

### 3.2 真实实验数据 (Real Experimental Data)
使用项目提供的真实显微镜成像数据：
- **文件路径**: `test_data/13um_1_im_561_005_002.mat`
- **数据类型**: 预计为 uint16 的 3D 图像堆栈。
- **用途**: 验证算法在实际应用场景下的压缩率和保真度。

## 4. 测试场景设计

### 4.1 场景一：无损压缩基准测试 (Lossless Benchmark)
**目标**: 评估 `HuffmanCompress` (uint8) 的性能极限。
**方法**:
1. 对不同熵值（Entropy）的模拟数据进行压缩。
2. 记录原始大小、压缩后大小、压缩时间、解压时间。
**输出**:
- 表格：不同数据集下的压缩比 (Compression Ratio, CR) 和吞吐量 (MB/s)。

### 4.2 场景二：量化压缩与误差分析 (Quantization & Error Analysis)
**目标**: 评估 `HuffmanCompressQuant` (uint16) 在不同参数下的表现。
**方法**:
1. 使用模拟泊松噪声图像和真实数据。
2. 调整量化参数 `scale` (如 0.5, 1.0, 2.0, 4.0)。
3. 计算压缩比、均方根误差 (RMSE)、峰值信噪比 (PSNR)。
4. **关键验证**: 验证解压后的数据与原始数据的差值是否在理论允许的噪声范围内（即量化引入的误差是否小于光子散粒噪声）。

### 4.3 场景三：Numcodecs 接口兼容性
**目标**: 验证 `codecs.Huffman` and `codecs.HuffmanQuant16` 类。
**方法**:
1. 使用 `numcodecs` API 进行 encode/decode 循环测试。
2. 模拟 `zarr` 数组存储场景，验证切片读写的正确性。

## 5. 脚本文件结构规划 (scripts/)

将在 `scripts/` 目录下创建以下 Python 脚本执行测试任务：

```text
scripts/
├── benchmark_utils.py       # 通用工具函数：计时器、误差计算、数据加载
├── 01_gen_sim_data.py       # 生成模拟数据并保存为临时文件（可选）
├── 02_test_lossless.py      # 执行无损压缩基准测试
├── 03_test_quantization.py  # 执行量化压缩测试（模拟数据 + 真实数据）
└── 04_plot_report.py        # 读取测试结果，绘制图表并生成报告

results/
├── 02/
├── 03/
└── 04/
```

### 详细脚本功能：

#### `benchmark_utils.py`
- `load_mat_file(path)`: 读取 .mat 文件。
- `calc_metrics(orig, decomp)`: 计算 RMSE, PSNR, MaxError。
- `Timer` 类: 用于精确测量代码块执行时间。

#### `02_test_lossless.py`
- 针对 uint8 数据。
- 循环测试多次取平均时间。
- 输出 `results_lossless.csv`。

#### `03_test_quantization.py`
- 针对 uint16 数据。
- 核心测试：`13um_1_im_561_005_002.mat`。
- 遍历 `scale` 参数列表: `[0.1, 0.5, 0.8, 1.0, 1.5, 2.0, 4.0]`。
- 比较 `quantize_u16` 不同实现（如果可以通过 API 强制选择 AVX/NoAVX，否则只测默认）。
- 输出 `results_quant.csv`。

#### `04_plot_report.py`
- 读取 CSV 结果。
- 生成评估图表（详见第6节）。

## 6. 预期输出结果与可视化

测试完成后，将生成以下关键图表和表格：

### 6.1 表格 (Tables)
1. **基准性能表**: 包含 数据集名称, 数据大小, 压缩比, 压缩速度, 解压速度。
2. **量化影响表**: (针对真实数据) Scale参数, 压缩比, RMSE, PSNR, 最大绝对误差。

### 6.2 可视化图表 (Figures)
1. **压缩性能对比图** (Bar Chart):
    - X轴: 不同的模拟数据类型（低熵、高熵）及真实数据。
    - Y轴: 压缩比 / 吞吐量。
    
2. **量化参数影响曲线** (Line Chart):
    - X轴: Scale 参数。
    - 左Y轴: 压缩比。
    - 右Y轴: RMSE (误差)。
    - **目的**: 寻找压缩率与图像质量的最佳平衡点。

3. **误差分布分析图** (Histogram & Heatmap):
    - **直方图**: 原始数据值 vs 解压后数据值的残差分布。
    - **散点图**: 原始像素值 (X轴) vs 误差 (Y轴)。验证误差是否随信号强度增加而保持在泊松分布方差范围内（方差稳定性）。
    - **图像对比**: 
        - 原图切片。
        - 解压后图切片。
        - 差值图 (Difference Image)，使用伪彩色显示误差空间分布。

4. **真实数据切片展示**:
    - 展示 .mat 文件中某一帧的压缩前后效果对比，特别是微弱信号区域的保留情况。

## 7. 执行步骤
1. 安装依赖：`pip install -r requirements.txt` 及 `matplotlib`, `scipy`。
2. 运行 `python scripts/02_test_lossless.py`。
3. 运行 `python scripts/03_test_quantization.py`。
4. 运行 `python scripts/04_plot_report.py`。
5. 查看生成的 PNG 图片和 CSV 报告。

