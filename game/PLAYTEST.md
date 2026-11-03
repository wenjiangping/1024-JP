# Go Lita 验收记录

最新：2026-11-03 的原生控件与 HomeCover 修复已在原项目发布，详见本文件末尾“原生控件与封面验收”。下方 2026-10-25/26 记录保留为历史，旧版隐藏运行积分的行为已被本轮修复取代。

2026-10-25，用户账号 En / 原项目 IdeaDash，XBuilder SPX 3.3.0 浏览器预览，480 × 360、4:3。项目仅导入、编译和预览，未发布。

## 本轮导入与运行

导入 `Go-Lita-runner-v0.5.xbp` 后，XBuilder 编译成功。精灵列表显示 `炸弹2`，旧 `炸弹` 和 `grass footsteps` 已移除；声音列表为“背景音乐”“坠落声”“获得宝石”“烟花声”。首页显示正常，点击 START 进入说明页，再点击说明页 START GAME 进入跑酷。

跑酷画面核对：运行页隐藏左侧囤粮分标签和动态数字；称号 HUD 已移至最右侧并保留边距；左、右、上三个按键相邻放在左下；暂停、重新开始两个按键相邻放在右下。暂停后按钮显示用户提供的“按键-暂停后开始”图标，点击后恢复运行。运行日志显示开局障碍密度为 1.0，较上一版翻倍。

自然运行得到多次 `HARVEST`，并在静态障碍挤出边界后输出 `FINISH 被障碍挤出小径了`。结算卡显示真实囤粮分 `6`，等待 2.5 秒后数字仍保持静态，没有闪动。失败画面、称号和 HOME / RESTART 按钮均正常。

## 规则核对

| 阶段 | 囤粮分 | 称号 | 速度 px/s | 目标障碍密度 |
|---:|---:|---|---:|---:|
| 0 | 0–19 | 蹦跶小新手 | 58 | 1.0 |
| 1 | 20–39 | 树影穿梭客 | 75.4 | 1.3 |
| 2 | 40–59 | 灌木飞毛腿 | 98.02 | 1.69 |
| 3 | 60–79 | 林间寻路家 | 127.426 | 2.197 |
| 4 | 80–99 | 风之探险家 | 165.6538 | 2.8561 |
| 5 | 100+ | 森林守护者 | 215.34994 | 3.71293 |

积分仍只来自收集：蘑菇 +1、水晶 +3；时间、距离、跳跃和存活时长不加分。每档速度乘 1.3，障碍生成密度在上一版基础上翻倍后继续乘 1.3；每段最多两个障碍，安全路段规则保留。

## 工程检查

`python game/tools/package_project.py` 与 `--check` 均通过：38 个精灵、205 个文件，检查 4:3 舞台、全局物理、按钮几何、`炸弹2` 静态物理、声音顺序、资源完整性、ZIP 完整性和源码逐字节一致。`git diff --check` 通过。

## 说明

背景音乐仅在首页和说明页播放，并按约 74 秒重新开始；进入跑酷或结算后停止。Lita 行走不再触发脚步声，Fall 动画只播放一次“坠落声”。短局已验证页面、按钮、收集、暂停、障碍挤出和静态结算；炸弹2的危险判定与动画资源已随正式包导入，尚未为专项测试强行制造炸弹碰撞。

## v0.6 增强回归（2026-10-26）

本轮保留 v0.5 的页面、输入、物理和结算流程，并在正式源码中加入三项回归保护：

- 结束时保留 `FinalScore`，记录当前运行会话最高分；新纪录和四类失败原因通过 Lita 气泡反馈，结算数字仍只绘制一次。
- `Esc` 可暂停/继续，结算页按 `Enter` 可直接重开；原有 `P`、`R` 和屏幕按钮继续可用。
- 路段生成后检查障碍与收集物的水平重叠，重叠的收集物抬到跳跃路线，避免素材被障碍遮住。

本地回归：`python game/tools/package_project.py`、`python game/tools/package_project.py --check` 与 `git diff --check` 通过。随后将同一份 `Go-Lita-runner-v0.5.xbp` 导入用户 `En / IdeaDash` XBuilder 项目并运行：

- 首页、说明页和跑酷页画面正常；控制台出现 `SCREEN HOME`、`SCREEN HELP`、`SCREEN PLAY`、`HARVEST`。
- `P` 暂停/恢复与 `Esc` 暂停均输出 `PAUSE true/false`，暂停期间分数和时间冻结。
- 自然结束输出 `FINISH 被障碍挤出小径了 ... BEST 6 NEW true`，结算卡显示真实分数 `6`，Lita 显示“新纪录！”。
- 结算页按 `Enter` 输出 `SCREEN RETRY` 并重新开始，确认无需重新打开说明页。

