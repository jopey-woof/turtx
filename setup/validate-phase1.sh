#!/bin/bash

# Turtle Monitoring System - Phase 1 Validation Script
# Run this to verify Phase 1 deployment is successful
# Usage: ./setup/validate-phase1.sh

set -e

echo "🐢 Turtle Monitoring System - Phase 1 Validation"
echo "================================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check service status
check_service() {
    local service_name=$1
    if systemctl is-active --quiet "$service_name"; then
        echo -e "✅ ${GREEN}$service_name is running${NC}"
        return 0
    else
        echo -e "❌ ${RED}$service_name is not running${NC}"
        return 1
    fi
}

# Function to check URL accessibility
check_url() {
    local url=$1
    local description=$2
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|302"; then
        echo -e "✅ ${GREEN}$description accessible${NC}"
        return 0
    else
        echo -e "❌ ${RED}$description not accessible${NC}"
        return 1
    fi
}

# Function to check file exists
check_file() {
    local file_path=$1
    local description=$2
    if [ -f "$file_path" ]; then
        echo -e "✅ ${GREEN}$description exists${NC}"
        return 0
    else
        echo -e "❌ ${RED}$description missing${NC}"
        return 1
    fi
}

# Function to check Docker container
check_container() {
    local container_name=$1
    if docker ps | grep -q "$container_name"; then
        echo -e "✅ ${GREEN}$container_name container running${NC}"
        return 0
    else
        echo -e "❌ ${RED}$container_name container not running${NC}"
        return 1
    fi
}

echo "🔍 Running Phase 1 validation checks..."
echo ""

# Track validation results
validation_errors=0

# Check 1: Prerequisites
echo "1️⃣ Checking Prerequisites..."
if ! command -v docker >/dev/null 2>&1; then
    echo -e "❌ ${RED}Docker not installed${NC}"
    ((validation_errors++))
else
    echo -e "✅ ${GREEN}Docker installed: $(docker --version | cut -d' ' -f3)${NC}"
fi

if ! command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then
    echo -e "❌ ${RED}Docker Compose not installed${NC}"
    ((validation_errors++))
else
    echo -e "✅ ${GREEN}Docker Compose installed${NC}"
fi

echo ""

# Check 2: Configuration Files
echo "2️⃣ Checking Configuration Files..."
check_file ".env" "Environment file" || ((validation_errors++))
check_file "docker/docker-compose.yml" "Docker Compose config" || ((validation_errors++))
check_file "homeassistant/configuration.yaml" "Home Assistant config" || ((validation_errors++))

echo ""

# Check 3: Docker Containers
echo "3️⃣ Checking Docker Containers..."
check_container "homeassistant" || ((validation_errors++))

echo ""

# Check 4: Services
echo "4️⃣ Checking System Services..."
check_service "docker" || ((validation_errors++))

# Check kiosk service (may not be started yet)
if systemctl list-unit-files | grep -q "kiosk.service"; then
    echo -e "✅ ${GREEN}Kiosk service configured${NC}"
    if systemctl is-active --quiet "kiosk.service"; then
        echo -e "✅ ${GREEN}Kiosk service running${NC}"
    else
        echo -e "⚠️  ${YELLOW}Kiosk service configured but not running${NC}"
    fi
else
    echo -e "❌ ${RED}Kiosk service not configured${NC}"
    ((validation_errors++))
fi

echo ""

# Check 5: Network Accessibility
echo "5️⃣ Checking Network Accessibility..."
check_url "http://localhost:8123" "Home Assistant" || ((validation_errors++))

echo ""

# Check 6: Display Configuration
echo "6️⃣ Checking Display Configuration..."
if [ -n "$DISPLAY" ]; then
    echo -e "✅ ${GREEN}DISPLAY variable set: $DISPLAY${NC}"
else
    echo -e "⚠️  ${YELLOW}DISPLAY variable not set${NC}"
fi

if command -v xinput >/dev/null 2>&1; then
    echo -e "✅ ${GREEN}X11 input tools installed${NC}"
else
    echo -e "❌ ${RED}X11 input tools not installed${NC}"
    ((validation_errors++))
fi

if command -v chromium-browser >/dev/null 2>&1; then
    echo -e "✅ ${GREEN}Chromium browser installed${NC}"
else
    echo -e "❌ ${RED}Chromium browser not installed${NC}"
    ((validation_errors++))
fi

echo ""

# Check 7: Home Assistant Health
echo "7️⃣ Checking Home Assistant Health..."
if curl -s http://localhost:8123 > /dev/null; then
    echo -e "✅ ${GREEN}Home Assistant responding${NC}"
    
    # Check if we can access the API (basic check)
    if curl -s http://localhost:8123/api/ | grep -q "API running"; then
        echo -e "✅ ${GREEN}Home Assistant API accessible${NC}"
    else
        echo -e "⚠️  ${YELLOW}Home Assistant API may need authentication${NC}"
    fi
else
    echo -e "❌ ${RED}Home Assistant not responding${NC}"
    ((validation_errors++))
fi

echo ""

# Final Results
echo "📊 Validation Summary"
echo "===================="

if [ $validation_errors -eq 0 ]; then
    echo -e "🎉 ${GREEN}Phase 1 validation PASSED!${NC}"
    echo ""
    echo "✅ All core components are working correctly"
    echo "✅ Ready for Phase 1 testing and validation"
    echo ""
    echo "📋 Next steps:"
    echo "1. Test kiosk mode: sudo systemctl start kiosk.service"
    echo "2. Test touchscreen functionality"
    echo "3. Test Home Assistant interface via touch"
    echo "4. Run system for 48+ hours for stability testing"
    echo "5. Complete full validation checklist in docs/PHASE1-DEPLOYMENT.md"
    echo ""
    echo "⚠️  Do NOT proceed to Phase 2 until all validation steps pass"
    exit 0
else
    echo -e "❌ ${RED}Phase 1 validation FAILED${NC}"
    echo ""
    echo -e "${RED}Found $validation_errors error(s) that must be fixed${NC}"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "1. Check service logs: sudo journalctl -u docker.service"
    echo "2. Check Home Assistant logs: docker-compose logs homeassistant"
    echo "3. Verify .env file has correct values"
    echo "4. Try running bootstrap again: ./setup/bootstrap.sh"
    echo ""
    echo "📖 See docs/PHASE1-DEPLOYMENT.md for detailed troubleshooting"
    exit 1
fi