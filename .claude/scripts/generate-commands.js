#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

function generateCommands(specName) {
    console.log(`Generating commands for spec: ${specName}`);
    
    // Read the tasks.md file
    const tasksPath = path.join('.claude', 'specs', specName, 'tasks.md');
    
    if (!fs.existsSync(tasksPath)) {
        console.error(`Tasks file not found: ${tasksPath}`);
        process.exit(1);
    }
    
    const tasksContent = fs.readFileSync(tasksPath, 'utf8');
    
    // Parse tasks from the markdown
    const tasks = [];
    const lines = tasksContent.split('\n');
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        // Look for task items in format: - [ ] 1. Task description
        const taskMatch = line.match(/^- \[ \] (\d+(?:\.\d+)*)\.\s*(.+)$/);
        if (taskMatch) {
            const taskId = taskMatch[1];
            const taskTitle = taskMatch[2];
            
            // Collect task details (lines that follow and are indented)
            const details = [];
            let j = i + 1;
            while (j < lines.length && (lines[j].startsWith('  ') || lines[j].trim() === '')) {
                if (lines[j].trim() !== '') {
                    details.push(lines[j].replace(/^  /, ''));
                }
                j++;
            }
            
            tasks.push({
                id: taskId,
                title: taskTitle,
                details: details.join('\n')
            });
        }
    }
    
    console.log(`Found ${tasks.length} tasks`);
    
    // Create commands directory
    const commandsDir = path.join('.claude', 'commands', specName);
    if (!fs.existsSync(commandsDir)) {
        fs.mkdirSync(commandsDir, { recursive: true });
    }
    
    // Generate command files
    tasks.forEach(task => {
        const commandContent = `# ${specName.replace(/_/g, ' ')} - Task ${task.id}

Execute task ${task.id}: ${task.title}

## Task Details
${task.details}

## Command
\`\`\`
/spec-execute ${task.id} ${specName}
\`\`\`

This command will execute task ${task.id} for the ${specName} specification.
`;
        
        const commandFileName = `task-${task.id}.md`;
        const commandPath = path.join(commandsDir, commandFileName);
        
        fs.writeFileSync(commandPath, commandContent);
        console.log(`Generated: ${commandPath}`);
    });
    
    console.log(`\nGenerated ${tasks.length} command files in ${commandsDir}`);
    console.log(`\nTo use the new commands, restart Claude Code and use:`);
    tasks.forEach(task => {
        console.log(`  /${specName}-task-${task.id}`);
    });
}

// Get spec name from command line arguments
const specName = process.argv[2];

if (!specName) {
    console.error('Usage: node generate-commands.js <spec-name>');
    console.error('Example: node generate-commands.js user-authentication');
    process.exit(1);
}

generateCommands(specName);