terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>  4.34"
    }
  }

  backend "local" {
    path = "terraform.jobs.tfstate"
  }
}
