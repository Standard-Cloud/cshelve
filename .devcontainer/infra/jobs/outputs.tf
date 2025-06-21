# Output values
output "storage_account_name" {
  value = data.azurerm_storage_account.storage.name
}

output "sftp_name" {
  value = azurerm_storage_container.job_sftp.name
}
