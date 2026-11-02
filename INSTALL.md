# 給 Claude 的安裝說明：ai-usage-report

> 這份是寫給 Claude 看的。使用者想安裝 AI 使用能力報告 skill（https://github.com/yoyo8462/ai-usage-report），用來分析他自己的 Claude Code 對話紀錄。

## 總原則

1. 每一步先用白話說要做什麼，使用者說好才做。
2. 已經有的檔案不覆蓋；`.claude\skills\ai-usage-report` 已存在就先問：是要更新（`git pull`），還是換掉。
3. 用使用者的語言、用沒學過程式的人也聽得懂的話；一次問 2～3 題，能給選項就給選項。
4. 你能自己做的就自己做，不要叫使用者去點設定、開資料夾、搬檔案。跳出 Windows「是否允許變更」視窗時，才請使用者按「是」。
5. 全部做完列「做了什麼、還沒做什麼」。

## 步驟 1：確認 Python 與 Git

- Windows：在 PowerShell 跑 `python --version` 和 `git --version`。
  - 沒有 Python，或跳出 Microsoft Store：`winget install -e --id Python.Python.3.12`，裝完請使用者重開 Claude App。
  - 沒有 Git：`winget install -e --id Git.Git`。
- Mac：`python3 --version`、`git --version`（沒有 git 會跳出安裝開發者工具的視窗，請使用者按「安裝」）。

## 步驟 2：下載 skill

- Windows：`git clone https://github.com/yoyo8462/ai-usage-report.git "$env:USERPROFILE\.claude\skills\ai-usage-report"`（`.claude\skills` 不存在就先建）
- Mac：`git clone https://github.com/yoyo8462/ai-usage-report.git ~/.claude/skills/ai-usage-report`

使用者如果有自己的 AI 工作資料夾、習慣把 skill 放在那裡統一管理（全域 CLAUDE.md 會寫），可以 clone 到那裡，再從 `.claude\skills\ai-usage-report` 建連結：Windows 用 `New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\ai-usage-report" -Target "<實際位置>"`（不需要系統管理員權限），Mac 用 `ln -s`。

## 步驟 3：問私事清單，寫進 config.local.json

用白話說明：「報告會從你的對話裡挑幾則當例子。有些主題你可能不想出現在報告裡，告訴我，我就不會挑那些對話。」

一次問：

- 有沒有哪些主題是私事，不要放進報告？（例如感情、看病、家裡的事、某個嗜好）
- 有沒有哪個資料夾放的都是私人東西？
- 有沒有設定排程讓 Claude 自己跑？哪些是私人用途的？

在 skill 資料夾建 `config.local.json`（不會進 git，之後更新不會被蓋掉），只寫這三個欄位：

```json
{
  "personal_keywords": ["關鍵字1", "關鍵字2"],
  "personal_paths": ["資料夾路徑的一段"],
  "personal_scheduled_tasks": ["排程名稱"]
}
```

寫完用 `python -c "import json;json.load(open(r'<路徑>\config.local.json',encoding='utf-8'));print('OK')"` 確認格式正確（Mac 用 `python3`）。使用者說都沒有，就不用建這個檔。

## 步驟 4：試跑

Windows：

```
python -I "$env:USERPROFILE\.claude\skills\ai-usage-report\scripts\collect.py" --days 7 --no-content --out "<你的 scratchpad>\aiuse-test"
```

Mac：`python3 -I ~/.claude/skills/ai-usage-report/scripts/collect.py --days 7 --no-content --out <scratchpad>/aiuse-test`

- 印出「證據包完成」和「本人對話 N 則」就是通了。
- 中文變亂碼或出現 `UnicodeEncodeError`：前面加 `$env:PYTHONUTF8=1;`（PowerShell）再跑一次。
- 本人對話 0 則：確認 `.claude\projects\` 底下有沒有東西；剛開始用的話改 `--days 30`。
- 「排程檢查略過」是正常的，代表沒有用排程。
- 測完刪掉測試輸出資料夾。

## 步驟 5：收尾

- 開新對話確認 skill 清單裡看得到 `ai-usage-report`。
- 告訴使用者：
  - 想看報告就說「分析我怎麼用 AI」，建議每個月跑一次；下次會跟這次比。
  - 要更新就說「更新 AI 健檢 skill」，你會在 skill 資料夾跑 `git pull`；私事清單在 `config.local.json`，不會被蓋掉。
- 問使用者要不要現在就跑第一份。要的話，在新對話裡跑（這個安裝對話已經很長）。
