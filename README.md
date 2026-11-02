# AI 健檢報告（ai-usage-report）

讓你的 Claude 讀你自己電腦上跟它的對話紀錄，寫一份「你是怎麼用 AI 的」報告：

- 你用 AI 用到第幾級（LV0～LV5，從「一問一答」到「讓它每天自己跑」）
- 你是 16 種使用風格裡的哪一型
- 你哪裡用得好、哪裡可以改，下一步先做哪一件
- 下次再跑，會跟這次比哪裡變了

報告是一份單檔 HTML，只存在你自己的電腦。

## 安裝

打開 Claude 桌面 App 的 Code 分頁（或 Claude Code），貼上這段話：

```text
請幫我安裝這個 skill：https://github.com/yoyo8462/ai-usage-report
先讀 repo 裡的 INSTALL.md，照步驟做。每一步先跟我說要做什麼，我說好再做。
```

裝好之後跟 Claude 說「分析我怎麼用 AI」，就會產出報告。之後要更新，說「更新 AI 健檢 skill」。

自己動手裝（Windows PowerShell）：

```powershell
git clone https://github.com/yoyo8462/ai-usage-report.git "$env:USERPROFILE\.claude\skills\ai-usage-report"
```

Mac／Linux：

```bash
git clone https://github.com/yoyo8462/ai-usage-report.git ~/.claude/skills/ai-usage-report
```

需要 Python 3（Windows 指令是 `python`，Mac 是 `python3`）。

## 先知道的事

- 只讀這台電腦上 Claude Code 的對話（含桌面 App 的 Code 分頁），也讀得到 Codex。網頁版 Claude、ChatGPT、手機 App 的對話讀不到。
- 全部在你的電腦上跑，不上傳任何東西。要把報告給別人看之前，先自己看一遍，裡面可能有你打過的原句。
- 安裝時 Claude 會問你哪些主題是私事，存在 `config.local.json`，那些對話不會被挑成案例；這個檔不進 git，更新時不會被蓋掉。
- 用不到一個月、對話很少的話，報告會很短，這是正常的。
- 等級和風格不是分數，也不是考績；這個 skill 刻意不做排名。

## 跟原版的差別

改自 Raymond Hou（雷蒙三十）的開源專案 [ai-level-check](https://github.com/Raymondhou0917/ai-level-check)（MIT，以 commit `d262ca6` 為底）。判準文件（`references/`）與報告版型沿用原版，收集程式改了這些：

| 原版的狀況 | 這版的做法 |
|---|---|
| 用「從哪裡啟動」判斷人或機器，桌面 App 排程跑的對話入口跟手動開的一樣，會全部算成本人 | 第一則訊息是 `<scheduled-task …>` 的算「排程自動執行」；跑完後本人接著打的字另計 |
| 只讀 `projects/` 第一層，子代理的紀錄（`subagents/`）整批漏掉 | 讀進子代理 |
| 從別的 AI 對話叫起來的 `codex exec` 被標成使用者發起，算成本人 | 算成「AI 驅動 agent」 |
| 沒有檢查排程有沒有照時間跑 | 比對桌面 App 的 cron 設定與實際執行紀錄，列出哪天哪個沒跑（`scripts/check_schedule_runs.py`，也能單獨跑） |
| 第⑤顆齒輪（守護與心跳）會把對話裡的 `Monitor` 工具算進去 | 不算 |
| 私人對話可能被抽成案例 | 依 `config.local.json` 的私事清單排除 |
| — | 報告開頭和上一次比較（`報告紀錄.json`） |
| 部分寫法只在 Mac 能跑 | Windows 與 Mac 都能跑（排程設定位置、日期格式、主控台編碼） |

## 授權

MIT，見 [LICENSE](LICENSE)。原作者版權聲明保留。
