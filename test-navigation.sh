#!/bin/bash

echo "🧭 Testing Enhanced Dashboard Navigation..."

# Test 1: Navigation elements on all pages
echo "📊 Test 1: Navigation Elements"
NAV_COUNT=$(curl -s "http://10.0.20.69/" | grep -c "navigation")
if [ "$NAV_COUNT" -eq 6 ]; then
    echo "✅ Navigation present on all 3 pages (6 total elements)"
else
    echo "❌ Navigation missing on some pages (found $NAV_COUNT elements)"
fi

# Test 2: Nav buttons on all pages
echo "🔘 Test 2: Navigation Buttons"
NAV_BTN_COUNT=$(curl -s "http://10.0.20.69/" | grep -c "nav-btn")
if [ "$NAV_BTN_COUNT" -eq 9 ]; then
    echo "✅ Navigation buttons present on all pages (9 total buttons)"
else
    echo "❌ Navigation buttons missing (found $NAV_BTN_COUNT buttons)"
fi

# Test 3: Page structure
echo "📄 Test 3: Page Structure"
PAGE_COUNT=$(curl -s "http://10.0.20.69/" | grep -c "page.*id=")
if [ "$PAGE_COUNT" -eq 3 ]; then
    echo "✅ All 3 pages present: status-page, camera-page, data-page"
else
    echo "❌ Missing pages (found $PAGE_COUNT pages)"
fi

# Test 4: Active page indicators
echo "🎯 Test 4: Active Page Indicators"
ACTIVE_COUNT=$(curl -s "http://10.0.20.69/" | grep -c "nav-btn active")
if [ "$ACTIVE_COUNT" -eq 3 ]; then
    echo "✅ Active indicators present on all pages (3 total)"
else
    echo "❌ Active indicators missing (found $ACTIVE_COUNT indicators)"
fi

echo ""
echo "🎉 Navigation Test Complete!"
echo ""
echo "📋 Navigation Features:"
echo "   • Global navigation on all 3 pages"
echo "   • STATUS, CAMERA, DATA buttons"
echo "   • Active page highlighting"
echo "   • Touch gesture support"
echo "   • Smooth page transitions"
echo ""
echo "🌐 Test the navigation at: http://10.0.20.69/"
echo "   You should now be able to navigate between all pages!" 