# PUSH-TO-GITHUB.md

> 临时手册：本地 git 仓库已经就绪，但 GitHub 远端仓库还没创建，
> 也没法在当前 agent session 里替你认证。把下面 3 步走完，代码就上 GitHub 了。
> 推送成功后可以删掉本文件。

## 当前状态（agent 已完成）

- ✅ `git init -b main`
- ✅ 本地 `user.name` / `user.email` 已配（仅作用于本仓库）：
    - `wen001-git`
    - `wen001-git@users.noreply.github.com`
- ✅ Initial commit：`2d6a1d1`，155 files，~500 KiB pack
- ✅ Remote 已设置：
    - `origin → https://github.com/wen001-git/PrefectFlow-Whitebox.git`
- ❌ GitHub 上 `wen001-git/PrefectFlow-Whitebox` 仓库**尚未创建**
- ❌ 还未推送任何 commit

## Step 1：在 GitHub 网页上创建空仓库

打开：<https://github.com/new>

填：

- **Owner**：`wen001-git`
- **Repository name**：`PrefectFlow-Whitebox`
- **Description**（可选）：`Reverse-engineering documentation for the Prefect remit-validation flow (whitebox).`
- **Public / Private**：自己选
- ⚠️ **不要**勾 "Add a README"、"Add .gitignore"、"Add license" —— 必须**空仓库**
  （否则推送会冲突）

点 **Create repository**。

## Step 2：推送

回到本机这个目录执行：

```powershell
cd C:\Users\jli\MyData\Copilot\PrefectFlow-Whitebox
git push -u origin main
```

第一次推送会弹出 Git Credential Manager 的浏览器登录窗口，按提示用 GitHub 帐号
登录授权即可（之后凭据缓存，不会再弹）。

如果使用 SSH 更习惯，先把 remote 换成 SSH：

```powershell
git remote set-url origin git@github.com:wen001-git/PrefectFlow-Whitebox.git
git push -u origin main
```

## Step 3：验收

```powershell
git log --oneline -3
git remote -v
git branch -vv     # 应看到 main 跟踪 origin/main
```

打开 <https://github.com/wen001-git/PrefectFlow-Whitebox> 应能看到所有
155 个文件。

## 之后的工作流（建议）

- 每次 agent session 结尾：`git add -A; git commit -m "..."; git push`
- 在 commit message 末尾保留：
  `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`
- `prompts-log.md`（如果以后启用）每个 session 末追加、随 commit 一起推。

## 故障排查

| 现象 | 原因 / 修复 |
|---|---|
| `remote: Repository not found.` | Step 1 还没做，或仓库名 / owner 拼错 |
| `Updates were rejected because the remote contains work that you do not have locally` | Step 1 时勾了 README/.gitignore/license。删掉远端仓库重建为空仓库，或 `git pull --rebase origin main --allow-unrelated-histories` 后再 push |
| 一直卡在 credential 弹窗 | 装 / 升级 [Git Credential Manager](https://github.com/git-ecosystem/git-credential-manager) 或改用 SSH |
| 想换仓库名 | `git remote set-url origin https://github.com/wen001-git/<NEW-NAME>.git` |
