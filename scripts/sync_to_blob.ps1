# Get environment variables from azd
$envVars = azd env get-values

# Set each environment variable
foreach ($envVar in $envVars) {
    if ($envVar -match '^(.*?)=(.*)$') {
        $name = $matches[1]
        $value = $matches[2]
        Set-Item -Path "Env:$name" -Value $value
    }
}

# Azure Storage Account name
$STORAGE_ACCOUNT_NAME = $env:AZURE_STORAGE_ACCOUNT_NAME

# Azure Storage Container name
$CONTAINER_NAME = $env:AZURE_STORAGE_CONTAINER_NAME

# Azure Storage Account key
$STORAGE_ACCOUNT_KEY = $env:AZURE_STORAGE_ACCOUNT_KEY

# Local directory to sync
$LOCAL_DIRECTORY = "./data/docs"

# Sync the local directory to the Azure Blob Storage container
az storage blob upload-batch -d $CONTAINER_NAME --account-name $STORAGE_ACCOUNT_NAME --account-key $STORAGE_ACCOUNT_KEY --source $LOCAL_DIRECTORY --overwrite