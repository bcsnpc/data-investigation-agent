targetScope = 'subscription'

param location string = 'eastus'
param resourceGroupName string
param storageName string
param vaultName string
param postgresName string
param identityName string
param environmentName string
param jobName string
param ownerObjectId string
param ownerPrincipalName string
param ownerIp string
param databaseName string = 'investigator'
param deployCompute bool = false
param workerImage string = ''

resource group 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
}

module platform './platform.bicep' = {
  name: 'platform-foundation'
  scope: group
  params: {
    location: location
    storageName: storageName
    vaultName: vaultName
    postgresName: postgresName
    identityName: identityName
    environmentName: environmentName
    jobName: jobName
    ownerObjectId: ownerObjectId
    ownerPrincipalName: ownerPrincipalName
    ownerIp: ownerIp
    databaseName: databaseName
    deployCompute: deployCompute
    workerImage: workerImage
  }
}

output platformOutputs object = platform.outputs
