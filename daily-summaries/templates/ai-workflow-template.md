# 🤖 AI Session Workflow - Turtle Monitor System

## 🎯 Purpose
This template provides a repeatable workflow for AI to:
1. Read the last session summary
2. Generate the next session start summary
3. Present parsed information for user focus selection
4. Execute the chosen focus area

## 📋 AI Workflow Steps

### Step 1: Find and Read Last Session Summary
```bash
# Find the most recent session complete summary
LAST_SESSION=$(find daily-summaries/ -name "*session-complete.md" -o -name "*current-status.md" | sort -r | head -1)

# Read the last session summary
cat "$LAST_SESSION"
```

### Step 2: Generate Next Session Start Summary
```bash
# Create next session start summary
TODAY=$(date +%Y-%m-%d)
cp daily-summaries/templates/session-start-template.md "daily-summaries/$(date +%Y)/$(date +%m)/${TODAY}-session-start.md"

# Fill in the template with current system status
```

### Step 3: Parse and Present Information
Extract and present:
- **Current System Status** (working components, issues)
- **Recent Accomplishments** (what was done last session)
- **Active Issues** (problems that need attention)
- **Next Steps Options** (available focus areas)
- **System Health** (performance metrics)

### Step 4: User Focus Selection
Present focus options and wait for user direction.

---

## 🔄 Repeatable AI Commands

### Find Last Session Summary
```bash
# Find most recent session summary
find daily-summaries/ -name "*.md" | grep -E "(session-complete|current-status)" | sort -r | head -1
```

### Check Current System Status
```bash
# Quick system health check
curl -s http://10.0.20.69/health
curl -s http://10.0.20.69/api/latest
ssh shrimp@10.0.20.69 'systemctl status temperhum-mqtt --no-pager'
```

### Generate Session Start Summary
```bash
# Create today's session start summary
TODAY=$(date +%Y-%m-%d)
YEAR=$(date +%Y)
MONTH=$(date +%m)

# Ensure directory exists
mkdir -p "daily-summaries/${YEAR}/${MONTH}"

# Copy template
cp daily-summaries/templates/session-start-template.md "daily-summaries/${YEAR}/${MONTH}/${TODAY}-session-start.md"
```

### Update System Status Index
```bash
# Update the machine-readable status index
# Edit daily-summaries/index/system-status-index.md with current data
```

---

## 📊 Information Parsing Template

### Current System Status Summary
```
🏥 SYSTEM HEALTH: [Excellent/Good/Warning/Critical]
⏰ UPTIME: [How long system has been running]
📊 PERFORMANCE: [CPU/Memory usage, response times]
🔧 SERVICES: [List of running/stopped services]
```

### Active Issues Summary
```
🐛 CRITICAL ISSUES: [Number and brief description]
⚠️ WARNINGS: [Number and brief description]
✅ RESOLVED: [Issues fixed in last session]
```

### Recent Accomplishments
```
🚀 MAJOR WINS: [Key achievements from last session]
📈 IMPROVEMENTS: [Performance/system improvements]
🔧 FIXES: [Issues resolved]
```

### Available Focus Areas
```
1. 🐛 ISSUE RESOLUTION: [Active problems to fix]
2. 🚀 FEATURE DEVELOPMENT: [New features to implement]
3. 🔧 SYSTEM MAINTENANCE: [Optimization and cleanup]
4. 📊 MONITORING: [Health checks and validation]
5. 📝 DOCUMENTATION: [Update docs and guides]
```

---

## 🎯 User Focus Selection

### Present Options
```
🤖 AI Session Ready - Please Select Focus:

📊 CURRENT STATUS:
- System Health: [Status]
- Active Issues: [Number]
- Recent Wins: [Number]

🎯 AVAILABLE FOCUS AREAS:
1. [Focus Area 1] - [Brief description]
2. [Focus Area 2] - [Brief description]
3. [Focus Area 3] - [Brief description]
4. [Focus Area 4] - [Brief description]
5. [Focus Area 5] - [Brief description]

💡 RECOMMENDED: [Based on current issues/priorities]

Please select your focus area (1-5) or provide specific direction:
```

### Handle User Selection
- **Option 1**: Issue Resolution - Focus on fixing active problems
- **Option 2**: Feature Development - Work on new features
- **Option 3**: System Maintenance - Optimize and clean up
- **Option 4**: Monitoring - Health checks and validation
- **Option 5**: Documentation - Update docs and guides
- **Custom**: User provides specific direction

---

## 🔧 AI Execution Commands

### For Issue Resolution
```bash
# Focus on fixing active issues
grep -r "## 🐛 Current Issues" daily-summaries/2025/08/
# Execute troubleshooting steps
```

### For Feature Development
```bash
# Focus on implementing new features
grep -r "## 🎯 Next Steps" daily-summaries/2025/08/
# Execute development plan
```

### For System Maintenance
```bash
# Focus on optimization and cleanup
ssh shrimp@10.0.20.69 'systemctl status --all'
# Execute maintenance tasks
```

### For Monitoring
```bash
# Focus on health checks and validation
curl -s http://10.0.20.69/health
curl -s http://10.0.20.69/api/latest
# Execute monitoring tasks
```

### For Documentation
```bash
# Focus on updating documentation
find . -name "*.md" -mtime +7
# Execute documentation updates
```

---

## 📝 Session Completion

### Generate Session Complete Summary
```bash
# Create session complete summary
TODAY=$(date +%Y-%m-%d)
cp daily-summaries/templates/session-complete-template.md "daily-summaries/$(date +%Y)/$(date +%m)/${TODAY}-session-complete.md"

# Fill in with session results
```

### Update Indexes
```bash
# Update system status index
# Update progress tracking
# Commit changes to git
```

---

## 🎯 Quick Start Commands

### Full Workflow
```bash
# 1. Find last session
LAST_SESSION=$(find daily-summaries/ -name "*session-complete.md" -o -name "*current-status.md" | sort -r | head -1)

# 2. Read and parse
cat "$LAST_SESSION"

# 3. Generate next session
TODAY=$(date +%Y-%m-%d)
cp daily-summaries/templates/session-start-template.md "daily-summaries/$(date +%Y)/$(date +%m)/${TODAY}-session-start.md"

# 4. Check system status
curl -s http://10.0.20.69/health
curl -s http://10.0.20.69/api/latest

# 5. Present options to user
```

### One-Liner for AI
```bash
# Complete workflow in one command
find daily-summaries/ -name "*session-complete.md" -o -name "*current-status.md" | sort -r | head -1 | xargs cat && echo "=== SYSTEM STATUS ===" && curl -s http://10.0.20.69/health && curl -s http://10.0.20.69/api/latest
```

---

**🤖 This workflow ensures consistent, repeatable session management with clear user direction and comprehensive system understanding.** 