本次没有改变舞台尺寸、按钮几何、计分公式或资源顺序。

## v0.7 HUD 回归（2026-10-26）

本轮仅调整运行页 HUD：`ScorePanel` 与 `ScoreDigits` 在 `Screen == 2` 时隐藏，结算页 `Screen == 3` 的静态分数绘制保持不变；`RankPanel` 从 x=105 移至 x=155，右边保留约 14 px。首页、说明页、暂停、结算和重开流程沿用 v0.6。

## 原生控件与封面验收（2026-11-03）

先在 [PR #5](https://github.com/wenjiangping/1024-JP/pull/5) 提交优化方案和正式改动，再导入原项目 `En / IdeaDash`。XBuilder SPX 3.3.0 编译成功，舞台仍为 480 × 360。四个原生 Monitor 分别读取运行积分 `Score`、冻结结算积分 `FinalScore` 和共用称号 `Rank`，只在对应页面显示；首页和说明页均隐藏。已删除模拟积分与称号的五个旧精灵及图片。

### 正式包自然试玩

- 首页 → 说明 → 跑酷 → 结算流程通过；控制台连续输出 `HARVEST 1` 至 `HARVEST 6`，最后 `FINISH ... 6 6 0`，结算控件显示 6 分与“蹦跶小新手”。[画面](evidence/v07/natural-result-6.png)、[日志](evidence/v07/natural-run.txt)。
- 结算页 Enter 重开清空本局积分；自然收集 2 分后按 P 暂停，系统积分和称号仍可见，约一分钟后分数和世界位置不变。[暂停画面](evidence/v07/live-paused-stable.png)。

### 临时回归包

使用 `create_native_hud_playtest.py --output <临时文件>` 生成带 `QAHUD` 标记的独立测试包，只为稳定触达边界条件，不修改正式源码。以下预置分数不属于自然试玩成绩。

| 用例 | 结果 | 证据 |
|---|---|---|
| 各阈值前一分，实际收集蘑菇两次 | 分别停在 20/40/60/80/100；重复领取不加分；五档称号正确 | [20](evidence/v07/threshold-1.png)、[40](evidence/v07/threshold-2.png)、[60](evidence/v07/threshold-3.png)、[80](evidence/v07/threshold-4.png)、[100](evidence/v07/threshold-5.png) |
| 18 蘑菇 + 1 水晶；重复领取水晶；暂停时再尝试收集 | 21 分、18 蘑菇、1 水晶，称号“树影穿梭客”；结算同为 21 分 | [运行](evidence/v07/fixture-crystal-21-live.png)、[结算](evidence/v07/fixture-crystal-21-final.png) |
| 0 分结束 | 原生控件显示 0 与“蹦跶小新手” | [画面](evidence/v07/fixture-zero.png) |
| 120 蘑菇 + 2 水晶，126 分结束 | 结束后收集与重复结束无效；随后将实时 Score 改成 999，FinalScore 和结算画面仍为 126，约 19 秒后保持 | [画面与日志](evidence/v07/fixture-frozen-126-stable.png) |

[完整 QA 日志](evidence/v07/qa-log.txt) 包含上述阈值、重复收集和冻结结果。打包校验器会拒绝正式源码中的 `QAHUD`、`QAFlow` 和 `QAScenario` 标记。

### 正式恢复与发布

QA 完成后重新导入正式 `Go-Lita-runner-v0.5.xbp`，再次编译成功，首页正常。发布前导出云端包，确认全部 34 份 `.spx` 与仓库源码逐字节一致、没有 QA 入口；4 个 Monitor 的绑定和初始隐藏状态正确；项目描述、操作说明保持原云端内容。

HomeCover 编辑态默认可见，导出的自动缩略图为 HomeCover，避免保存时重新变成石堆场景。2026-11-03 已在原项目执行一次发布，看到成功提示，公开页新增本次发布历史并显示 HomeCover。[发布成功](evidence/v07/publish-success.png)、[公开页封面与发布历史](evidence/v07/published-homecover.png)。

发布后在[公开页面](https://x.qiniu.com/project/En/IdeaDash)进入说明和跑酷，实际收集到 2 分后暂停，运行积分与称号系统控件均正常显示。[发布版运行画面](evidence/v07/published-live-hud.png)。

本地 `python game/tools/package_project.py --check`、Python 工具语法检查与 `git diff --check` 通过；正式包为 33 个精灵、171 个文件。PR #5 保持打开，未合并。
