# 🤖 AI Instructions for Daily Summaries

## Quick Reference for AI

### When Reading Summaries
1. **Find Current Status**: Look for `## ✅ Current System Status`
2. **Find Issues**: Look for `## 🐛 Current Issues` or `### Issues/Challenges`
3. **Find Next Steps**: Look for `## 🎯 Next Steps` or `### Immediate Priorities`
4. **Find Technical Details**: Look for `## 🔧 Technical Details`
5. **Find File Changes**: Look for `### Files Modified`

### When Generating Summaries
1. **Use Template**: Copy appropriate template file
2. **Fill Metadata**: Include date, session type, duration, AI-generated flag
3. **Be Specific**: Use exact file paths, commands, technical details
4. **Follow Structure**: Maintain exact section headers and formatting
5. **Link References**: Include links to related documentation

## AI Commands for Summary Management

### Before Starting Work (Session Start)
```bash
# Generate session start summary
cp daily-summaries/templates/session-start-template.md daily-summaries/2025/08/$(date +%Y-%m-%d)-session-start.md

# Read most recent session complete summary
ls -t daily-summaries/2025/08/*session-complete.md | head -1 | xargs cat

# Check current system status
curl -s http://10.0.20.69/health
curl -s http://10.0.20.69/api/latest
```

### After Finishing Work (Session Complete)
```bash
# Generate session complete summary
cp daily-summaries/templates/session-complete-template.md daily-summaries/2025/08/$(date +%Y-%m-%d)-session-complete.md

# Update system status index
# Edit daily-summaries/index/system-status-index.md

# Commit changes
git add daily-summaries/
git commit -m "Update daily summaries - $(date +%Y-%m-%d)"
```

### When Searching for Information
```bash
# Find current system status
grep -r "## ✅ Current System Status" daily-summaries/2025/08/

# Find current issues
grep -r "## 🐛 Current Issues" daily-summaries/2025/08/

# Find next steps
grep -r "## 🎯 Next Steps" daily-summaries/2025/08/

# Find recent file changes
grep -r "Files Modified" daily-summaries/2025/08/ | tail -10
```

## Required Sections for AI-Generated Summaries

### Session Start Summary Must Include:
- `## 📅 Date:` - Current date
- `## ⏰ Session:` - "Start"
- `## 🎯 Focus:` - Primary objective
- `## ⏱️ Duration:` - Estimated time
- `## 🤖 AI-Generated:` - "Yes"
- `## ✅ Current System Status` - What's working
- `## 🎯 Session Goals` - What to accomplish
- `## 🛠️ Preparation Checklist` - What to check

### Session Complete Summary Must Include:
- `## 📅 Date:` - Current date
- `## ⏰ Session:` - "Complete"
- `## 🎯 Focus:` - What was accomplished
- `## ⏱️ Duration:` - Actual time spent
- `## 🤖 AI-Generated:` - "Yes"
- `## ✅ Session Results` - Goals achieved/not achieved
- `## 🚀 Major Accomplishments` - What was done
- `## 🔧 Technical Details` - Files, commands, configs
- `## 🐛 Issues Encountered` - Problems and solutions
- `## 📊 Current System Status` - Updated status
- `## 🎯 Next Steps` - What to do next

## AI Search Patterns

### Finding System Status
```bash
# Look for current status sections
grep -A 20 "## ✅ Current System Status" daily-summaries/2025/08/*.md

# Look for working components
grep -A 10 "Working Components" daily-summaries/2025/08/*.md
```

### Finding Issues
```bash
# Look for issues sections
grep -A 20 "## 🐛 Current Issues" daily-summaries/2025/08/*.md

# Look for problems remaining
grep -A 10 "Problems Remaining" daily-summaries/2025/08/*.md
```

### Finding Next Steps
```bash
# Look for next steps sections
grep -A 20 "## 🎯 Next Steps" daily-summaries/2025/08/*.md

# Look for immediate priorities
grep -A 10 "Immediate Priorities" daily-summaries/2025/08/*.md
```

### Finding Technical Changes
```bash
# Look for file modifications
grep -A 10 "Files Modified" daily-summaries/2025/08/*.md

# Look for commands executed
grep -A 10 "Commands Executed" daily-summaries/2025/08/*.md
```

## AI Quality Checklist

### Before Committing a Summary
- [ ] All required sections are present
- [ ] Metadata is complete and accurate
- [ ] Technical details are specific and accurate
- [ ] File paths and commands are exact
- [ ] Links to related documentation are included
- [ ] Formatting follows template structure
- [ ] Content is searchable and machine-readable

### When Reading Summaries
- [ ] Check date to ensure relevance
- [ ] Look for current status sections
- [ ] Note any issues or problems
- [ ] Identify next steps and priorities
- [ ] Review technical changes made
- [ ] Check for related documentation links

## Common AI Tasks

### Task: Understand Current System State
```bash
# Read most recent status summary
ls -t daily-summaries/2025/08/*current-status.md | head -1 | xargs cat

# Check system health
curl -s http://10.0.20.69/health
curl -s http://10.0.20.69/api/latest

# Check service status
ssh shrimp@10.0.20.69 'systemctl status temperhum-mqtt'
```

### Task: Find Recent Issues
```bash
# Search for recent issues
grep -r "Issues/Challenges" daily-summaries/2025/08/ | tail -5

# Check for problems remaining
grep -r "Problems Remaining" daily-summaries/2025/08/ | tail -5
```

### Task: Find Next Steps
```bash
# Search for next steps
grep -r "Next Steps" daily-summaries/2025/08/ | tail -5

# Check immediate priorities
grep -r "Immediate Priorities" daily-summaries/2025/08/ | tail -5
```

### Task: Track Progress
```bash
# List recent summaries
ls -t daily-summaries/2025/08/*.md | head -10

# Check for milestones
grep -r "Milestone" daily-summaries/2025/08/
```

## AI Best Practices

### For Reading
- **Start with Recent**: Always read most recent summary first
- **Look for Patterns**: Identify recurring issues or themes
- **Check Status**: Verify current system state before making changes
- **Follow Links**: Read related documentation for context

### For Writing
- **Be Specific**: Use exact technical details
- **Be Consistent**: Follow template structure exactly
- **Be Complete**: Include all required sections
- **Be Accurate**: Verify information before documenting
- **Be Searchable**: Use consistent terminology

### For Maintenance
- **Update Regularly**: Generate summaries after each session
- **Keep Indexes Current**: Update status indexes frequently
- **Archive Old**: Move old summaries to archive directory
- **Validate Format**: Ensure consistent structure

---

**🤖 These instructions ensure AI can efficiently read, generate, and maintain high-quality daily summaries for the turtle monitoring system.** 