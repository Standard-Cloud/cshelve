locals {
  containers = [
    "compression",
    "dedicated-iter",
    "dedicated-len",
    "del",
    "encryption-and-compression",
    "encryption",
    "flag",
    "flagn",
    "standard",
    "test-account-key",
    "test-connection-string",
  ]
}

resource "azurerm_storage_container" "storage_containers" {
  for_each = toset(local.containers)
  name                  = each.key
  storage_account_id    = azurerm_storage_account.storage.id
  container_access_type = "private"
}
