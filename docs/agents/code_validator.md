# CodeValidator Agent

**Code validation, correctness checking, and issue detection.**

## Overview

The CodeValidator agent validates code for syntax errors, logical issues, and potential problems. It supports multiple programming languages and can leverage LLM clients for deeper semantic analysis beyond basic syntax validation.

## Key Capabilities

### 1. **Basic Code Validation**
- Syntax error detection
- Empty code detection
- Language-specific validation
- Issue categorization by severity

### 2. **Multi-Language Support**
- Python, JavaScript, Java, Go, Rust, C++, SQL, and more
- Language-specific error detection
- Proper syntax rules for each language

### 3. **LLM-Enhanced Analysis**
- Deep semantic analysis with LLM client
- Error pattern recognition
- Code quality insights beyond syntax
- Contextual issue detection

### 4. **Issue Reporting**
- Severity levels for each issue
- Line number information
- Detailed issue descriptions
- Issue counts and summaries

## Usage

### Basic: Validate Simple Code

```python
from socratic_agents import CodeValidator

validator = CodeValidator()

python_code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""

result = validator.process({
    "code": python_code,
    "language": "python"
})

print(f"Valid: {result['valid']}")
print(f"Issues: {result['issue_count']}")
```

### Intermediate: Check Code with Issues

```python
invalid_code = """
def broken_function()
    x = 10  # Missing colon
    y = x +  # Incomplete expression
    return y
"""

result = validator.process({
    "code": invalid_code,
    "language": "python"
})

if not result['valid']:
    for issue in result['issues']:
        print(f"[{issue['severity']}] Line {issue['line']}: {issue['message']}")
```

### Advanced: Validate with LLM Analysis

```python
from socrates_nexus import LLMClient

llm = LLMClient(provider="anthropic")
validator = CodeValidator(llm_client=llm)

code = """
def process_data(data):
    items = data.split(',')
    for item in items:
        print(item)
"""

# With LLM client, gets deeper semantic analysis
result = validator.process({
    "code": code,
    "language": "python"
})

print(f"Valid: {result['valid']}")
if result['issues']:
    for issue in result['issues']:
        print(f"Issue: {issue['message']}")
```

## Request Format

### action: (default - validate)
Validate code for errors and issues.

```python
request = {
    "code": code_string,                    # Required
    "language": "python"                    # Optional: default "python"
}
```

**Returns:**
```python
{
    "status": "success",
    "agent": "CodeValidator",
    "valid": true,
    "issues": [],
    "issue_count": 0
}
```

**With issues:**
```python
{
    "status": "success",
    "agent": "CodeValidator",
    "valid": false,
    "issues": [
        {
            "severity": "error",
            "line": 2,
            "message": "SyntaxError: invalid syntax"
        },
        {
            "severity": "error",
            "line": 3,
            "message": "SyntaxError: unexpected EOF while parsing"
        }
    ],
    "issue_count": 2
}
```

## Configuration

### Initialization

```python
from socratic_agents import CodeValidator

# Basic initialization (syntax checking only)
validator = CodeValidator()

# With LLM client (deep semantic analysis)
from socrates_nexus import LLMClient
llm = LLMClient(provider="anthropic")
validator = CodeValidator(llm_client=llm)
```

## Supported Languages

| Language | Status | Validation |
|----------|--------|-----------|
| Python | ✅ Full | Syntax, style |
| JavaScript | ✅ Full | Syntax, patterns |
| Java | ✅ Full | Syntax, structure |
| Go | ✅ Full | Syntax, idioms |
| Rust | ✅ Full | Syntax, safety |
| C++ | ✅ Full | Syntax, patterns |
| SQL | ✅ Full | Syntax, queries |

## Issue Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **error** | Code will not run | Fix required |
| **warning** | Code may fail | Review recommended |
| **info** | Improvement suggested | Optional fix |

## Best Practices

### 1. **Always Validate Generated Code**
```python
from socratic_agents import CodeGenerator, CodeValidator

generator = CodeGenerator()
validator = CodeValidator()

# Generate code
gen_result = generator.process({
    "action": "generate",
    "prompt": "Merge two sorted arrays",
    "language": "python"
})

# Validate immediately
val_result = validator.process({
    "code": gen_result["code"],
    "language": "python"
})

if val_result["valid"]:
    print("Code is valid and ready to use")
else:
    print("Code has issues - regenerate or fix")
```

