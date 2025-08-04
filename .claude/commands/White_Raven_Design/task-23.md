# White_Raven_Design - Task 23

Execute task 23 for the White_Raven_Design specification.

## Task Description
Create Deployment Documentation

## Code Reuse
**Leverage existing code**: Markdown documentation

## Requirements Reference
**Requirements**: 6.2, 6.4

## Usage
```
/White_Raven_Design-task-23
```

## Instructions

**Agent-Based Execution (Recommended)**: First check if agents are enabled by running:

```bash
npx @pimzino/claude-code-spec-workflow@latest using-agents
```

If this returns `true`, use the `spec-task-executor` agent for optimal task implementation:

```
Use the spec-task-executor agent to implement task 23: "Create Deployment Documentation" for the White_Raven_Design specification.

The agent should:
1. Load all specification context from .claude/specs/White_Raven_Design/
2. Load steering documents from .claude/steering/ (if available)
3. Implement ONLY task 23: "Create Deployment Documentation"
4. Follow all project conventions and leverage existing code
5. Mark the task as complete in tasks.md
6. Provide a completion summary

Context files to load using get-content script:

**Load task-specific context:**
```bash
# Get specific task details with all information
npx @pimzino/claude-code-spec-workflow@latest get-tasks White_Raven_Design 23 --mode single

# Load context documents
# Windows:
npx @pimzino/claude-code-spec-workflow@latest get-content "C:\path\to\project\.claude\specs\White_Raven_Design\requirements.md"
npx @pimzino/claude-code-spec-workflow@latest get-content "C:\path\to\project\.claude\specs\White_Raven_Design\design.md"

# macOS/Linux:
npx @pimzino/claude-code-spec-workflow@latest get-content "/path/to/project/.claude/specs/White_Raven_Design/requirements.md"
npx @pimzino/claude-code-spec-workflow@latest get-content "/path/to/project/.claude/specs/White_Raven_Design/design.md"

# Steering documents (if they exist):
npx @pimzino/claude-code-spec-workflow@latest get-content "/path/to/project/.claude/steering/product.md"
npx @pimzino/claude-code-spec-workflow@latest get-content "/path/to/project/.claude/steering/tech.md"
npx @pimzino/claude-code-spec-workflow@latest get-content "/path/to/project/.claude/steering/structure.md"
```

Task details:
- ID: 23
- Description: Create Deployment Documentation
- Leverage: Markdown documentation
- Requirements: 6.2, 6.4
```

**Fallback Execution**: If the agent is not available, you can execute:
```
/spec-execute 23 White_Raven_Design
```

**Context Loading**:
Before executing the task, you MUST load all relevant context using the get-content script:

**1. Specification Documents:**
```bash
# Requirements document:
# Windows: npx @pimzino/claude-code-spec-workflow@latest get-content "C:\path\to\project\.claude\specs\White_Raven_Design\requirements.md"
# macOS/Linux: npx @pimzino/claude-code-spec-workflow@latest get-content "/path/to/project/.claude/specs/White_Raven_Design/requirements.md"

# Design document:
# Windows: npx @pimzino/claude-code-spec-workflow@latest get-content "C:\path\to\project\.claude\specs\White_Raven_Design\design.md"
# macOS/Linux: npx @pimzino/claude-code-spec-workflow@latest get-content "/path/to/project/.claude/specs/White_Raven_Design/design.md"

# Task details:
npx @pimzino/claude-code-spec-workflow@latest get-tasks White_Raven_Design 23 --mode single
```

**2. Steering Documents (if available):**
```bash
# Windows examples:
npx @pimzino/claude-code-spec-workflow@latest get-content "C:\path\to\project\.claude\steering\product.md"
npx @pimzino/claude-code-spec-workflow@latest get-content "C:\path\to\project\.claude\steering\tech.md"
npx @pimzino/claude-code-spec-workflow@latest get-content "C:\path\to\project\.claude\steering\structure.md"

# macOS/Linux examples:
npx @pimzino/claude-code-spec-workflow@latest get-content "/path/to/project/.claude/steering/product.md"
npx @pimzino/claude-code-spec-workflow@latest get-content "/path/to/project/.claude/steering/tech.md"
npx @pimzino/claude-code-spec-workflow@latest get-content "/path/to/project/.claude/steering/structure.md"
```

