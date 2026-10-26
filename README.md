# txtkit

**处理大文本文件时，先别急着 `cat | grep`。**

`txtkit` 是三个纯标准库小工具合在一起：统计、查找、截取。
针对的场景是——日志文件几十 MB、终端里滚屏看不清、或者你只想看某个区间。

- 零依赖，Python 3.10+ 标准库
- 单文件，`txtkit.py` 拷走就能用
- 中文按字符统计，不会把一个汉字算成一个"词"

<!-- ipos:install -->
## 安装

零依赖，Python 3.10+ 即可：

```bash
pip install eduar-tree-txtkit
```

装完直接用命令名调用：

```bash
txtkit --help
```

也可以不用安装，直接把 `txtkit.py` 拷走用——它只依赖标准库。

## 用法

`txtkit` 有三个子命令。

### count —— 看清一个文件有多大

```bash
python txtkit.py count access.log
```

```
characters           1048576
characters_no_space   921344
lines                  18432
blank_lines             310
words_latin            21093
cjk_characters            0
total_words            21093
```

`characters_no_space` 用来估算 token 量级（英文场景下大致是字符数的 4 倍）。
`words_latin` 和 `cjk_characters` 分开统计，是因为中文没有空格分词，
把"汉字数"当成"词数"会严重低估。

### find —— 带着上下文找东西

```bash
python txtkit.py find app.log "ERROR|Timeout" --context 2
```

```
>  1204 | 2026-10-25T10:03:11Z ERROR upstream timeout after 30000ms
   1205 |   retrying request id=8f21
   1206 | 2026-10-25T10:03:12Z ERROR upstream timeout after 30000ms
  ...
```

`>` 标记命中行，上下文行以空格开头。文件里每一行都会带行号，方便回头定位。

没有匹配时退出码是 `1`，可以直接用在 shell 判断里：

```bash
python txtkit.py find app.log "FATAL" --context 3 || echo "没有致命错误"
```

### slice —— 只取你要的那一段

```bash
# 按行取 10 到 30 行
python txtkit.py slice app.log --lines 10:30

# 按字符取前 500 个字符
python txtkit.py slice app.log --chars 0:500
```

区间语法：

| 写法 | 含义 |
|---|---|
| `10:30` | 第 10 行到第 30 行（含两端） |
| `10` | 只有第 10 行 |
| `10:` | 第 10 行到结尾 |
| `:30` | 从开头到第 30 行 |

## 输出

三个子命令的输出都是纯文本，可以直接接进管道：

```bash
# count 输出键值对，一行一个
python txtkit.py count access.log

# find 输出命中行与上下文，> 标记命中行
python txtkit.py find app.log "ERROR" --context 2

# slice 只输出取到的那一段，原样输出，不加任何标记
python txtkit.py slice app.log --lines 10:30
```

`count` 的输出示例：

```
characters           1048576
characters_no_space   921344
lines                  18432
blank_lines             310
words_latin            21093
cjk_characters            0
total_words            21093
```

## 编码处理

默认按 UTF-8 读取。遇到非 UTF-8 文件（老的 GBK 日志）不会崩——会退回
`errors="replace"`，坏字节显示成 `�`。宁可显示乱码也不要整个流程挂掉。

这意味着 `count` 的字符数在乱码文件上会偏大，介意的话请先转换：

```bash
iconv -f gbk -t utf-8 app.log > app.utf8.log
```

## 已知局限

- **整体读入内存**。几百 MB 的文件会占不少内存。真的很大请配合 `head` / `tail` 先切一刀。
- **不处理压缩文件**。`.gz` 需要先 `gunzip`。
- **不跟踪行尾差异**。`\r\n` 与 `\n` 混排时统计的"行数"仍按 `\n` 算。
- **正则用 Python 语法**，不是 grep 的基本正则（BRE）。`\d`、`\w` 可用，`\b` 行为一致。
- **find 的输出会全部打印**。文件很大时建议先缩小范围。

## 跑测试

```bash
python test_txtkit.py
```

---

## 关于作者

eduar-tree 写日志排查与文本处理的纯标准库小工具。这个工具默认用 Unix 风格，输出能直接接进管道。

- 个人主页：<https://eduar-tree.github.io>
- 仓库：<https://github.com/eduar-tree/txtkit>

## 许可

MIT，见 [LICENSE](LICENSE)。
