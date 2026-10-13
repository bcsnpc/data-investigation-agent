targetScope = 'resourceGroup'

param location string
param postgresLocation string
param computeLocation string
param storageName string
param vaultName string
param postgresName string
param identityName string
param environmentName string
param jobName string
param ownerObjectId string
param ownerPrincipalName string
param ownerIp string
param databaseName string
param deployCompute bool
param deployPostgres bool
param workerImage string

resource worker 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  kind: 'StorageV2'
  sku: { name: 'Standard_LRS' }
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    defaultToOAuthAuthentication: true
    // Owner bootstrap transfers use existing ARM listKeys authority in memory.
    // The worker uses only its scoped managed identity, never this key.
    allowSharedKeyAccess: true
  }
}
resource blob 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storage
  name: 'default'
  properties: {}
}
resource containers 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = [for name in ['snapshots', 'tapes', 'captures', 'screenshots', 'archive']: {
  parent: blob
  name: name
  properties: { publicAccess: 'None' }
}]

resource vault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: vaultName
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: { family: 'A', name: 'standard' }
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    publicNetworkAccess: 'Enabled'
    accessPolicies: []
  }
}

resource blobRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: storage
  name: guid(storage.id, worker.id, 'blob-data-contributor')
  properties: {
    principalId: worker.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  }
}
resource secretsRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: vault
  name: guid(vault.id, worker.id, 'key-vault-secrets-user')
  properties: {
    principalId: worker.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')
  }
}

resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2024-08-01' = if (deployPostgres) {
  name: postgresName
  location: postgresLocation
  sku: { name: 'Standard_B1ms', tier: 'Burstable' }
  properties: {
    version: '16'
    authConfig: {
      activeDirectoryAuth: 'Enabled'
      passwordAuth: 'Disabled'
      tenantId: subscription().tenantId
    }
    storage: { storageSizeGB: 32, type: 'Premium_LRS', autoGrow: 'Disabled' }
    highAvailability: { mode: 'Disabled' }
    backup: { backupRetentionDays: 7, geoRedundantBackup: 'Disabled' }
    network: { publicNetworkAccess: 'Enabled' }
  }
}
resource ownerFirewall 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2024-08-01' = if (deployPostgres) {
  parent: postgres
  name: 'OwnerCurrentIp'
  properties: { startIpAddress: ownerIp, endIpAddress: ownerIp }
}
resource azureFirewall 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2024-08-01' = if (deployPostgres) {
  parent: postgres
  name: 'AllowAzureServices'
  properties: { startIpAddress: '0.0.0.0', endIpAddress: '0.0.0.0' }
}
resource administrator 'Microsoft.DBforPostgreSQL/flexibleServers/administrators@2024-08-01' = if (deployPostgres) {
  parent: postgres
  name: ownerObjectId
  properties: {
    principalName: ownerPrincipalName
    principalType: 'User'
    tenantId: subscription().tenantId
  }
}
resource database 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2024-08-01' = if (deployPostgres) {
  parent: postgres
  name: databaseName
  properties: { charset: 'UTF8', collation: 'en_US.utf8' }
}

resource environment 'Microsoft.App/managedEnvironments@2025-01-01' = if (deployCompute) {
  name: environmentName
  location: computeLocation
  properties: {
    appLogsConfiguration: { destination: 'none' }
    workloadProfiles: [{ name: 'Consumption', workloadProfileType: 'Consumption' }]
    zoneRedundant: false
  }
}
resource job 'Microsoft.App/jobs@2025-01-01' = if (deployCompute) {
  name: jobName
  location: computeLocation
  identity: { type: 'UserAssigned', userAssignedIdentities: { '${worker.id}': {} } }
  properties: {
    environmentId: environment!.id
    workloadProfileName: 'Consumption'
    configuration: {
      triggerType: 'Manual'
      replicaTimeout: 1800
      replicaRetryLimit: 0
      manualTriggerConfig: { parallelism: 1, replicaCompletionCount: 1 }
    }
    template: {
      containers: [{
        name: 'worker'
        image: workerImage
        resources: { cpu: json('0.5'), memory: '1Gi' }
        env: [
          { name: 'AZURE_CLIENT_ID', value: worker.properties.clientId }
          { name: 'DIA_STORAGE_ACCOUNT', value: storage.name }
          { name: 'DIA_KEY_VAULT_URL', value: vault.properties.vaultUri }
          { name: 'INVESTIGATOR_STATE_BACKEND', value: 'postgresql' }
          { name: 'INVESTIGATOR_PG_HOST', value: deployPostgres ? postgres!.properties.fullyQualifiedDomainName : '' }
          { name: 'INVESTIGATOR_PG_DATABASE', value: databaseName }
          { name: 'INVESTIGATOR_PG_USER', value: identityName }
          { name: 'DIA_LIVE_ACCESS_DISABLED', value: '1' }
        ]
      }]
    }
  }
}

output managedIdentityResourceId string = worker.id
output managedIdentityClientId string = worker.properties.clientId
output managedIdentityPrincipalId string = worker.properties.principalId
output storageAccountName string = storage.name
output vaultUri string = vault.properties.vaultUri
output postgresHost string = deployPostgres ? postgres!.properties.fullyQualifiedDomainName : ''
output databaseName string = databaseName
