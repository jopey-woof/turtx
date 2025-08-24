# 🤖 AI Session Start - Turtle Monitor System

## 🎯 **Simple, Repeatable AI Instruction**

**Copy and paste this instruction to any AI:**

```
🤖 AI Session Start - Turtle Monitor System

Please follow this workflow:

1. 📖 READ: Find and read the most recent session summary
   - Look for files ending in "session-complete.md" or "current-status.md"
   - Read the most recent one to understand current state

2. 📊 PARSE: Extract and present this information:
   - Current system status (working/not working)
   - Active issues that need attention
   - Recent accomplishments from last session
   - Available focus areas for today

3. 🎯 PRESENT: Show me a clear summary with focus options:
   - System health status
   - Number of active issues
   - 3-5 focus area options for today
   - Your recommendation based on current state

4. ⏸️ WAIT: Let me choose the focus area before proceeding

Use the templates in daily-summaries/templates/ for consistent formatting.
```

---

## 🔄 **Even Simpler Version**

**For quick daily use:**

```
🤖 Turtle Monitor AI Session:

1. Read the last session summary (find most recent *session-complete.md or *current-status.md)
2. Check current system status (curl http://10.0.20.69/health)
3. Present me with:
   - Current system health
   - Active issues
   - 3-5 focus options for today
4. Wait for my direction

Then proceed with my chosen focus.
```

---

## 📋 **What the AI Should Present**

### System Status Summary
```
🏥 SYSTEM HEALTH: [Excellent/Good/Warning/Critical]
⏰ UPTIME: [How long running]
🔧 SERVICES: [Running/Stopped count]
🐛 ISSUES: [Number of active problems]
```

### Focus Options
```
🎯 AVAILABLE FOCUS AREAS:
1. 🐛 Issue Resolution - Fix active problems
2. 🚀 Feature Development - Work on new features  
3. 🔧 System Maintenance - Optimize and cleanup
4. 📊 Monitoring - Health checks and validation
5. 📝 Documentation - Update docs and guides

💡 RECOMMENDED: [Based on current issues]
```

---

## 🎯 **User Response Examples**

### Choose from Options
```
"Focus on option 1 - Issue Resolution"
"Work on option 2 - Feature Development"
"Choose option 3 - System Maintenance"
```

### Custom Direction
```
"Focus on camera integration specifically"
"Prioritize fixing Sensor 2 hardware issues"
"Work on dashboard enhancements"
"Check system performance and optimize"
```

---

## 📝 **Session Completion**

**When the AI finishes the session, tell it:**

```
"Generate a session complete summary using the template at daily-summaries/templates/session-complete-template.md"
```

---

**🤖 This provides a consistent, repeatable way to start every AI session with proper context and clear direction.** 