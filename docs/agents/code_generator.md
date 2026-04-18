# CodeGenerator Agent

**Intelligent LLM-powered code generation with multi-language support.**

## Overview

The CodeGenerator agent uses Large Language Models to generate code based on natural language descriptions, requirements, and specifications. It supports multiple programming languages, integrates with the knowledge base for artifact storage, and can leverage previous code generation for consistency.

## Key Capabilities

### 1. **Code Generation**
- Generate code from natural language prompts
- Multi-language support (Python, JavaScript, Java, Go, Rust, etc.)
- Context-aware generation based on project type
- Consistent coding style and patterns

### 2. **Multiple Approaches**
- Quick generation: Fast synthesis of working code
- Detailed generation: Comprehensive implementation with documentation
- Template-based: Use existing code patterns
- Skill-based: Apply learned skills to generation

### 3. **Integration**
- Store generated code in knowledge base
- Validate generated code with CodeValidator
- Track code lineage and modifications
- Support iterative refinement

### 4. **Quality Assurance**
- Automatic code formatting
- Comments and documentation generation
- Type hints and signatures
- Error handling patterns

## Usage

### Basic: Generate Simple Code

```python
from socratic_agents import CodeGenerator

generator = CodeGenerator()

result = generator.process({
    "action": "generate",
    "prompt": "Create a function to calculate factorial",
    "language": "python"
})

print(result["code"])
# def factorial(n):
#     if n <= 1:
#         return 1
#     return n * factorial(n - 1)
```

### Intermediate: Generate with Specifications

```python
result = generator.process({
    "action": "generate",
    "prompt": "Create a REST API endpoint for user authentication",
    "language": "python",
    "framework": "fastapi",
    "specifications": {
        "endpoint": "/login",
        "method": "POST",
        "parameters": ["username", "password"],
        "return_type": "authentication_token"
    }
})

print(result["code"])
print(result["imports"])    # Required imports
print(result["dependencies"]) # Package requirements
```

### Advanced: Generate with Context

```python
result = generator.process({
    "action": "generate",
    "prompt": "Database migration to add user roles",
    "language": "python",
    "framework": "sqlalchemy",
    "context": {
        "existing_model": "User",
        "database_type": "postgresql",
        "migration_tool": "alembic"
    },
    "style": {
        "docstring_format": "google",
        "type_hints": True,
        "line_length": 88
    }
})
```

## Request Format

### action: `generate`
Generate code from a prompt.

```python
request = {
    "action": "generate",
    "prompt": "Create a sorting function",        # Required
    "language": "python",                         # Required
    "framework": "django",                        # Optional
    "specifications": {...},                      # Optional
    "context": {...},                             # Optional
    "style": {...},                               # Optional
    "complexity": "intermediate"                  # Optional: simple|intermediate|complex
}
```

**Returns:**
```python
{
    "status": "success",
    "code": "def sort_list(items):\n    ...",
    "language": "python",
    "imports": ["from typing import List"],
    "dependencies": ["numpy==1.21.0"],
    "explanation": "This function implements...",
    "complexity": "O(n log n)",
    "error_handling": ["ValueError on empty list"],
    "code_id": "gen_123"
}
```

### action: `refactor`
Improve existing code.

```python
request = {
    "action": "refactor",
    "code": existing_code,                        # Required
    "language": "python",                         # Required
    "improvements": [                             # Optional
        "add_type_hints",
        "improve_documentation",
        "reduce_complexity"
    ],
    "target_style": "google"
}
```

**Returns:**
```python
{
    "status": "success",
    "original_code": "...",
    "refactored_code": "...",
    "changes": [
        "Added type hints",
        "Improved variable names",
        "Extracted helper functions"
    ],
    "improvements_made": 3
}
```

### action: `generate_tests`
Generate test code for existing code.

```python
request = {
    "action": "generate_tests",
    "code": function_code,                        # Required
    "language": "python",                         # Required
    "test_framework": "pytest",                   # Optional
    "coverage_goal": 95                           # Optional
}
```

