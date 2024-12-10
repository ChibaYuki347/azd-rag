#!/bin/bash

# Get environment variables from azd
eval $(azd env get-values | sed 's/^/export /')

# Azure Storage Account name
STORAGE_ACCOUNT_NAME=$AZURE_STORAGE_ACCOUNT_NAME

# Azure Storage Container name
CONTAINER_NAME=$AZURE_STORAGE_CONTAINER_NAME

# Azure Storage Account key
STORAGE_ACCOUNT_KEY=$AZURE_STORAGE_ACCOUNT_KEY

# Local directory to sync
LOCAL_DIRECTORY="./data/docs"

echo 'uploading files to Azure Blob Storage'

# Sync the local directory to the Azure Blob Storage container
az storage blob upload-batch -d $CONTAINER_NAME --account-name $STORAGE_ACCOUNT_NAME --account-key $STORAGE_ACCOUNT_KEY --source $LOCAL_DIRECTORY --overwrite

echo 'files uploaded to Azure Blob Storage'