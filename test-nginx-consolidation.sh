#!/bin/bash

# Test script for Nginx consolidation of turtle dashboard
# This verifies that the dashboard and API are working through Nginx

set -e

echo "🐢 Testing Nginx Consolidation"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_pattern="$3"
    
    echo -e "\n${BLUE}Testing: ${test_name}${NC}"
    
    if eval "$test_command" | grep -q "$expected_pattern"; then
        echo -e "  ${GREEN}✅ PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "  ${RED}❌ FAIL${NC}"
        echo "  Command: $test_command"
        echo "  Expected pattern: $expected_pattern"
        ((TESTS_FAILED++))
    fi
}

# Test 1: Health check endpoint
run_test "Health Check" \
    "curl -s http://localhost/health" \
    "healthy"

# Test 2: Dashboard loads
run_test "Dashboard HTML" \
    "curl -s http://localhost/ | head -5" \
    "Turtle Habitat Monitor"

# Test 3: API proxy works
run_test "API Proxy" \
    "curl -s http://localhost/api/latest" \
    "temperature"

# Test 4: API returns valid JSON
run_test "API JSON Format" \
    "curl -s http://localhost/api/latest | jq -e '.readings' >/dev/null 2>&1" \
    ""

# Test 5: Static assets are accessible
run_test "CSS Files" \
    "curl -s -I http://localhost/css/style.css | head -1" \
    "200"

# Test 6: JavaScript files are accessible
run_test "JS Files" \
    "curl -s -I http://localhost/js/app.js | head -1" \
    "200"

# Test 7: Port 8080 is no longer in use
run_test "Port 8080 Closed" \
    "! ss -tlnp | grep -q ':8080'" \
    ""

# Test 8: Port 8000 is still running (API)
run_test "Port 8000 Running" \
    "ss -tlnp | grep -q ':8000'" \
    ""

# Test 9: Nginx is serving the site
run_test "Nginx Serving" \
    "curl -s -I http://localhost/ | grep -i 'server: nginx'" \
    "nginx"

# Test 10: CORS headers for API
run_test "CORS Headers" \
    "curl -s -I http://localhost/api/latest | grep -i 'access-control'" \
    "Access-Control"

echo -e "\n${BLUE}Test Summary${NC}"
echo "============="
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! Nginx consolidation is working correctly.${NC}"
    echo -e "\n${BLUE}Access your dashboard at:${NC}"
    echo -e "  ${YELLOW}http://10.0.20.69/${NC}"
    echo -e "\n${BLUE}API endpoint:${NC}"
    echo -e "  ${YELLOW}http://10.0.20.69/api/latest${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Please check the configuration.${NC}"
    exit 1
fi 