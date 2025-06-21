# Output values
output "storage_account_name" {
  value = data.azurerm_storage_account.storage.name
}

output "sftp_name" {
  value = azurerm_storage_container.job_sftp.name
}

output "storage_account_primary_connection_string" {
  value     = data.azurerm_storage_account.storage.primary_connection_string
  sensitive = true
}
