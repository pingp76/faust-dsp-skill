# Faust DSP Skill

让 Codex、Claude Code 或其他支持 skill 的 AI agent 帮你写、检查、试听和调试
[Faust](https://faust.grame.fr/) DSP 音频程序。

如果你是音乐人、声音设计师、电子乐玩家，暂时不懂 MCP、Python、Node.js 这些词也没关系。这个项目的目标就是：你只管描述声音，AI 帮你把本地 Faust 测试环境装好、启动好、用完关掉。

## 这个东西能帮你做什么

你可以对 AI 说：

```text
Use $faust-dsp to write a simple warm pad synth in Faust and check whether it outputs sound.
```

或者中文也可以：

```text
用 $faust-dsp 帮我检查这个 Faust 合成器为什么没声音，并修好。
```

安装后，AI 可以帮你：

- 写 Faust `.dsp` 合成器或效果器。
- 检查 Faust 代码有没有语法错误。
- 分析声音是否静音、爆音、削波。
- 启动本地浏览器试听界面。
- 调参数、读取音频电平、查看 scope/spectrum/probe 数据。
- 自动安装和启动底层 runtime，尽量不让你手动配置 MCP server。

## 一句话解释

这是一个 **AI skill**，不是普通音频插件。

它会教 AI 如何使用本地 Faust runtime。真正的编译、分析和试听能力来自
[sletz/faust-mcp](https://github.com/sletz/faust-mcp)。本项目把它包装成更容易安装和使用的 skill：需要时自动下载，需要时启动，用完可以自动关闭。

## 推荐安装：Codex

### 1. 下载这个项目

打开终端，运行：

```bash
git clone https://github.com/pingp76/faust-dsp-skill.git
cd faust-dsp-skill
```

### 2. 安装 skill

```bash
mkdir -p ~/.codex/skills
cp -R skill/faust-dsp ~/.codex/skills/
```

### 3. 重启 Codex

重启后，Codex 才会重新扫描 skills。之后你就可以在对话里使用：

```text
$faust-dsp
```

### 4. 测试是否安装成功

你可以对 Codex 说：

```text
Use $faust-dsp to run doctor and tell me what is missing.
```

或者自己在终端运行：

```bash
python3 ~/.codex/skills/faust-dsp/scripts/faust_runtime.py doctor
```

如果看到一段 JSON 状态信息，就说明 skill 脚本可以运行。

## Claude Code 和其他支持 skill 的 agent

把这个目录复制到你的 agent 能读取 skills 的位置：

```text
skill/faust-dsp
```

这个目录里面有标准的：

```text
faust-dsp/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

Claude Code 的插件项目通常会把 skill 放在类似 `skills/faust-dsp/` 的目录里。其他 agent 的安装位置可能不同，请按那个工具自己的 skill 搜索路径放置。

## 第一次使用会发生什么

第一次真正分析或试听 Faust 代码时，AI 会通过这个脚本工作：

```bash
python3 scripts/faust_runtime.py ...
```

它会按需做这些事：

1. 检查电脑上有没有 `git`、Python、Faust、编译器等基础工具。
2. 把 `sletz/faust-mcp` 下载到本机缓存目录。
3. 创建一个独立的 Python 虚拟环境。
4. 安装运行所需的 Python 依赖。
5. 如果你需要浏览器试听界面，再安装浏览器 UI 相关依赖。
6. 启动本地 runtime。
7. 任务结束时关闭由 skill 启动的后台进程。

默认缓存位置是：

```text
~/.cache/faust-dsp-skill/
```

也就是说，它不会把一堆 runtime 文件塞进你的音乐工程目录。

## 常用命令

这些命令主要给 AI 或稍微懂终端的用户使用。平时你可以直接让 AI 运行。

检查环境：

```bash
python3 scripts/faust_runtime.py doctor
```

安装/准备底层 runtime：

```bash
python3 scripts/faust_runtime.py ensure
```

分析一个 Faust 文件是否有声音：

```bash
python3 scripts/faust_runtime.py analyze --dsp assets/examples/oscillator.dsp
```

启动浏览器试听 runtime：

```bash
python3 scripts/faust_runtime.py start --kind browser
```

查看 runtime 是否还在运行：

```bash
python3 scripts/faust_runtime.py status
```

关闭 skill 启动的 runtime：

```bash
python3 scripts/faust_runtime.py stop
```

## 你可能需要安装的基础软件

最简单的离线分析通常需要：

- Git：用来下载底层 runtime。
- Python 3：用来运行管理脚本。
- Faust CLI：真正编译 Faust DSP。
- C++ 编译器：离线分析时使用。

如果你用 macOS，通常会需要：

```bash
xcode-select --install
```

如果你用 Homebrew，可以尝试：

```bash
brew install git python faust
```

如果这些你不熟，不要紧。你可以直接把报错贴给 AI，让它用 `$faust-dsp` 帮你解释下一步。

## 浏览器试听时的注意事项

浏览器播放声音有一个现实限制：很多浏览器要求用户亲自点击一下页面上的按钮，才能解锁音频。

所以如果 AI 启动了浏览器试听界面，但你还听不到声音，先看页面上有没有类似：

```text
Unlock Audio
```

或者输出开关按钮。点一下之后再让 AI 继续调试。

## 常见问题

### 我必须懂 MCP 吗？

不需要。

这个 skill 背后会使用来自 `sletz/faust-mcp` 的本地 runtime，但你不需要自己配置 MCP server。AI 会通过脚本自动安装、启动和调用。

### 这是不是 VST/AU 插件？

不是。它是给 AI agent 用的 skill。它帮助 AI 写和测试 Faust DSP。你之后可以再把 Faust 代码导出到其他音频插件或工程里。

### 会不会一直开着后台服务？

设计上不会。`faust_runtime.py` 会记录自己启动的进程，并提供：

```bash
python3 scripts/faust_runtime.py stop
```

来关闭它们。AI 使用这个 skill 时，也应该在任务结束前关闭自己启动的 runtime。

### 为什么不直接把 faust-mcp 放进这个仓库？

因为本项目创建时，上游 `sletz/faust-mcp` 没有明确的 license 文件。为了尊重上游版权，这里不直接复制上游源码，而是在用户本机按需下载。

## 项目来源

这个 skill 是基于
[sletz/faust-mcp](https://github.com/sletz/faust-mcp)
的 runtime 设计和工具接口改写出来的。

`sletz/faust-mcp` 提供了 Faust MCP server、浏览器 runtime、Node realtime runtime、离线分析等核心实现。本项目提供的是更适合 AI skill 使用的说明、脚本包装、安装流程和面向 agent 的工作方式。

## License

本仓库中的 wrapper 脚本和文档使用 MIT License。

MIT License 不自动覆盖运行时下载的上游 `sletz/faust-mcp` 代码。上游代码的使用应以它自己的授权状态为准。
