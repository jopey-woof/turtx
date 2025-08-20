#!/bin/bash

# 🐢 TEMPerHUM Fresh Cleanup Script
# This script removes ALL previous TEMPerHUM sensor work from the repository
# and prepares for a completely fresh implementation

set -e

echo "🐢 TEMPerHUM Fresh Cleanup - Removing ALL previous sensor work"
echo "================================================================"

# Remove all TEMPerHUM related files from repository
echo "🧹 Cleaning repository files..."

# Remove hardware files
rm -f hardware/temperhum_manager.py
rm -f hardware/temperhum-manager.service
rm -f hardware/99-temperhum.rules
rm -rf hardware/sensors/

# Remove setup files
rm -f setup/cleanup-temperhum.sh
rm -f setup/cleanup-temperhum-legacy.sh
rm -f setup/install-temperhum.sh
rm -f setup/deploy-temperhum.sh
rm -f setup/test-temperhum-manager.sh
rm -f setup/debug-temperhum-verbose.sh

# Remove all test files
rm -f setup/test-*.py
rm -f setup/test-*.sh

# Remove documentation files
rm -f docs/TEMPERHUM-IMPLEMENTATION.md
rm -f docs/TEMPERHUM-INTEGRATION-STATUS.md
rm -f TEMPERHUM_FRESH_IMPLEMENTATION_SUMMARY.md

# Remove any custom components
rm -rf homeassistant/custom_components/temperhum_custom/

# Update README to remove TEMPerHUM references
echo "📝 Updating README..."
sed -i '/TEMPerHUM/d' README.md
sed -i '/temperature.*humidity.*sensor/d' README.md

# Clean up environment template
if [ -f environment.template ]; then
    sed -i '/Temperature\/Humidity Sensor/d' environment.template
fi

# Git cleanup
echo "📦 Git cleanup..."
git add -A
git commit -m "🐢 Cleanup: Remove all previous TEMPerHUM sensor work for fresh implementation" || true

echo ""
echo "✅ Local repository cleanup completed!"
echo ""
echo "🖥️  Remote cleanup commands (run on remote machine):"
echo "ssh shrimp@10.0.20.69"
echo "sudo systemctl stop temperhum-manager.service 2>/dev/null || true"
echo "sudo systemctl disable temperhum-manager.service 2>/dev/null || true"
echo "sudo rm -f /etc/systemd/system/temperhum-manager.service"
echo "sudo rm -f /etc/udev/rules.d/99-temperhum.rules"
echo "sudo rm -f /var/log/temperhum-manager.log"
echo "sudo systemctl daemon-reload"
echo "mosquitto_pub -t 'turtle/sensors/temperhum/status' -m 'CLEANUP' -r 2>/dev/null || true"
echo ""
echo "🎯 Next steps:"
echo "1. Run the remote cleanup commands above"
echo "2. Create fresh implementation following the new specifications"
echo "3. Test the new implementation thoroughly"
echo ""
echo "🔍 Verification commands:"
echo "  git status"
echo "  find . -name '*temperhum*' -o -name '*TEMPerHUM*'" 