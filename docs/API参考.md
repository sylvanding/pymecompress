# PYMECompress API 参考

## 模块结构

```
pymecompress
├── HuffmanCompress          # 霍夫曼压缩（低级API）
├── HuffmanCompressQuant     # 量化霍夫曼压缩（低级API）
├── HuffmanDecompress        # 霍夫曼解压（低级API）
├── codecs                   # numcodecs编解码器（高级API）
│   ├── Huffman              # 霍夫曼编解码器类
│   └── HuffmanQuant16       # 量化霍夫曼编解码器类
└── version                  # 版本信息
```

## 低级API (pymecompress.bcl)

### HuffmanCompress

```python
pymecompress.HuffmanCompress(data: np.ndarray) -> np.ndarray
```

**功能**: 使用霍夫曼编码压缩数据

**参数**:
- `data` (np.ndarray): 输入数据，必须是uint8类型的NumPy数组

**返回**:
- `np.ndarray`: 压缩后的数据（uint8数组）

**示例**:
```python
import numpy as np
import pymecompress

data = np.array([1, 2, 3, 4, 5], dtype='uint8')
compressed = pymecompress.HuffmanCompress(data)
```

**注意**:
- 输入必须是uint8类型
- 对于其他类型，需要先转换为uint8视图：`data.view('uint8')`

---

### HuffmanCompressQuant

```python
pymecompress.HuffmanCompressQuant(
    data: np.ndarray,
    offset: float,
    scale: float
) -> np.ndarray
```

**功能**: 先量化再压缩uint16数据

**参数**:
- `data` (np.ndarray): 输入数据，必须是uint16类型
- `offset` (float): 量化偏移量（背景值）
- `scale` (float): 量化缩放因子

**返回**:
- `np.ndarray`: 压缩后的数据（uint8数组）

**量化公式**:
```
quantized = sqrt((data - offset) / scale)
```

**示例**:
```python
import numpy as np
import pymecompress

# 模拟光子计数数据
data = np.random.poisson(100, 1000).astype('uint16')

# 压缩
compressed = pymecompress.HuffmanCompressQuant(data, offset=0, scale=1.0)
```

**注意**:
- 输入必须是连续的uint16数组
- offset和scale影响压缩率和精度
- 量化是有损的，但误差在泊松噪声范围内

---

### HuffmanDecompress

```python
pymecompress.HuffmanDecompress(
    data: np.ndarray,
    outsize: int
) -> np.ndarray
```

**功能**: 解压缩霍夫曼编码的数据

**参数**:
- `data` (np.ndarray): 压缩数据，uint8数组
- `outsize` (int): 解压后的字节数

**返回**:
- `np.ndarray`: 解压后的数据（uint8数组）

**示例**:
```python
import numpy as np
import pymecompress

# 压缩
data = np.array([1, 2, 3, 4, 5], dtype='uint8')
compressed = pymecompress.HuffmanCompress(data)

# 解压
original_size = data.nbytes
decompressed = pymecompress.HuffmanDecompress(compressed, original_size)
```

**注意**:
- 必须提供正确的outsize，否则会出错
- 返回的是uint8数组，需要手动转换类型

---

### huffman_compress_buffer

```python
pymecompress.bcl.huffman_compress_buffer(data: np.ndarray) -> bytes
```

**功能**: 压缩并返回bytes对象

**参数**:
- `data` (np.ndarray): uint8数组

**返回**:
- `bytes`: 压缩后的字节串

**示例**:
```python
from pymecompress import bcl
import numpy as np

data = np.array([1, 2, 3], dtype='uint8')
compressed_bytes = bcl.huffman_compress_buffer(data)
```

---

### huffman_compress_quant_buffer

```python
pymecompress.bcl.huffman_compress_quant_buffer(
    data: np.ndarray,
    offset: float,
    scale: float
) -> bytes
```

**功能**: 量化压缩并返回bytes

**参数**:
- `data` (np.ndarray): uint16数组
- `offset` (float): 量化偏移
- `scale` (float): 量化缩放

**返回**:
- `bytes`: 压缩后的字节串

---

### huffman_decompress_buffer

```python
pymecompress.bcl.huffman_decompress_buffer(
    data: bytes,
    out: np.ndarray = None
) -> np.ndarray
```

**功能**: 从bytes解压缩

**参数**:
- `data` (bytes): 压缩数据
- `out` (np.ndarray, 可选): 预分配的输出缓冲区

**返回**:
- `np.ndarray`: 解压后的数据

---

## 高级API (pymecompress.codecs)

### Huffman类

```python
class pymecompress.codecs.Huffman(Codec)
```

**功能**: numcodecs兼容的无损霍夫曼编解码器

**属性**:
- `codec_id` (str): 'pymecompress-huffman'

#### 方法

##### encode

```python
Huffman.encode(buf: np.ndarray) -> bytes
```

**功能**: 编码数据

**参数**:
- `buf` (np.ndarray): 输入缓冲区，必须是uint8类型

**返回**:
- `bytes`: 编码后的数据

**示例**:
```python
from pymecompress import codecs
import numpy as np

huff = codecs.Huffman()
data = np.ones(1000, dtype='uint8')
compressed = huff.encode(data)
```

##### decode

```python
Huffman.decode(buf: bytes, out: np.ndarray = None) -> np.ndarray
```

**功能**: 解码数据

**参数**:
- `buf` (bytes): 编码数据
- `out` (np.ndarray, 可选): 输出缓冲区

**返回**:
- `np.ndarray`: 解码后的数据

**示例**:
```python
decompressed = huff.decode(compressed)
```

##### get_config

```python
Huffman.get_config() -> dict
```

