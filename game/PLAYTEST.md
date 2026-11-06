# Go Lita 验收记录

最新：2026-11-03 的原生控件与 HomeCover 修复已在原项目发布，详见本文件末尾“二次调整验收”。下方 2026-10-25/26 记录保留为历史，旧版隐藏运行积分的行为已被本轮修复取代。

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


## 二次调整验收（2026-11-03）

按用户后续要求，更新同一 [PR #5](https://github.com/wenjiangping/1024-JP/pull/5)，先推送修改，再导入原 XBuilder 项目。正式包为 36 个精灵、194 个文件和 2 个系统 Monitor。

- 运行页右侧称号控件移至 x=102.6，左侧维持 x=-225；两侧外边距约为 15 个舞台像素。自然运行和 21 分称号截图均保持一致边距。[运行画面](evidence/v07-followup/production-live-balanced.png)、[21 分运行画面](evidence/v07-followup/qa-live-21.png)。
- 结算页移除系统 Monitor，恢复原版橙色数字和称号及“囤粮分 / 达成成就”文字。`FinalScore` 与 `FinalRank` 在结束瞬间从运行控件所绑定的 `Score` / `Rank` 同时冻结。
- 正式自然试玩连续收集 6 个蘑菇，结算显示 6 与“蹦跶小新手”；Enter 重开显示系统积分 0，结算文字不残留。[自然日志](evidence/v07-followup/production-natural-log.txt)、[重开画面](evidence/v07-followup/production-retry.png)。
- 最新 QA 包中 18 蘑菇加 1 水晶为 21 分，重复领取及暂停收集不加分；运行控件与原版结算均显示 21 / 树影穿梭客。[结算画面](evidence/v07-followup/qa-final-21.png)。
- 零分结算正确显示 0 与“蹦跶小新手”。[画面](evidence/v07-followup/qa-zero.png)。
- 126 分结束后尝试重复结束与收集，并将实时 Score 改为 999、Rank 改为测试文字；原版结算仍为 126 / 森林守护者。“新纪录！”气泡已移除。[冻结画面](evidence/v07-followup/qa-frozen-126.png)、[QA 日志](evidence/v07-followup/qa-log.txt)。预置分数仅用于边界验证，不是自然试玩成绩。

QA 后再次导入正式包并编译运行至首页；导出云端存档确认 37 份 `.spx` 与仓库逐字节一致，无 QA 标记，Lita 脚本无“新纪录！”文本，只有 Score/Rank 两个运行控件，HomeCover 默认可见，项目描述与操作说明保持一致。

`python game/tools/package_project.py --check`、工具语法检查及 `git diff --check` 通过。本轮仅发布一次，发布说明使用玩家可读的简短概述：“优化界面布局与结算展示，提升游戏体验。”。[发布成功](evidence/v07-followup/publish-success.png)。PR 保持打开，未合并。

发布后在公开版本自然试玩，结算显示 6 / 蹦跶小新手，保留原版橙色文字，无“新纪录！”气泡；运行控件左右外边距一致，HomeCover 与简短发布历史均正常。[公开版运行](evidence/v07-followup/published-live-balanced.png)、[公开版结算](evidence/v07-followup/published-settlement.png)、[公开封面](evidence/v07-followup/published-homecover.png)。


## 高分运行稳定性回归（2026-11-05）

基于已合并 PR #5 的 GitHub main 创建 `codex/fix-highscore-obstacle-capacity`，先提交 [PR #6](https://github.com/wenjiangping/1024-JP/pull/6)，再同步 XBuilder 原项目。

- 原云端项目导出备份；37 份 SPX 脚本与 GitHub main 一致。
- 原始生成器的密度从 60 分起超过每段两个固定障碍槽位。修复在累计配额前将实际密度封顶为 2；低分配额、速度与安全路线保持原规则。
- 本地回归直接提取生产生成函数，仅转换 XGo 调用写法并添加观测。旧源码在 60 分跨路段写入失败；新版 14 档积分共 28 万次路段再生、6 万次配额分配通过，含数组范围、槽位归属、双障碍间距、缺口与开局安全路线。[旧版反例](evidence/highscore-stability/capacity-before.txt)、[修复后](evidence/highscore-stability/capacity-after.txt)。
- XBuilder SPX 3.3.0 中临时包编译通过；14 档积分共 2800 次路段再生完成，控制台出现 `QA_CAPACITY_ALL_PASS 2800`。[记录](evidence/highscore-stability/xbuilder-sweep.txt)、[截图](evidence/highscore-stability/qa-sweep.png)。
- 临时包从 70 分运行到 152 分，经过 80/100 分阈值，持续约 65.155 秒，地图与收集物继续循环；高档日志实际生成数始终为 2，配额无积压。手动结束后原版结算显示 152 / 森林守护者，Enter 重试恢复 0 分。[运行](evidence/highscore-stability/qa-highscore-live.png)、[结算](evidence/highscore-stability/qa-highscore-settlement.png)、[日志](evidence/highscore-stability/xbuilder-finish.txt)。

临时包为稳定持续运行跳过了角色物理与危险事件，70 分为预置数据；以上不作为自然试玩成绩。正式源码没有该入口，打包检查拒绝 `QACapacity`。测试后已重新导入正式修复包并编译成功，首页 HomeCover 正常。[正式首页](evidence/highscore-stability/production-home.png)。


正式包自然试玩收集 6 个蘑菇后正常结算为 6 / 蹦跶小新手。[正式结算](evidence/highscore-stability/production-settlement.png)、[日志](evidence/highscore-stability/production-log.txt)。发布前从原云端项目再次导出，37 份 SPX 脚本与仓库正式源码逐字节一致；无 QA 标记，两个系统 Monitor 与 HomeCover 保持正确。

本轮在原项目成功发布一次，说明为“修复游戏运行问题，提升游玩稳定性。”；公开项目发布历史已显示该简短概述。[发布成功](evidence/highscore-stability/publish-success.png)、[公开历史](evidence/highscore-stability/published-history.png)。


## 120–200 分称号扩充（2026-11-06）

新增 120–139 林海追风侠、140–159 秘境开拓者、160–179 星辉守望者、180–199 万木守护神、200+ 森林传说王。0–119 分称号保持原样；称号阶段单独封顶为 10，难度仍封顶为 5，120 分后的晋升不会重置障碍配额。

五张用户原图等比例缩至 640×358，沿用原成就精灵位置和 0.4375 倍缩放；旧造型、图片及 ID 保持原样。结算新增同样字体、颜色和尺寸的五个橙色称号造型，仍读取冻结的 `FinalRank`。

本地 `check_rank_progression.py` 通过 251 个分数、20 组蘑菇/水晶跨档、重复/暂停/结束收集、结算冻结、最高称号和初始化检查；原 `check_obstacle_capacity.py` 的 28 万次路段再生及 6 万次配额分配通过。打包及逐字节检查通过，36 个精灵、204 个文件；工具语法与 `git diff --check` 通过。原项目已导出备份，37 份 SPX 与 GitHub main 一致。先创建 [PR #7](https://github.com/wenjiangping/1024-JP/pull/7)，再进行云端同步。


### XBuilder 原项目验收与发布

XBuilder SPX 3.3.0 编译成功。使用独立 `QARank` 临时包，从阈值前一分实际调用收集函数到达五个新分段，系统称号、成就造型及原版橙色结算称号均正确：

| 分数 | 运行插图 | 冻结结算 |
|---|---|---|
| 120 林海追风侠 | [画面](evidence/rank-expansion/qa-120.png) | [画面](evidence/rank-expansion/qa-final-120.png) |
| 140 秘境开拓者 | [画面](evidence/rank-expansion/qa-140.png) | [画面](evidence/rank-expansion/qa-final-140.png) |
| 160 星辉守望者 | [画面](evidence/rank-expansion/qa-160.png) | [画面](evidence/rank-expansion/qa-final-160.png) |
| 180 万木守护神 | [画面](evidence/rank-expansion/qa-180.png) | [画面](evidence/rank-expansion/qa-final-180.png) |
| 200 森林传说王 | [画面](evidence/rank-expansion/qa-200.png) | [画面](evidence/rank-expansion/qa-final-200.png) |

每档结算后将实时积分/称号改为测试值并尝试重复结束，结算仍保留结束时的原值。118 分收集水晶达到 121 分，显示林海追风侠并正确结算：[运行](evidence/rank-expansion/qa-crystal-121.png)、[结算](evidence/rank-expansion/qa-final-121.png)。重开清零、回到蹦跶小新手、清除旧成就；原有 100 分插图保持原样。暂停时成就留在画面，恢复后第 8 档在约 1.99 秒结束显示。所有新档速度为 215.34994，难度因子为 3.71293。[完整日志](evidence/rank-expansion/xbuilder-qa-log.txt)。临时分数为预置验收数据，临时包跳过危险与物理，不作为自然试玩成绩。

恢复正式包后再次编译运行，首页 HomeCover 正常，自然收集 6 个蘑菇后结算为 6 / 蹦跶小新手：[正式结算](evidence/rank-expansion/production-settlement.png)、[日志](evidence/rank-expansion/production-log.txt)。发布前导出核对 37 份脚本逐字节一致且无 QA 标记，全部旧造型、42 份舞台/精灵/声音配置及原素材内容保持原样；两个原生 Monitor、HomeCover 与项目元信息一致。[核对记录](evidence/rank-expansion/cloud-consistency.txt)。

本轮成功发布一次，简短说明为“新增高分称号与成就展示，丰富冒险体验。”：[发布成功](evidence/rank-expansion/publish-success.png)。公开项目刷新后已显示本次发布历史与 HomeCover：[公开页面](evidence/rank-expansion/published-history.png)。公开发布版已进入说明和跑酷，自然收集到 6 分后暂停，系统控件与原有操作正常：[公开版运行](evidence/rank-expansion/published-live.png)。PR #7 保持打开，未合并。


## 分段、危险物和布局调整（2026-11-06）

按用户确认保留最高速度 215.34994；阶段门槛改为 30/60/90/120/150/180/210/260/310/360。用户授权决定高阶段配额，采用阶段 7–10 每可布置路段 3 个障碍，并增加危险路段中的火焰/炸弹数量，未采用每段 6 个或原始密度无上限方案。

右组按钮整体右移 30 像素，左右外边距均为 14；点击区域和编辑配置同时更新。木桩/石堆图片下移 4 像素，碰撞几何不变。炸弹路线从模板 6 扩至 6/8，全阶段翻倍；火焰模板 5/9 保留。高阶段三障碍危险路段显示一个实体和两个同类危险物，间距为 66。障碍槽扩为 15 项，各路段独占三个；全部克隆、清理、渲染、滚动和碰撞循环同步更新。

仓库首页补全页面流程、操作、精确积分公式、分段称号/速度/配额表、危险物、安全路线与工程验证信息。根目录旧 v0.1.8 移到 docs；原 docs 同名稿内容不同，两稿均保留并标注历史。当前机制以仓库 README 为准。

本地生产函数检查通过：451 个积分、20 组蘑菇/水晶跨档、暂停/重复/结束收集、冻结结算、速度封顶和阶段 7 配额变化；22 个边界积分共 44 万次路段再生及 11 万次配额分配，验证槽位归属、数组范围、间距、缺口/开局安全区；逐阶段遍历 10 个模板验证炸弹机会翻倍和高阶段危险物增加。包为 36 精灵/204 文件，打包逐字节与工具语法检查通过。原云端项目已导出备份，37 份 SPX 与 GitHub main 一致。先提 PR，再同步云端；后续补充实际 XBuilder 验收。
