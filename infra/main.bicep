targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment that can be used as part of naming resource convention')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

// openai resouce model
param embeddingModel string = 'text-embedding-3-large'

// ai services region
@description('Region for the AI Services resource')
@allowed(['eastus','eastus2','northcentralus','swedencentral','westus'])
param aiServicesRegion string = 'eastus2'

// AI Search region
@description('Region for the AI Search resource')
@allowed(['eastus','eastus2','northcentralus','swedencentral','westus'])
param searchRegion string = 'eastus2'


// Generate a unique token to be used in naming resources.
// Remove linter suppression after using.
#disable-next-line no-unused-vars
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))

var abbrs = loadJsonContent('./abbreviations.json')

// Tags that should be applied to all resources.
// 
// Note that 'azd-service-name' tags should be applied separately to service host resources.
// Example usage:
//   tags: union(tags, { 'azd-service-name': <service name in azure.yaml> })
var tags = {
  'azd-env-name': environmentName
}



resource rg 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: 'rg-${environmentName}'
  location: location
  tags: tags
}

// Resouces definitions

// Blob Storage
module storage 'core/storage/storage-account.bicep' = {
  name: 'stroage'
  scope: rg
  params: {
    name: '${abbrs.storageStorageAccounts}${resourceToken}'
    location: location
    tags: tags
    containers: [
      {name: 'docs'}
    ]
    isHnsEnabled: true
  }
}


// AI Search
module search 'core/search/search-services.bicep' = {
  name: 'search'
  scope: rg
  params: {
    name: '${abbrs.searchSearchServices}${resourceToken}'
    location: searchRegion
    tags: tags
    sku: {
      name: 'basic'
    }
  }
}

// AI Services
module aiservices 'core/ai/cognitiveservices-preview.bicep' = {
  name: 'aiservices'
  scope: rg
  params: {
    name: 'aiservices${abbrs.cognitiveServicesAccounts}${resourceToken}'
    location: aiServicesRegion
    kind: 'CognitiveServices'
    tags: tags
    sku: {
      name: 'S0'
    }
  }
}

// Azure OpenAI
module openai 'core/ai/cognitiveservices.bicep' = {
  name: 'openai'
  scope: rg
  params: {
    name: 'aoai${abbrs.cognitiveServicesAccounts}${resourceToken}'
    location: location
    tags: tags
    sku: {
      name: 'S0'
    }
    deployments: [
      {
        name: 'gpt4o'
        model: {
          format: 'OpenAI'
          name: 'gpt-4o'
          version: '2024-08-06'
        }
        sku: {
          name: 'Standard'
          capacity: 8
        }
      }
      {
        name: 'embedding'
        model: {
          format: 'OpenAI'
          name: embeddingModel
        }
      }
    ]
  }
}

// AI Studio Deployment
// Dependent resources for the Azure Machine Learning workspace

var aiHubFriendlyName = 'aihub'

@description('Description of your Azure AI resource dispayed in AI studio')
param aiHubDescription string = 'This is an example AI resource for use in Azure AI Studio.'

module aiDependencies 'core/ai/dependencies-resources.bicep' = {
  name: 'dependencies-${aiHubFriendlyName}-${resourceToken}-deployment'
  scope: rg
  params: {
    location: location
    storageName: 'st${aiHubFriendlyName}${resourceToken}'
    keyvaultName: 'kv-${aiHubFriendlyName}-${resourceToken}'
    applicationInsightsName: 'appi-${aiHubFriendlyName}-${resourceToken}'
    containerRegistryName: 'cr${aiHubFriendlyName}${resourceToken}'
    // aiServicesName: 'ais${aiHubFriendlyName}${resourceToken}'
    tags: tags
  }
}

module aiHub 'core/ai/ai-hub.bicep' = {
  name: 'ai-${aiHubFriendlyName}-${resourceToken}-deployment'
  scope: rg
  params: {
    // workspace organization
    aiHubName: 'aih-${aiHubFriendlyName}-${resourceToken}'
    aiHubFriendlyName: aiHubFriendlyName
    aiHubDescription: aiHubDescription
    location: location
    tags: tags

    // dependent resources
    aiServicesId: openai.outputs.id
    aiServicesTarget: openai.outputs.endpoint
    aiSearchId: search.outputs.id
    aiSearchName: search.outputs.name
    aiSearchTarget: search.outputs.endpoint
    applicationInsightsId: aiDependencies.outputs.applicationInsightsId
    containerRegistryId: aiDependencies.outputs.containerRegistryId
    keyVaultId: aiDependencies.outputs.keyvaultId
    storageAccountId: aiDependencies.outputs.storageId
  }
}

module aiProject 'core/ai/project.bicep' = {
  name: 'ai-project'
  scope: rg
  params: {
    location: location
    displayName: 'AI Project'
    hubName: 'aih-${aiHubFriendlyName}-${resourceToken}'
    keyVaultName: 'kv-${aiHubFriendlyName}-${resourceToken}'
    skuName: 'Basic'
    skuTier: 'Basic'
    name: 'ai-project'
    tags: tags
  }
}


// output parameters

// Storage Outputs
output AZURE_STORAGE_ACCOUNT_NAME string = storage.outputs.name
output AZURE_STORAGE_CONTAINER_NAME string = storage.outputs.containerName
output AZURE_STORAGE_ACCOUNT_KEY string = storage.outputs.storageAccountKey
output AZURE_STORAGE_CONNECTION_STRING string = storage.outputs.storageAccountConnectionString

// AI Search Outputs
output AZURE_SEARCH_ENDPOINT string = search.outputs.endpoint
output AZURE_SEARCH_PRINCIPAL_ID string = search.outputs.principalId
output AZURE_SEARCH_KEY string = search.outputs.primaryKey

// OpenAI Outputs
output AZURE_OPENAI_ENDPOINT string = openai.outputs.endpoint
output AZURE_OPENAI_KEY string = openai.outputs.accountKey
output AZURE_OPENAI_EMBEDDING_MODEL string = embeddingModel

// AI Services Outputs
output AZURE_AISERVICES_KEY string = aiservices.outputs.accountKey
