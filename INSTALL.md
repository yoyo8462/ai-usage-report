# 安裝說明（給 AI 看）：ai-usage-report

> 這份是寫給幫使用者安裝的 AI 看的（Claude Code 或 Codex 都適用）。使用者想安裝 AI 使用能力報告 skill（https://github.com/yoyo8462/ai-usage-report），用來分析他自己在 Claude Code 與 Codex 的對話紀錄。

## 總原則

1. 每一步先用白話說要做什麼，使用者說好才做。
2. 已經有的檔案不覆蓋；`~/ai-usage-report` 或兩個 skills 資料夾裡已經有 `ai-usage-report`，先問：是要更新（`git pull`），還是換掉。
3. 用使用者的語言、用沒學過程式的人也聽得懂的話；一次問 2～3 題，能給選項就給選項。
4. 你能自己做的就自己做，不要叫使用者去點設定、開資料夾、搬檔案。跳出 Windows「是否允許變更」視窗，或你的沙盒要使用者核准指令時，才請使用者按同意。
5. 全部做完列「做了什麼、還沒做什麼」。

## 步驟 1：問用哪些 AI 工具

問使用者平常用哪個：只用 Claude（含桌面 App 的 Code 分頁）／只用 Codex／兩個都用。你自己是哪一個，就至少裝到你自己那邊。

## 步驟 2：確認 Python 與 Git

- Windows：在 PowerShell 跑 `python --version` 和 `git --version`。
  - 沒有 Python，或跳出 Microsoft Store：`winget install -e --id Python.Python.3.12`，裝完請使用者重開 App。
  - 沒有 Git：`winget install -e --id Git.Git`。
- Mac：`python3 --version`、`git --version`（沒有 git 會跳出安裝開發者工具的視窗，請使用者按「安裝」）。

## 步驟 3：下載一份，連到要用的工具

只下載一份，放在家目錄，再從各工具的 skills 資料夾建連結。兩邊用同一份，更新一次兩邊都生效。

Windows（PowerShell）：

```powershell
git clone https://github.com/yoyo8462/ai-usage-report.git "$env:USERPROFILE\ai-usage-report"
# 用 Claude 的話
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\ai-usage-report" -Target "$env:USERPROFILE\ai-usage-report"
# 用 Codex 的話
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
New-Item -ItemType Junction -Path "$env:USERPROFILE\.codex\skills\ai-usage-report" -Target "$env:USERPROFILE\ai-usage-report"
```

（junction 不需要系統管理員權限。建連結失敗就直接複製一份過去，並告訴使用者「以後更新要兩邊都更新」。）

Mac：

```bash
git clone https://github.com/yoyo8462/ai-usage-report.git ~/ai-usage-report
mkdir -p ~/.claude/skills && ln -s ~/ai-usage-report ~/.claude/skills/ai-usage-report   # 用 Claude 的話
mkdir -p ~/.codex/skills && ln -s ~/ai-usage-report ~/.codex/skills/ai-usage-report     # 用 Codex 的話
```

使用者如果有自己的 AI 工作資料夾、習慣把 skill 統一放在那裡（全域 CLAUDE.md 或 AGENTS.md 會寫），可以 clone 到那裡，連結的目標改成那個位置。

## 步驟 4：問私事清單，寫進 config.local.json

用白話說明：「報告會從你的對話裡挑幾則當例子。有些主題你可能不想出現在報告裡，告訴我，我就不會挑那些對話。」

一次問：

- 有沒有哪些主題是私事，不要放進報告？（例如感情、看病、家裡的事、某個嗜好）
- 有沒有哪個資料夾放的都是私人東西？
- 有沒有設定排程讓 AI 自己跑？哪些是私人用途的？

在 skill 資料夾（`~/ai-usage-report`）建 `config.local.json`（不會進 git，之後更新不會被蓋掉），只寫這三個欄位：

```json
{
  "personal_keywords": ["關鍵字1", "關鍵字2"],
  "personal_paths": ["資料夾路徑的一段"],
  "personal_scheduled_tasks": ["排程名稱"]
}
```

寫完用 `python -c "import json;json.load(open(r'<路徑>/config.local.json',encoding='utf-8'));print('OK')"` 確認格式正確（Mac 用 `python3`）。使用者說都沒有，就不用建這個檔。

## 步驟 5：試跑

暫存資料夾：Claude 用這次對話的 scratchpad；Codex 用系統暫存（Windows `$env:TEMP`，Mac `$TMPDIR`）。

Windows：

```powershell
python -I "$env:USERPROFILE\ai-usage-report\scripts\collect.py" --days 7 --no-content --out "$env:TEMP\aiuse-test"
```

Mac：`python3 -I ~/ai-usage-report/scripts/collect.py --days 7 --no-content --out "$TMPDIR/aiuse-test"`

- 印出「證據包完成」和「本人對話 N 則」就是通了。程式會同時讀 Claude 與 Codex 兩邊的紀錄，`metrics.md` 的「多棲」段落看得到各幾則。
- 中文變亂碼或出現 `UnicodeEncodeError`：前面加 `$env:PYTHONUTF8=1;`（PowerShell）再跑一次。
- 本人對話 0 則：確認 `~/.claude/projects/` 或 `~/.codex/sessions/` 底下有沒有東西；剛開始用的話改 `--days 30`。
- 「排程檢查略過」是正常的，代表沒有用 Claude 桌面 App 的排程。
- Codex 沙盒擋住讀取家目錄：請使用者核准這一次執行。
- 測完刪掉測試輸出資料夾。

## 步驟 6：收尾

- 開新對話確認看得到 `ai-usage-report` 這個 skill（Claude 在 skill 清單；Codex 輸入 `$` 或問「你有哪些 skill」）。
- 告訴使用者：
  - 想看報告就說「分析我怎麼用 AI」，建議每個月跑一次；下次會跟這次比。Claude 和 Codex 跑出來的報告讀的是同一批紀錄。
  - 要更新就說「更新 AI 健檢 skill」，你會在 `~/ai-usage-report` 跑 `git pull`；私事清單在 `config.local.json`，不會被蓋掉。
- 問使用者要不要現在就跑第一份。要的話，在新對話裡跑（這個安裝對話已經很長）。
