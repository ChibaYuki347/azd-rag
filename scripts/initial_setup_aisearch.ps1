#!/usr/bin/env pwsh

./scripts/load_python_env.ps1

$venvPythonPath = "./.venv/scripts/python.exe"
if (Test-Path -Path "/usr") {
  # fallback to Linux venv path
  $venvPythonPath = "./.venv/bin/python"
}

Write-Host 'Running "initial_setup_aisearch.py"'

Start-Process -FilePath $venvPythonPath "scripts/initial_setup_aisearch.py" -Wait -NoNewWindow

Write-Host 'set azd variables'

# set azd variable
# azd env set IS_DATASOURCE_SETUP true
# azd env set IS_DOC_INDEX_SETUP true
# azd env set IS_INDEXER_SETUP true
# azd env set IS_SKILLSET_SETUP true
# azd env set IS_FAQ_INDEX_SETUP true
# azd env set IS_FAQ_INDEXER_SETUP true