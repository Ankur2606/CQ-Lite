#!/usr/bin/env python3
"""
Create demo files for testing the Code Quality Intelligence Agent
"""

def create_python_demo():
    """Create Python demo file with various issues"""
    python_code = '''import os
import subprocess
import sys

def process_user_input(user_input):
    """Process user input - contains security issues"""
    # SECURITY ISSUE: eval usage allows arbitrary code execution
    result = eval(user_input)
    
    # PERFORMANCE ISSUE: inefficient nested loops
    for i in range(1000):
        for j in range(1000):
            temp = i * j
    
    # COMPLEXITY ISSUE: deeply nested conditions
    if result > 0:
        if result < 100:
            if result % 2 == 0:
                if result > 50:
                    if result < 75:
                        return "very complex logic"
                    else:
                        return "complex logic"
                else:
                    return "medium logic"
            else:
                return "odd number"
        else:
            return "large number"
    else:
        return "negative or zero"

# DUPLICATION ISSUE: similar functions
def process_data(data):
    """Process data - duplicate of process_user_input logic"""
    result = eval(data)  # Same security issue
    return result

def another_process_data(info):
    """Another data processor - also duplicate"""
    result = eval(info)  # Same security issue again
    return result

# PERFORMANCE ISSUE: inefficient string concatenation
def build_large_string():
    """Build a large string inefficiently"""
    result = ""
    for i in range(10000):
        result += str(i) + ","
    return result

# SECURITY ISSUE: shell injection vulnerability
def execute_command(user_command):
    """Execute user command - shell injection risk"""
    os.system(user_command)  # Dangerous!
    
# COMPLEXITY ISSUE: function too long and complex
def complex_business_logic(data, config, options, flags):
    """Complex business logic with high cyclomatic complexity"""
    if not data:
        return None
    
    if config.get('mode') == 'strict':
        if options.get('validate'):
            if flags.get('deep_check'):
                for item in data:
                    if item.get('type') == 'critical':
                        if item.get('status') == 'pending':
                            if item.get('priority') > 5:
                                if item.get('assigned'):
                                    return process_critical_item(item)
                                else:
                                    return assign_critical_item(item)
                            else:
                                return queue_item(item)
                        else:
                            return skip_item(item)
                    else:
                        return process_normal_item(item)
            else:
                return quick_process(data)
        else:
            return raw_process(data)
    else:
        return simple_process(data)

if __name__ == "__main__":
    # Test the functions
    print("Demo file created successfully!")
'''
    
    with open('demo_code.py', 'w') as f:
        f.write(python_code)
    print("✅ Created demo_code.py")

def create_javascript_demo():
    """Create JavaScript demo file with various issues"""
    js_code = '''// Demo JavaScript file with code quality issues

function processUserData() {
    // SECURITY ISSUE: eval usage
    var userInput = getUserInput();
    eval(userInput);  // Dangerous!
    
    // STYLE ISSUE: var instead of let/const
    var oldStyleVariable = "should use let or const";
    
    // PERFORMANCE ISSUE: DOM queries in loop
    for (let i = 0; i < 1000; i++) {
        document.getElementById('element-' + i).style.display = 'block';
    }
    
    // SECURITY ISSUE: innerHTML without sanitization
    document.getElementById('content').innerHTML = userInput;
    
    // STYLE ISSUE: console.log in production code
    console.log("Processing user data:", userInput);
}

// COMPLEXITY ISSUE: deeply nested function
function complexValidation(data) {
    if (data) {
        if (data.type === 'user') {
            if (data.permissions) {
                if (data.permissions.read) {
                    if (data.permissions.write) {
                        if (data.permissions.admin) {
                            if (data.status === 'active') {
                                if (data.verified) {
                                    return true;
                                } else {
                                    return false;
                                }
                            } else {
                                return false;
                            }
                        } else {
                            return checkRegularUser(data);
                        }
                    } else {
                        return checkReadOnlyUser(data);
                    }
                } else {
                    return false;
                }
            } else {
                return false;
            }
        } else {
            return false;
        }
    } else {
        return false;
    }
}

// DUPLICATION ISSUE: similar functions
function validateUser(user) {
    if (user && user.type === 'user') {
        return user.status === 'active';
    }
    return false;
}

function checkUser(user) {
    if (user && user.type === 'user') {
        return user.status === 'active';
    }
    return false;
}

// PERFORMANCE ISSUE: inefficient array operations
function processLargeArray(items) {
    let result = [];
    for (let i = 0; i < items.length; i++) {
        for (let j = 0; j < items.length; j++) {
            if (items[i].id === items[j].parentId) {
                result.push(items[i]);
            }
        }
    }
    return result;
}

// SECURITY ISSUE: document.write usage
function displayMessage(message) {
    document.write("<div>" + message + "</div>");
}

// COMPLEXITY ISSUE: long function with multiple responsibilities
function handleUserAction(action, user, context, options, callback) {
    console.log("Handling action:", action);
    
    if (!user) {
        callback(new Error("No user provided"));
        return;
    }
    
    if (!action) {
        callback(new Error("No action specified"));
        return;
    }
    
    if (action === 'login') {
        if (user.credentials) {
            if (validateCredentials(user.credentials)) {
                if (user.status === 'active') {
                    if (user.permissions.login) {
                        if (context.secure) {
                            if (options.rememberMe) {
                                setRememberMeCookie(user);
                            }
                            createSession(user);
                            logUserAction(user, 'login_success');
                            callback(null, { success: true, user: user });
                        } else {
                            callback(new Error("Insecure context"));
                        }
                    } else {
                        callback(new Error("No login permission"));
                    }
                } else {
                    callback(new Error("User not active"));
                }
            } else {
                callback(new Error("Invalid credentials"));
            }
        } else {
            callback(new Error("No credentials provided"));
        }
    } else if (action === 'logout') {
        destroySession(user);
        logUserAction(user, 'logout');
        callback(null, { success: true });
    } else {
        callback(new Error("Unknown action"));
    }
}

console.log("Demo JavaScript file loaded");
'''
    
    with open('demo_code.js', 'w') as f:
        f.write(js_code)
    print("✅ Created demo_code.js")

def main():
    """Create all demo files"""
    print("🎯 Creating demo files for Code Quality Intelligence Agent...")
    create_python_demo()
    create_javascript_demo()
    print("\n🚀 Demo files created! You can now test with:")
    print("   uv run python -m cli analyze demo_code.py")
    print("   uv run python -m cli analyze demo_code.js")

if __name__ == "__main__":
    main()