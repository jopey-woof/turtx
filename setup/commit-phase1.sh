#!/bin/bash

# Commit Phase 1 TemperhUM Sensor Integration

echo "🐢 Committing Phase 1 TemperhUM Sensor Integration..."

# Add all Phase 1 files
git add hardware/temperhum_controller.py
git add hardware/temperhum_phase1.py
git add hardware/temperhum_phase1_v2.py
git add hardware/temperhum_phase1_simple.py
git add hardware/requirements.txt
git add hardware/99-temperhum-sensors.rules
git add hardware/PHASE1_SUMMARY.md
git add setup/cleanup-temperhum.sh
git add setup/commit-phase1.sh

# Commit with descriptive message
git commit -m "Phase 1: TemperhUM Sensor Integration - Core Control

✅ Sensor Detection: Successfully detect 2 TemperhUM sensors
✅ Programmatic Control: Linux HID control via evdev
✅ Multi-Sensor Support: Individual sensor management
✅ Activation System: Caps Lock commands working
✅ Development Environment: Virtual env with dependencies
✅ Udev Rules: Non-root sensor access configured

- temperhum_controller.py: Full-featured controller
- temperhum_phase1*.py: Multiple implementation approaches
- requirements.txt: Python dependencies
- 99-temperhum-sensors.rules: Udev rules for access
- PHASE1_SUMMARY.md: Complete documentation

Ready for Phase 2: Interval Adjustment per Sensor"

echo "✅ Phase 1 committed successfully!"
echo ""
echo "Next steps:"
echo "1. Proceed to Phase 2: Interval Adjustment"
echo "2. Implement double-press commands for interval configuration"
echo "3. Set up unified data stream for both sensors" 