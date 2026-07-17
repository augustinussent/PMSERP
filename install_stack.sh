#!/bin/bash
# Installation script for Kamra, ERPNext, and Ury ERP on an Ubuntu VPS
# Run this inside your frappe-bench directory!

echo "Starting unified installation of Kamra + ERPNext + Ury..."

# 1. Ensure bench is available
if ! command -v bench &> /dev/null
then
    echo "Frappe bench could not be found. Please install bench first."
    exit 1
fi

# 2. Get the Apps
echo "Pulling ERPNext (Version 15)..."
bench get-app erpnext --branch version-15 https://github.com/frappe/erpnext.git

echo "Pulling Ury ERP..."
bench get-app ury https://github.com/ury-erp/ury.git

echo "Pulling Kamra..."
bench get-app kamra https://github.com/augustinussent/PMSERP.git

# 3. Install the Apps on the Site
# Prompt for site name
read -p "Enter your Frappe site name (e.g. site1.local): " site_name

if [ -z "$site_name" ]; then
    echo "Site name cannot be empty."
    exit 1
fi

echo "Installing ERPNext on $site_name..."
bench --site $site_name install-app erpnext

echo "Installing Ury ERP on $site_name..."
bench --site $site_name install-app ury

echo "Installing Kamra on $site_name..."
bench --site $site_name install-app kamra

# 4. Migrate and Build
echo "Running migrations..."
bench --site $site_name migrate

echo "Building assets..."
bench build

echo "Installation complete! Kamra, ERPNext, and Ury are now running as a unified stack."