**Returns:**
```python
{
    "status": "success",
    "test_code": "def test_function():\n    ...",
    "test_cases": [
        {"name": "test_valid_input", "description": "..."},
        {"name": "test_edge_cases", "description": "..."},
        {"name": "test_error_handling", "description": "..."}
    ],
    "estimated_coverage": 95
}
```

### action: `document`
Generate documentation for code.

```python
request = {
    "action": "document",
    "code": function_code,                        # Required
    "language": "python",                         # Required
    "doc_format": "google",                       # Optional
    "include": [                                  # Optional
        "docstring",
        "examples",
        "parameters",
        "returns"
    ]
}
```

**Returns:**
```python
{
    "status": "success",
    "documented_code": "...",
    "docstring": "...",
    "examples": ["example_1", "example_2"],
    "parameter_docs": {...}
}
```

## Configuration

### Initialization

```python
from socratic_agents import CodeGenerator

# Basic initialization
generator = CodeGenerator()

# With LLM client
from socrates_nexus import LLMClient
llm = LLMClient(provider="anthropic", model="claude-opus")
generator = CodeGenerator(llm_client=llm)

# With knowledge store
generator = CodeGenerator(
    llm_client=llm,
    knowledge_store=kb_client
)
```

### Configuration Options

| Option | Type | Default | Purpose |
|--------|------|---------|---------|
| `llm_client` | LLMClient | None | LLM for code generation |
| `knowledge_store` | Store | None | Store generated code artifacts |
| `max_tokens` | int | 2000 | Maximum tokens per generation |
| `temperature` | float | 0.7 | Creativity level (0.0-1.0) |
| `format_code` | bool | True | Auto-format generated code |

## Supported Languages

| Language | Status | Frameworks |
|----------|--------|-----------|
| Python | ✅ Full | Django, FastAPI, Flask |
| JavaScript | ✅ Full | React, Node.js, Vue |
| TypeScript | ✅ Full | React, Express |
| Java | ✅ Full | Spring, Maven |
| Go | ✅ Full | Gin, Standard Library |
| Rust | ✅ Full | Actix, Tokio |
| C++ | ✅ Full | Standard Library, Boost |
| SQL | ✅ Full | PostgreSQL, MySQL |

## Code Specifications

### Parameters
```python
{
    "name": "parameter_name",
    "type": "str",
    "description": "What it does",
    "required": True,
    "default": None
}
```

### Returns
```python
{
    "type": "dict",
    "description": "What is returned",
    "example": {"key": "value"}
}
```

### Context
```python
{
    "project_type": "web_app",
    "existing_code": "...",
    "coding_standards": "pep8",
    "dependencies": ["numpy", "pandas"],
    "version_constraints": {"python": ">=3.9"}
}
```

## Generation Styles

### Docstring Formats
- `google` - Google style docstrings
- `numpy` - NumPy style docstrings
- `sphinx` - Sphinx-compatible docstrings
- `javadoc` - JavaDoc style

### Code Styles
- `pep8` - Python PEP 8
- `airbnb` - Airbnb JavaScript style
- `google` - Google Java style
- `rust` - Rust naming conventions

## Best Practices

### 1. **Provide Clear Prompts**
```python
# Good: Specific and detailed
"Create a function that validates email addresses using regex,
 supporting plus addressing and common TLDs"

# Avoid: Vague
"Make an email function"
```

### 2. **Include Context**
```python
request = {
    "action": "generate",
    "prompt": "Add caching layer",
    "context": {
        "existing_code": current_function,
        "performance_requirements": "sub-100ms"
    }
}
```

### 3. **Validate Generated Code**
```python
from socratic_agents import CodeValidator

code_result = generator.process(generate_request)
validation = validator.process({
    "code": code_result["code"],
    "language": "python"
})

if validation["status"] == "success":
    use_code(code_result["code"])
```

### 4. **Store for Reuse**
```python
# Store successful generation for future use
if code_result["status"] == "success":
    knowledge_base.store({
        "type": "generated_code",
        "prompt": request["prompt"],
        "code": code_result["code"],
        "language": code_result["language"]
    })
```

