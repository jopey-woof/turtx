#!/bin/bash

# 🧹 TEMPerHUM Cleanup Script
# Removes all previous TEMPerHUM sensor work for fresh implementation

set -e

echo "🐢 TEMPerHUM Cleanup - Fresh Start Required"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Confirm cleanup
echo "This script will remove ALL previous TEMPerHUM sensor work:"
echo "  - Custom Home Assistant integration"
echo "  - All debug and test scripts"
echo "  - Status documentation files"
echo "  - Udev rules"
echo "  - Sensor configurations"
echo ""
read -p "Are you sure you want to proceed? (yes/no): " confirm

if [[ $confirm != "yes" ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

print_status "Starting TEMPerHUM cleanup..."

# 1. Remove status documentation files
print_status "Removing status documentation files..."
rm -f TEMPERHUM_WIN_STATUS.md
rm -f TEMPERHUM_INTEGRATION_FINAL_STATUS.md
rm -f TEMPERHUM_INTEGRATION_STATUS.md
rm -f UPON_YOUR_RETURN_CURRENT_STATUS.md
rm -f docs/TEMPerHUM-INTEGRATION-STATUS.md

# 2. Remove custom Home Assistant integration
print_status "Removing custom Home Assistant integration..."
rm -rf homeassistant/custom_components/temperhum_custom/

# 3. Remove all debug and test scripts
print_status "Removing debug and test scripts..."
rm -f setup/debug-temperhum-*.sh
rm -f setup/test-temperhum-*.sh
rm -f setup/install-temperhum-udev.sh

# 4. Remove udev rules
print_status "Removing udev rules..."
rm -f hardware/99-temperhum.rules

# 5. Remove sensor configurations from Home Assistant
print_status "Cleaning Home Assistant sensor configurations..."
# Remove TEMPerHUM platform from sensors.yaml
if [ -f homeassistant/sensors.yaml ]; then
    # Create backup
    cp homeassistant/sensors.yaml homeassistant/sensors.yaml.backup
    # Remove TEMPerHUM platform section
    sed -i '/# TEMPerHUM USB Sensors/,/^$/d' homeassistant/sensors.yaml
    sed -i '/- platform: temperhum_custom/d' homeassistant/sensors.yaml
fi

# 6. Remove Docker HID device mappings
print_status "Cleaning Docker configuration..."
if [ -f docker/docker-compose.yml ]; then
    # Create backup
    cp docker/docker-compose.yml docker/docker-compose.yml.backup
    # Remove TEMPerHUM HID device mappings
    sed -i '/# TEMPerHUM HID devices/,/^$/d' docker/docker-compose.yml
fi

# 7. Remove any remaining TEMPerHUM references from README
print_status "Updating README to remove TEMPerHUM references..."
if [ -f README.md ]; then
    # Create backup
    cp README.md README.md.backup
    # Remove TEMPerHUM completion status
    sed -i 's/- \[x\] TEMPerHUM temperature\/humidity sensor ✅ \*\*COMPLETED\*\*/- [ ] TEMPerHUM temperature\/humidity sensor/g' README.md
    # Remove TEMPerHUM from hardware specs
    sed -i 's/- \*\*Sensors\*\*: TEMPerHUM USB (temperature \& humidity)/- \*\*Sensors\*\*: TEMPerHUM USB (temperature \& humidity) - \*\*PENDING\*\*/g' README.md
fi

# 8. Remove any large binary files that might be related
print_status "Removing large binary files..."
rm -f usb.core
rm -f libusb1

# 9. Clean up any Python cache files
print_status "Cleaning Python cache files..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# 10. Remove simple keyboard toggle script
print_status "Removing keyboard toggle script..."
rm -f simple-keyboard-toggle.py

print_status "Cleanup completed successfully!"
echo ""
echo "📋 Cleanup Summary:"
echo "  ✅ Removed all TEMPerHUM status documentation"
echo "  ✅ Removed custom Home Assistant integration"
echo "  ✅ Removed all debug and test scripts"
echo "  ✅ Removed udev rules"
echo "  ✅ Cleaned Home Assistant configurations"
echo "  ✅ Cleaned Docker configurations"
echo "  ✅ Updated README"
echo "  ✅ Removed binary files"
echo "  ✅ Cleaned Python cache"
echo ""
echo "🔄 Repository is now ready for fresh TEMPerHUM implementation"
echo ""
echo "📝 Next steps:"
echo "  1. Commit these changes to Git"
echo "  2. Push to GitHub to clean remote repository"
echo "  3. Begin fresh TEMPerHUM implementation"
echo ""
echo "💡 To commit these changes:"
echo "  git add -A"
echo "  git commit -m '🧹 Clean TEMPerHUM: Remove all previous sensor work for fresh implementation'"
echo "  git push origin main" 