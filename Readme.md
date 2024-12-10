# Overview

AzureでRAGを構築するための日本語サンプル構成です。

# 構成

Azure Developer CLIを利用してリソース作成やインデックの作成を行います。

# 事前準備

- [Azure Developer CLI](https://learn.microsoft.com/ja-jp/azure/developer/azure-developer-cli/overview?tabs=windows)のインストール

Azure Developer CLIへのログインを行う
```bash
azd auth login
```


- [Azure CLI](https://learn.microsoft.com/ja-jp/cli/azure/install-azure-cli)のインストール

Azure CLIへのログインを行う
```bash
az login
```

- [Python](https://www.python.org/downloads/)のインストール

- Windowsの場合、[Windows Subsystem for Linux](https://docs.microsoft.com/ja-jp/windows/wsl/install)のインストール、もしくは[PowerShell Core](https://learn.microsoft.com/ja-jp/powershell/scripting/install/installing-powershell-on-windows?view=powershell-7.4)をインストールしてください。

- (スクリプトにエラーが出る場合)PowerShellスクリプト、及びShellスクリプトへの実行権限を付与してください。

Shell
```bash
chmod +x ./scripts/sync_to_blob.sh # Shellのパス
```
PowerShell
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Scriptsの一覧は/scripts内に格納されており、
azure.yamlで実行タイミングが定義されています。
下記の例ではhooksとして、Azureのリソースが作成された後に、Blob Storageにファイルをアップロードするスクリプトを実行しています。

posix: Linux、macOS、Windows Subsystem for Linuxで実行されるスクリプト

windows: Windowsで実行されるスクリプト
という形で場合分けされています。

```yaml
hooks:
  postprovision: 
    posix:
      shell: sh
      continueOnError: false
      interactive: true
      run: |
       ./scripts/sync_to_blob.sh
    windows:
      shell: pwsh
      continueOnError: false
      interactive: true
      run: |
       ./scripts/sync_to_blob.ps1
```

[スクリプト一覧](./scripts/Readme.md)についてこちらで詳細を確認できます。
# インフラの作成

```bash
azd provision
```

こちらのコマンドを実行することで、Azure上にリソースが作成されます。