## Integration Examples

### With Code Validator
```python
generator = CodeGenerator()
validator = CodeValidator()

# Generate code
gen_result = generator.process({
    "action": "generate",
    "prompt": "Merge two sorted arrays",
    "language": "python"
})

# Validate it
val_result = validator.process({
    "code": gen_result["code"],
    "language": "python"
})

if val_result["status"] == "success":
    print("Code is valid and ready to use")
```

### With Quality Controller
```python
from socratic_agents import CodeGenerator, QualityController

generator = CodeGenerator()
quality = QualityController()

code_result = generator.process(generate_request)

# Check code quality
quality_result = quality.process({
    "action": "check",
    "code": code_result["code"],
    "language": "python"
})

print("Quality Score:", quality_result["quality_score"])
print("Issues:", quality_result["issues"])
```

### With Skill System
```python
from socratic_agents import CodeGenerator, SkillGeneratorAgent

generator = CodeGenerator()
skill_gen = SkillGeneratorAgent()

# Generate code
code = generator.process({"action": "generate", ...})

# Create skill from generated code
skill = skill_gen.process({
    "action": "generate",
    "code": code["code"],
    "skill_name": "array_merge"
})

# Use skill in future generations
generator.process({
    "action": "generate",
    "prompt": "...",
    "apply_skills": [skill["skill_id"]]
})
```

## Common Patterns

### Pattern 1: Simple Code Generation
```python
result = generator.process({
    "action": "generate",
    "prompt": "Hello world program",
    "language": "python"
})
```

### Pattern 2: Generate with Tests
```python
code_result = generator.process({
    "action": "generate",
    "prompt": "Fibonacci calculator"
})

test_result = generator.process({
    "action": "generate_tests",
    "code": code_result["code"]
})
```

### Pattern 3: Iterative Refinement
```python
code = generate_initial_code("binary search")

for iteration in range(3):
    code = generator.process({
        "action": "refactor",
        "code": code,
        "improvements": ["optimize", "document"]
    })["refactored_code"]
```

### Pattern 4: Full Code Pipeline
```python
# 1. Generate
code = generator.process({"action": "generate", ...})

# 2. Generate tests
tests = generator.process({"action": "generate_tests", ...})

# 3. Validate
validation = validator.process({"code": code})

# 4. Document
docs = generator.process({"action": "document", ...})

# 5. Store
knowledge_base.store_code(code, tests, docs)
```

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Generate simple code | 1-3s | Basic 50-100 lines |
| Generate complex code | 5-15s | 200+ lines with context |
| Refactor code | 2-5s | Improving existing code |
| Generate tests | 3-8s | Full test suite |
| Generate docs | 1-3s | Docstrings and comments |

## Troubleshooting

### Generated Code Has Errors
- Provide more specific prompt
- Include context and specifications
- Use `action: "generate_tests"` to verify
- Run through CodeValidator

### Incorrect Language Syntax
- Check language parameter is correct
- Verify framework if specified
- Include style guidelines in request
- Review returned code carefully

### Missing Dependencies
- Check `dependencies` in response
- Install listed packages
- Verify version compatibility
- Check `imports` field

### Inconsistent Code Style
- Specify `style` in request
- Use consistent `docstring_format`
- Enable `format_code: True`
- Review generated code

## Advanced Features

### Custom Templates

```python
# Use custom code templates
generator.templates["api_endpoint"] = {
    "language": "python",
    "framework": "fastapi",
    "template": "def {name}({params}):\n    ..."
}

code = generator.process({
    "action": "generate_from_template",
    "template": "api_endpoint",
    "params": {"name": "get_user", "params": "user_id: int"}
})
```

### Batch Generation

```python
requests = [
    {"prompt": "Sort function", "language": "python"},
    {"prompt": "Search function", "language": "python"},
    {"prompt": "Filter function", "language": "python"}
]

results = [generator.process(req) for req in requests]
```

---

**Related Agents:** CodeValidator, QualityController, SkillGeneratorAgent

**Next:** [CodeValidator Agent](./code_validator.md)
