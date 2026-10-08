# Model Library Organizer

**Windows · v1.0.0 · MIT 许可证**

[English](README.md) · [日本語](README.JP.md) · **简体中文**

[下载 Windows 版](https://github.com/Take-No-Break/ModelLibraryOrganizer/releases/tag/v1.0.0) · [界面预览](#整理模型库) · [报告问题](https://github.com/Take-No-Break/ModelLibraryOrganizer/issues)

浏览已下载的 LoRA 和检查点模型，在应用内查看预览图片，以及通过公开 API 获取的触发词和描述，无需逐个打开来源网站。Model Library Organizer 还可以识别和整理文件、创建模型来源 TXT、准备 Image to Text 工作流，以及编辑训练用文本和标签。

## 可以做什么

| 功能 | 说明 |
| --- | --- |
| [模型列表](#整理模型库) | 递归扫描支持的文件，计算完整 SHA-256，匹配公开来源，识别类型和模型家族，检查未识别文件。 |
| [文件整理](#整理模型库) | 按类型和用途，或按平台 → 作者 → 类型 → 家族整理。审核移动和硬链接，执行获批变更时创建所需目录。 |
| [模型查看](#模型预览) | 在应用内查看可用的描述、触发词、来源链接和图片，调整预览区域大小。 |
| [模型检查工具](#更新作者和触发词) | 检查新版本、复制触发词、按作者浏览本地模型及比较版本说明。 |
| [图片模型查询](#查找图片使用的模型) | 将受支持生成元数据与已扫描文件匹配；无元数据的图片不能识别模型。 |
| [兼容性](#兼容性) | 按基础模型系列比较 LoRA → Checkpoint 或 Checkpoint → LoRA；保存组合的手动评价。 |
| [来源 TXT](#模型来源-txt) | 保存可用触发词、来源、类型、家族和哈希；选择附加字段，或备份后更新已有说明文件。 |
| [Image to Text](#image-to-text) | 导出一体式或分解式 ComfyUI 工作流，安装或更新所需自定义节点，也可提交给本地 ComfyUI 执行。 |
| [Edit Text](#edit-text) | 查看图片与 TXT 配对或独立 TXT，单独编辑，批量前置、追加、删除、替换和包裹文本。 |
| [Tag editor](#tag-editor) | 浏览缩略图和紧凑标签，搜索、筛选、按出现次数排序，批量插入或删除标签，审核后保存。 |
| [结果与恢复](#结果历史与恢复) | 查看操作结果，按 SHA-256 检测重复文件，查看移动历史，恢复符合条件的操作，修复支持的工作流引用。 |

**LoRA / Checkpoint 训练准备：** Image to Text、Edit Text 和 Tag editor 用于创建和编辑数据集文本；来源 TXT 用于记录下载模型的信息。本应用用于准备训练数据，不直接训练 LoRA 或 Embedding，也不生成图片。

使用 AI 助手了解本仓库或 README：[完整操作参考（英文）](docs/CONTROLS.md)。

## Windows 安装

1. 从 Releases 下载 **Windows-x64.zip**，并完整解压。
2. 运行 `Install.cmd`，或直接启动 `ModelLibraryOrganizer.exe`。请将 `_internal` 保留在 EXE 旁。
3. 选择自己的目录。安装包不包含模型权重、个人路径、历史记录或 ComfyUI。

附带 `Uninstall.cmd`，用于移除已记录的应用文件，保留模型库和用户数据。**卸载程序尚未运行或测试。** 已进行本地测试和打包程序启动验证，但没有宣称完成另一台电脑或虚拟机上的测试。

## 整理模型库

![模型列表：类型、家族及建议目标位置](docs/screenshots/models.jpg)

1. 选择包含下载模型的 **Scan folder**。扫描包括子目录。
2. 选择目标 **models folder**，例如 `ComfyUI/models` 或已配置的共享模型目录。请选择实际的 models 目录，而非 ComfyUI 程序根目录。
3. 点击 **Scan all**，选择整理方式并审核建议。扫描会记录原始路径清单，但不会移动文件。
4. 批准、拒绝或暂缓变更，然后使用 **Review and organize proposed moves**。最终确认会说明变更，并在执行前保存移动日志。

示例布局（获得相关元数据时，也可能包含用途目录）：

```text
models/loras/Character/Pony/example.safetensors
models/Civitai/ExampleCreator/loras/Pony/example.safetensors
```

目标请选择 **models 根目录**，不要选择 `models/loras` 等类型子目录。应用在所选目标下创建或复用 `loras`、`checkpoints`、`vae`、`embeddings` 等目录。若选择 `models/loras`，其他类型会嵌套在 loras 内，因此扫描前会提示改用根目录。目录创建与文件移动只在批准后执行。

家族目录来自来源返回的元数据，而不是预先打包的固定目录列表。新家族也可产生新目录建议，只有执行获批变更时才会创建。未知家族不会被猜测：可能建议类型目录、`Unknown`，或保留待审核。已正确放置的文件可以保持原位置。

不会为了整理布局而删除文件。只会移除符合条件的空源目录。目标位置冲突会标记为待审核。

### 如何识别模型

应用计算每个支持文件的完整 SHA-256。Civitai 使用公开哈希 API 查询；Hugging Face 按文件名搜索候选，并使用公开 SHA-256 验证。仅文件名相同并不代表已验证匹配。缓存、张量名称和形状、内嵌元数据也用于识别文件用途。

可识别 LoRA、检查点、VAE、Embedding、支持的 ControlNet 结构、风格适配器、模型补丁及支持的图像描述模型包。可以保留已有 ComfyUI 分类，但支持目录名称不等于能识别其中所有模型。可信的单文件张量结构优先于发布页面的整体分类。未识别或信息冲突的文件保留供审核。

SeaArt 和 Tensor.Art 不会被自动查询：本应用没有经过验证的反向哈希 API 集成。无法识别来源的模型可能需要审核，或选择整理到 `Not Found`。不会仅因查询失败就自动移动；已识别类型和原位置可以保留，也可手动指定目标。已知来源 URL 可手动添加。来源匹配不保证运行兼容性。

### 模型预览

![预览：模型列表、来源信息和图片](docs/screenshots/preview.jpg)

1. 在 **Model inspection → Preview** 扫描模型目录。
2. 组合 **Base model family**、**Model type** 和 **Filename search** 筛选列表。文件名标题按 A–Z 排序；系列标题可以切换排序方向。
3. 选择模型，查看公开触发词、描述、来源链接和文件元数据。触发词靠前显示，SHA-256 和依据在下方显示。
4. 使用 **Previous image / Next image** 浏览可取得的一般受众预览图。拖动分隔线调整列表、文本和图片区域。

图片和触发词取决于公开 API 提供的内容。受限制或不可用的图片可能不显示；在浏览器打开来源页面与通过 API 获取图片不同。本应用不提供 Civitai OAuth 登录。

**术语：** **Model type（模型类型）**表示 LoRA、Checkpoint、VAE、Embedding 等用途；**Base model family（基础模型系列）**表示 Illustrious、Pony、Anima 等基础模型或派生系列。**Identification confidence（识别可信度）**是已验证、推测等识别状态，不是数值概率；**Evidence（依据）**说明支持判断的信息。**ss_datasets** 和 **ss_tag_frequency** 中的数字描述训练数据，不是正向提示词、置信度或提示词权重。

### 更新、作者和触发词

1. 在预览中使用 Ctrl / Shift 选择模型。**Copy trigger words** 合并可用触发词并去重；离线时可以使用缓存。
2. **Check model updates** 按发布日期查找 Civitai 的新公开版本。打开链接审核版本；应用不会自动下载或替换权重。
3. **Authors** 按作者、模型和版本分组显示已扫描且仍在本机的文件。分组默认折叠；使用 **Expand all / Collapse all**，或双击文件打开预览。列表不是该作者的全部在线投稿。
4. **Compare version descriptions** 比较所选 Civitai 模型的两个版本：新增为绿色，删除为红色。比较的是描述和触发词，不是模型权重。

### 查找图片使用的模型

1. 先扫描本地模型库。
2. 点击 **Find models used in image**，选择含受支持生成信息的 PNG；当前 API 预览可使用 **Models used in this image**。
3. 将记录的模型名称、哈希或版本 ID 与已扫描文件匹配。受支持的 ComfyUI 生成节点信息也可提供加载器文件名。
4. 区分哈希或版本匹配与未经验证的文件名匹配。**Not identified** 不证明本机没有该模型。

没有生成元数据的普通 PNG 无法仅凭外观识别使用的模型。图片不限于 Civitai 来源，但元数据可能被删除或不完整。参阅[操作指南（英文）](docs/MODEL-INSPECTION-TOOLS.md)。

### 兼容性

1. 在 **Model inspection → Compatibility** 选择检查点和 LoRA 目录并扫描。
2. 选择 **LoRA → Checkpoint**，将一个 LoRA 与检查点或扩散模型比较；或选择 **Checkpoint → LoRA**，将一个检查点与多个 LoRA 比较。
3. 选择模型。**绿色**为同一基础模型系列，**黄色**为相关 SDXL 系列，**灰色**为不同或未知系列。
4. 选择组合，保存自己进行的加载或生成测试评价和备注。两个方向共享同一组合的评价。

这些是元数据估计，不是实际模型加载测试或生成保证。候选来自本机的扫描；仅选择目录不会识别其中的文件。

### 模型来源 TXT

1. 扫描模型，然后选择要记录信息的模型。
2. 在 **Text editor → Model source TXT** 选择附加字段。基本身份信息和可用的公开触发词始终包含。
3. 点击 **Create source TXT**，在模型旁创建尚不存在的 `model-name.safetensors.source.txt`。
4. **Update readable TXT** 只用于备份后重新生成应用此前创建的说明文件。

未选择模型时，创建操作使用列表中符合条件的项目。已有说明会跳过。字段标签使用英文，描述保留来源语言。这些文件记录模型信息，不是图片训练文本。模型权重不会被修改。

## LoRA / Checkpoint 训练数据准备

创建和编辑用于 LoRA 或检查点训练的图片描述 TXT。Image to Text 生成描述，Edit Text 和 Tag editor 调整触发词等文本以配合训练工具。本应用准备数据，不直接训练模型。来源 TXT 是独立功能，用于记录下载模型的信息。

### Image to Text

本项目目前实现的适配器为 **PixAI、JoyCaption、CL Tagger 和 Taggerine**，并非所有 Image to Text 模型的完整列表。在 **Image to Text model folder** 选择模型目录，再在 **Model** 选择对应适配器。需要包含该适配器所需文件的完整模型包，单个或任意 `.safetensors` 文件并不足够。其他架构需要兼容适配器的实现，否则可能加载失败。阈值设置因适配器而异，可能不适用于其他模型。权重和依赖项需另行安装。

![Image to Text：模型设置和工作流预览](docs/screenshots/image-to-text.jpg)

### 首次设置自定义节点

1. 点击 **Install / update custom nodes**。
2. 使用 **Detect**，或浏览并选择实际使用的 ComfyUI 实例的 `custom_nodes` 目录。
3. 点击 **Install / update**，用 ComfyUI 的 Python 安装缺少的依赖，然后重启 ComfyUI。
4. 输入正在运行的本地 ComfyUI URL，点击 **Check connection**。

同一套节点支持四种适配器和两种模板格式。修改路径、模型或模板格式不需要重新安装。节点代码更新时再更新节点。应用不会启动或重启 ComfyUI。

手动 ZIP 安装：通过 **Save required custom nodes** 保存后解压，使入口文件位于 `ComfyUI/custom_nodes/model_library_organizer_bridge/__init__.py`。详细排查见[节点设置（英文）](docs/CONTROLS.md#custom-node-setup)。

### 运行或导出

1. 选择图片目录、模型适配器及完整模型目录。
2. 设置对应阈值或提示词，确认自动保存位置。
3. 直接执行时，点击 **Check connection**，然后点击 **Run in ComfyUI and save image hardlinks + TXT**。
4. 导出时选择 **Combined** 或 **Expanded**，按需启用 **Save matching TXT in ComfyUI**，点击 **Save ComfyUI workflow template**。在 ComfyUI 中打开 JSON 并运行。

**工作流模板**是可编辑的可视化节点图；**所需自定义节点**是让节点工作的代码。仅导出文件不会分析图片或保存文本。

输出保存在所选图片目录内，以适配器命名的子目录中：

```text
Images/
├─ example.png              # 原图
└─ PixAI/
   ├─ example.png           # 指向原图的硬链接
   └─ example.txt           # 生成的描述文本
```

其他适配器使用 `JoyCaption`、`CL-Tagger` 或 `Taggerine`。原图保留原位置。硬链接要求同一文件系统卷；编辑硬链接图片会影响同一底层文件。已有文本会跳过，冲突图片受到保护。递归扫描排除这些生成的输出目录。

旧工作流的输出设置为空时，可能把 TXT 写在原图旁。更新自定义节点、重启 ComfyUI，并导出新模板以使用子目录布局。

## Edit Text

![文本编辑：图片列表、预览及可编辑文本](docs/screenshots/text-editor.jpg)

1. 选择数据集目录，自动加载图片和 TXT 列表。
2. 选择图片与 TXT 配对，查看图片并在右侧编辑文本。
3. 批量编辑时选择多个文件，选择包裹、前置、追加、删除或替换，然后点击 **Preview changes**。
4. 保存当前 TXT，或批准批量审核。原文件会备份；外部编辑发生冲突时会阻止保存。

### Tag editor

![标签编辑：缩略图、标签统计和图片标签](docs/screenshots/tag-editor.jpg)

1. 点击 **Open Folder**，浏览左侧缩略图。
2. 按标签出现次数排序、搜索，或选择标签筛选匹配图片。
3. 点击文本标签进行编辑，或按 **Selected / Filtered / All** 范围批量插入和删除。
4. 点击 **Save All**，审核变更后确认保存。

数值表示使用标签的文本文件数量，不是 AI 置信度。类别筛选使用本地关键词规则。编辑内容在保存前保持未保存状态。用 `< >` 包裹词语不会训练 Embedding；请与训练工具的 token 设置保持一致。

## 结果、历史与恢复

1. 打开 **Results**，选择报告，重新查看扫描、导出或文本变更。
2. 使用 **History / Restore** 查看已记录的文件移动。
3. 选择符合条件的历史记录，或打开其 JSON，然后选择 **Restore this layout**。
4. 审核确认信息后恢复。已恢复的移动日志可以根据当前记录的路径重新检查；文件变化、日志缺失或路径冲突可能阻止恢复。

**没有关联移动日志的扫描清单无法恢复文件位置。** 文件被修改、删除或路径冲突可能阻止恢复。历史不是模型内容备份，也不能撤销外部操作。[工具及恢复详情（英文）](docs/CONTROLS.md#tools)说明了重复检测和工作流引用修复。

## 离线与隐私

- **在线查询：** 发送哈希和 HF 搜索文件名，不发送模型权重或数据集图片。
- **完全离线：** 阻止外部来源、预览及更新请求。本地工具、缓存及另行运行的本地 ComfyUI 仍可使用。
- **报告与更新：** 日志从不自动提交，分享前请检查。更新检查只打开发布页面，不自动安装更新。

详情见[支持相关操作（英文）](docs/CONTROLS.md#about-support-and-updates)。

## 开发与贡献

```powershell
python -m pip install -r requirements.txt
python scripts/run_tests.py
python -m pip install pyinstaller==6.22.3
python -m PyInstaller --noconfirm ModelLibraryOrganizer.spec
```

Windows CI 使用 Python 3.12，本地 Windows 发布包使用 Python 3.14.5 构建。请用可丢弃数据测试文件整理。参阅[贡献指南](CONTRIBUTING.md)、[安全说明](SECURITY.md)和[发布准备](RELEASE_PREPARATION.md)。

## 许可证与致谢

应用源码采用 [MIT 许可证](LICENSE)。欢迎贡献和改进，但 MIT 不要求将修改提交回原项目。模型权重及第三方依赖保留各自的许可证和声明。

标签编辑界面以 [unaya-git/TagFilter](https://github.com/unaya-git/TagFilter) 为设计参考。此致谢不代表背书或合作关系。
