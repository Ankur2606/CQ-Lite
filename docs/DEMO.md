# Demo Script

## CQ Lite Demo

### Overview
This demo showcases the AI-powered code analysis capabilities of CQ Lite, including AST-based analytics, security detection, and conversational AI insights.

### Demo Flow (10 minutes)

#### 1. Introduction (1 minute)
"Today I'll demonstrate CQ Lite - an AI-powered tool that provides deep insights into code quality using AST analysis and Gemini AI."

**Key Points:**
- AST-based analysis for Python and JavaScript
- Security, performance, and complexity detection
- AI-powered conversational interface
- Modern dark gradient UI

#### 2. CLI Analysis Demo (3 minutes)

**Setup:**
```bash
# Create sample Python file with issues
cat > demo_code.py << 'EOF'
import os
import subprocess

def process_user_input(user_input):
    # Security issue: eval usage
    result = eval(user_input)
    
    # Performance issue: inefficient loop
    for i in range(1000):
        for j in range(1000):
            temp = i * j
    
    # Complexity issue: nested conditions
    if result > 0:
        if result < 100:
            if result % 2 == 0:
                if result > 50:
                    return "complex logic"
    
    return result

# Duplicate function
def process_data(data):
    result = eval(data)
    return result

def another_process_data(info):
    result = eval(info)
    return result
EOF
```

**Demo Commands:**
```bash
# Analyze the demo file
uv run python -m cli analyze demo_code.py

# Show JSON output
uv run python -m cli analyze demo_code.py --format json

# Filter by severity
uv run python -m cli analyze demo_code.py --severity high
```

**Expected Output:**
- Security issues (eval usage)
- Performance issues (nested loops)
- Complexity issues (high cyclomatic complexity)
- Duplication detection

#### 3. Web Interface Demo (4 minutes)

**Landing Page (30 seconds):**
- Navigate to http://localhost:3000
- Showcase modern dark gradient design
- Highlight key features

**Dashboard (2 minutes):**
- Navigate to /dashboard
- Upload demo_code.py
- Show analysis results:
  - Summary cards (total issues, files, lines, complexity)
  - Severity breakdown
  - Issue filtering
  - Detailed issue cards with suggestions

**Visual Elements to Highlight:**
- Dark gradient backgrounds
- Color-coded severity levels
- Interactive filtering
- Code snippets and suggestions

#### 4. AI Chat Demo (2 minutes)

**Navigate to /chat:**
- Start with: "What are the most critical security issues in my code?"
- Follow up: "How can I fix the eval() usage?"
- Show: "What performance optimizations do you recommend?"

**Demonstrate:**
- Contextual AI responses
- Follow-up suggestions
- Natural language explanations
- Code-specific advice

### Sample Demo Code Issues

#### Python Issues to Demonstrate:

1. **Security (Critical)**:
   ```python
   result = eval(user_input)  # Arbitrary code execution
   ```

2. **Performance (High)**:
   ```python
   for i in range(1000):
       for j in range(1000):  # O(n²) complexity
   ```

3. **Complexity (Medium)**:
   ```python
   # Deeply nested conditions (cyclomatic complexity > 10)
   if condition1:
       if condition2:
           if condition3:
               if condition4:
   ```

4. **Duplication (Medium)**:
   ```python
   def func1(data):
       return eval(data)
   
   def func2(info):
       return eval(info)  # Duplicate logic
   ```

#### JavaScript Issues to Demonstrate:

```javascript
// Create demo.js
function processData() {
    // Security issue
    eval(userInput);
    
    // Performance issue
    for (let i = 0; i < 1000; i++) {
        document.getElementById('element-' + i);  // DOM query in loop
    }
    
    // Style issue
    var oldStyleVar = "should use let/const";
    
    // Console statement
    console.log("Debug statement");
}
```

### Key Demo Points

#### Technical Highlights:
- **AST Analysis**: "Notice how we detect structural issues, not just text patterns"
- **Multi-Language**: "Works with both Python and JavaScript out of the box"
- **Severity Scoring**: "Issues are prioritized by impact and risk"
- **AI Integration**: "Gemini provides contextual explanations and fixes"

#### UI/UX Highlights:
- **Modern Design**: "Dark gradient theme with excellent contrast"
- **Responsive**: "Works on desktop, tablet, and mobile"
- **Interactive**: "Filter, search, and drill down into issues"
- **Accessible**: "WCAG compliant with keyboard navigation"

### Q&A Preparation

**Common Questions:**

1. **"How accurate is the analysis?"**
   - AST-based analysis is highly accurate
   - Combines multiple tools (bandit, radon)
   - AI provides context and reduces false positives

2. **"Can it handle large codebases?"**
   - Designed for scalability
   - Incremental analysis support
   - CLI for batch processing

3. **"What languages are supported?"**
   - Currently Python and JavaScript/TypeScript
   - Extensible architecture for more languages
   - Roadmap includes Java, C#, Go

4. **"How does the AI integration work?"**
   - Uses Google Gemini Pro
   - Context-aware responses
   - Trained on code quality best practices

### Closing (30 seconds)
"This demonstrates how AI can enhance traditional static analysis, providing not just issue detection but intelligent insights and actionable recommendations for improving code quality."

### Demo Environment Setup

```bash
# Ensure everything is running
uv run uvicorn backend.main:app --reload &
cd frontend && npm run dev &

# Create demo files
python create_demo_files.py

# Test CLI
uv run python -m cli analyze demo_code.py
```