### 2. **Validate Before Integration**
```python
def integrate_code_safely(code, language="python"):
    validator = CodeValidator()

    result = validator.process({
        "code": code,
        "language": language
    })

    if result["valid"]:
        return True, "Code validation passed"
    else:
        issues = "\n".join([
            f"  [{i['severity']}] {i['message']}"
            for i in result['issues'][:5]
        ])
        return False, f"Validation failed:\n{issues}"
```

### 3. **Handle Multiple Languages**
```python
def validate_codebase(file_language_pairs):
    validator = CodeValidator()
    results = {}

    for code, language in file_language_pairs:
        result = validator.process({
            "code": code,
            "language": language
        })
        results[language] = result

    return results
```

### 4. **Use with LLM for Deep Analysis**
```python
def detailed_validation(code, language="python"):
    from socrates_nexus import LLMClient

    llm = LLMClient(provider="anthropic")
    validator = CodeValidator(llm_client=llm)

    result = validator.process({
        "code": code,
        "language": language
    })

    # LLM provides deeper insights
    issues_summary = "Valid" if result['valid'] else "Invalid"

    return {
        "valid": result['valid'],
        "issue_count": result['issue_count'],
        "issues": result['issues'],
        "summary": issues_summary
    }
```

## Common Patterns

### Pattern 1: Basic Validation Gate

```python
def is_code_valid(code, language="python"):
    validator = CodeValidator()
    result = validator.process({
        "code": code,
        "language": language
    })
    return result["valid"]
```

### Pattern 2: Issue Collection

```python
def collect_issues(code, language="python"):
    validator = CodeValidator()
    result = validator.process({
        "code": code,
        "language": language
    })

    issues_by_severity = {
        "error": [],
        "warning": [],
        "info": []
    }

    for issue in result['issues']:
        severity = issue.get('severity', 'info')
        issues_by_severity[severity].append(issue)

    return issues_by_severity
```

### Pattern 3: Pre-Commit Validation

```python
def validate_before_commit(code_changes):
    validator = CodeValidator()

    for filename, code, language in code_changes:
        result = validator.process({
            "code": code,
            "language": language
        })

        if not result['valid']:
            print(f"Cannot commit {filename} - has validation errors")
            for issue in result['issues']:
                print(f"  {issue['message']}")
            return False

    return True
```

### Pattern 4: Validation with CodeGenerator

```python
def generate_and_validate(prompt, language="python"):
    from socratic_agents import CodeGenerator

    generator = CodeGenerator()
    validator = CodeValidator()

    # Generate
    gen_result = generator.process({
        "action": "generate",
        "prompt": prompt,
        "language": language
    })

    # Validate
    val_result = validator.process({
        "code": gen_result["code"],
        "language": language
    })

    return {
        "code": gen_result["code"],
        "valid": val_result["valid"],
        "issues": val_result["issues"]
    }
```

## Integration Examples

### With CodeGenerator

```python
from socratic_agents import CodeGenerator, CodeValidator

generator = CodeGenerator()
validator = CodeValidator()

# Generate code
gen_result = generator.process({
    "action": "generate",
    "prompt": "Fibonacci calculator",
    "language": "python"
})

# Validate it
val_result = validator.process({
    "code": gen_result["code"],
    "language": "python"
})

if val_result["valid"]:
    use_generated_code(gen_result["code"])
else:
    print(f"Generated code has {val_result['issue_count']} issues")
```

### With QualityController

```python
from socratic_agents import CodeValidator, QualityController

validator = CodeValidator()
quality = QualityController()

code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""

# First validate syntax
val_result = validator.process({
    "code": code,
    "language": "python"
})

if val_result["valid"]:
    # Then check quality
    quality_result = quality.process({
        "action": "check",
        "code": code
    })
    print(f"Quality score: {quality_result['quality_score']}")
```

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Basic validation | <100ms | Syntax check only |
| LLM validation | 1-3s | Semantic analysis |
| Empty check | <1ms | Immediate |
| Issue parsing | <10ms | Parse and categorize |

## Troubleshooting

### No Issues Found for Bad Code
- Ensure language parameter is correct
- Check code syntax is actually invalid
- Enable LLM client for deeper analysis
- Review issue severity - may be warnings not errors

### LLM Analysis Too Slow
- Use without LLM for faster validation
- Batch validations if possible
- Consider caching results
- Increase LLM timeout if needed

### Language Not Recognized
- Verify language parameter matches supported list
- Check for typos in language name
- Use language aliases if available
- Default to "python" if unsure

---

**Related Agents:** CodeGenerator, QualityController

**Next:** [SkillGeneratorAgent](./skill_generator_agent.md)