**Process**:
1. Load all context documents listed above
2. Execute task 23: "Create Deployment Documentation"
3. **Prioritize code reuse**: Use existing components and utilities identified above
4. Follow all implementation guidelines from the main /spec-execute command
5. **Follow steering documents**: Adhere to patterns in tech.md and conventions in structure.md
6. **CRITICAL**: Mark the task as complete in tasks.md by changing [ ] to [x]
7. Confirm task completion to user
8. Stop and wait for user review

**Important Rules**:
- Execute ONLY this specific task
- **Leverage existing code** whenever possible to avoid rebuilding functionality
- **Follow project conventions** from steering documents
- Mark task as complete by changing [ ] to [x] in tasks.md
- Stop after completion and wait for user approval
- Do not automatically proceed to the next task
- Validate implementation against referenced requirements

## Task Completion Protocol
When completing this task:
1. **Mark task complete**: Use the get-tasks script to mark completion:
   ```bash
   npx @pimzino/claude-code-spec-workflow@latest get-tasks White_Raven_Design 23 --mode complete
   ```
2. **Confirm to user**: State clearly "Task 23 has been marked as complete"
3. **Stop execution**: Do not proceed to next task automatically
4. **Wait for instruction**: Let user decide next steps

## Post-Implementation Review (if agents enabled)
First check if agents are enabled:
```bash
npx @pimzino/claude-code-spec-workflow@latest using-agents
```

If this returns `true`, automatically use the `spec-task-implementation-reviewer` agent:

```
Use the spec-task-implementation-reviewer agent to review the implementation of task 23 for the White_Raven_Design specification.

The agent automatically loads complete context using helper scripts:
- Specification documents (requirements.md, design.md, tasks.md) via get-content
- Steering documents (product.md, tech.md, structure.md) via get-content (if available)
- Specific task 23 details via get-tasks
- All implementation changes for task 23

The reviewer provides comprehensive quality validation:
- Requirements compliance verification
- Design adherence assessment
- Code quality standards validation
- Integration point verification
- Structured feedback on implementation quality
- Identification of any issues requiring attention

This ensures all implementations meet quality standards before proceeding.
```

## Code Duplication Analysis (if agents enabled)
First check if agents are enabled:
```bash
npx @pimzino/claude-code-spec-workflow@latest using-agents
```

If this returns `true`, use the `spec-duplication-detector` agent:

```
Use the spec-duplication-detector agent to analyze code duplication for task 23 of the White_Raven_Design specification.

The agent should:
1. Scan the newly implemented code
2. Identify any duplicated patterns
3. Suggest refactoring opportunities
4. Recommend existing utilities to reuse
5. Help maintain DRY principles

This ensures code quality and maintainability.
```

## Integration Testing (if agents enabled)
First check if agents are enabled:
```bash
npx @pimzino/claude-code-spec-workflow@latest using-agents
```

If this returns `true`, use the `spec-integration-tester` agent:

```
Use the spec-integration-tester agent to test the implementation of task 23 for the White_Raven_Design specification.

The agent should:
1. Load all specification documents and understand the changes made
2. Run relevant test suites for the implemented functionality
3. Validate integration points and API contracts
4. Check for regressions using git history analysis
5. Provide comprehensive test feedback

Test context:
- Changes made in task 23
- Related test suites to execute
- Integration points to validate
- Git history for regression analysis
```

## Next Steps
After task completion, you can:
- Review the implementation (automated if spec-task-implementation-reviewer agent is available)
- Run integration tests (automated if spec-integration-tester agent is available)
- Address any issues identified in reviews or tests
- Execute the next task using /White_Raven_Design-task-[next-id]
- Check overall progress with /spec-status White_Raven_Design
- If all tasks complete, run /spec-completion-review White_Raven_Design