**返回**: 编解码器配置字典

##### from_config

```python
@classmethod
Huffman.from_config(config: dict) -> Huffman
```

**功能**: 从配置创建实例

---

### HuffmanQuant16类

```python
class pymecompress.codecs.HuffmanQuant16(Codec)
```

**功能**: numcodecs兼容的量化霍夫曼编解码器

**属性**:
- `codec_id` (str): 'pymecompress-quant16'

#### 构造函数

```python
HuffmanQuant16(offset: float = 0, scale: float = 1)
```

**参数**:
- `offset` (float): 量化偏移量，默认0
- `scale` (float): 量化缩放因子，默认1

**示例**:
```python
from pymecompress import codecs

# 默认参数
codec1 = codecs.HuffmanQuant16()

# 自定义参数
codec2 = codecs.HuffmanQuant16(offset=100, scale=0.5)
```

#### 方法

##### encode

```python
HuffmanQuant16.encode(buf: np.ndarray) -> bytes
```

**功能**: 量化并编码uint16数据

**参数**:
- `buf` (np.ndarray): 输入数据，必须是uint16类型

**返回**:
- `bytes`: 编码后的数据

**示例**:
```python
codec = codecs.HuffmanQuant16(offset=0, scale=1.0)
data = np.linspace(1, 2**15, 1000).astype('uint16')
compressed = codec.encode(data)
```

##### decode

```python
HuffmanQuant16.decode(buf: bytes, out: np.ndarray = None) -> np.ndarray
```

**功能**: 解码并反量化数据

**参数**:
- `buf` (bytes): 编码数据
- `out` (np.ndarray, 可选): 输出缓冲区

**返回**:
- `np.ndarray`: 解码后的uint16数据

**反量化公式**:
```
dequantized = quantized^2 * scale + offset
```

**示例**:
```python
decompressed = codec.decode(compressed)
```

##### get_config

```python
HuffmanQuant16.get_config() -> dict
```

**返回**: 
```python
{
    'id': 'pymecompress-quant16',
    'offset': self._offset,
    'scale': self._scale
}
```

##### from_config

```python
@classmethod
HuffmanQuant16.from_config(config: dict) -> HuffmanQuant16
```

**功能**: 从配置创建实例

**参数**:
- `config` (dict): 配置字典

**示例**:
```python
config = {'id': 'pymecompress-quant16', 'offset': 100, 'scale': 2.0}
codec = codecs.HuffmanQuant16.from_config(config)
```

---

## C/Cython接口（内部使用）

### quantize_u16

```c
void quantize_u16(
    uint16_t *data,
    uint8_t *out,
    int size,
    float offset,
    float scale
)
```

**功能**: 量化uint16数组为uint8

**实现**: 
- 自动检测CPU特性
- 支持AVX时使用`quantize_u16_avx`
- 否则使用`quantize_u16_noavx`

---

### quantize_u16_avx

```c
void quantize_u16_avx(
    uint16_t *data,
    uint8_t *out,
    int size,
    float offset,
    float scale
)
```

**功能**: AVX优化的量化函数

**性能**: 
- 并行处理8个像素
- 使用256位SIMD寄存器
- 约2-3倍性能提升

---

### quantize_u16_noavx

```c
void quantize_u16_noavx(
    uint16_t *data,
    uint8_t *out,
    int size,
    float offset,
    float scale
)
```

**功能**: 标准C实现的量化函数

**用途**: 兼容不支持AVX的CPU

---

### Huffman_Compress

```c
unsigned int Huffman_Compress(
    unsigned char *in,
    unsigned char *out,
    unsigned int insize
)
```

**功能**: C级别的霍夫曼压缩

**参数**:
- `in`: 输入缓冲区
- `out`: 输出缓冲区
- `insize`: 输入大小

**返回**: 压缩后的大小

---

### Huffman_Uncompress

```c
void Huffman_Uncompress(
    unsigned char *in,
    unsigned char *out,
    unsigned int insize,
    unsigned int outsize
)
```

**功能**: C级别的霍夫曼解压

**参数**:
- `in`: 输入缓冲区
- `out`: 输出缓冲区
- `insize`: 输入大小
- `outsize`: 输出大小

---

## 错误和异常

### ValueError

**触发条件**:
- 输入数据类型不正确
- 数组不连续

**示例**:
```python
# 错误：类型不对
data = np.array([1, 2, 3], dtype='float32')
# compressed = pymecompress.HuffmanCompress(data)  # 会报错

# 正确：转换为uint8
compressed = pymecompress.HuffmanCompress(data.view('uint8'))
```

### MemoryError

**触发条件**:
- 输出缓冲区太小
- 内存不足

---

## 类型定义

### 支持的NumPy数据类型

| API | 输入类型 | 输出类型 |
|-----|---------|---------|
| `HuffmanCompress` | uint8 | uint8 |
| `HuffmanCompressQuant` | uint16 | uint8 |
| `HuffmanDecompress` | uint8 | uint8 |
| `Huffman.encode` | uint8 | bytes |
| `Huffman.decode` | bytes | uint8 |
| `HuffmanQuant16.encode` | uint16 | bytes |
| `HuffmanQuant16.decode` | bytes | uint16 |

---

## 版本信息

```python
import pymecompress
print(pymecompress.version.version)  # '0.3.6'
```

---

## numcodecs注册

编解码器在导入时自动注册：

```python
from pymecompress import codecs

# 现在可以通过codec_id获取
import numcodecs
codec = numcodecs.get_codec({'id': 'pymecompress-huffman'})
```

**注意**: 读取使用pymecompress压缩的Zarr文件前，必须先导入codecs模块。

