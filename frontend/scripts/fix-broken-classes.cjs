#!/usr/bin/env node

/**
 * Fix Broken Class Attributes
 * Repairs class attributes that are missing closing quotes and content
 * 
 * This fixes issues from the dark mode migration where content got eaten
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Patterns to fix
const FIXES = [
  // Headers that lost their text
  { pattern: /class="([^"]*text-gray-900[^"]*) In"/, replacement: 'class="$1">Sign In' },
  { pattern: /class="([^"]*text-gray-900[^"]*) In</, replacement: 'class="$1">Sign In<' },
  { pattern: /class="([^"]*text-gray-900[^"]*) Account"/, replacement: 'class="$1">Create Account' },
  { pattern: /class="([^"]*text-gray-900[^"]*) Account</, replacement: 'class="$1">Create Account<' },
  { pattern: /class="([^"]*text-gray-900[^"]*) Password"/, replacement: 'class="$1">Reset Password' },
  { pattern: /class="([^"]*text-gray-900[^"]*) Password</, replacement: 'class="$1">Reset Password<' },
  { pattern: /class="([^"]*text-gray-900[^"]*) Verification"/, replacement: 'class="$1">Email Verification' },
  { pattern: /class="([^"]*text-gray-900[^"]*) Verification</, replacement: 'class="$1">Email Verification<' },
  
  // Common text that got eaten
  { pattern: /class="([^"]*text-gray-\d+[^"]*) Date"/, replacement: 'class="$1">Start Date' },
  { pattern: /class="([^"]*text-gray-\d+[^"]*) Date</, replacement: 'class="$1">Start Date<' },
  { pattern: /class="([^"]*text-gray-\d+[^"]*) Members"/, replacement: 'class="$1">Team Members' },
  { pattern: /class="([^"]*text-gray-\d+[^"]*) Members</, replacement: 'class="$1">Team Members<' },
  { pattern: /class="([^"]*text-gray-\d+[^"]*) Tasks"/, replacement: 'class="$1">Total Tasks' },
  { pattern: /class="([^"]*text-gray-\d+[^"]*) Tasks</, replacement: 'class="$1">Total Tasks<' },
  { pattern: /class="([^"]*text-gray-\d+[^"]*) Progress"/, replacement: 'class="$1">In Progress' },
  { pattern: /class="([^"]*text-gray-\d+[^"]*) Progress</, replacement: 'class="$1">In Progress<' },
  
  // Fix unclosed quotes with various content patterns
  { pattern: /class="([^"]*)\s+([a-zA-Z][^">]*)">/g, replacement: 'class="$1">$2">' },
  { pattern: /class="([^"]*)\s+\{\{([^}]+)\}\}">/g, replacement: 'class="$1">{{$2}}">' },
  
  // Generic unclosed class attributes at end of line
  { pattern: /class="([^"\n]*?)(\s*)$/gm, replacement: 'class="$1">' },
  
  // Fix common button/span patterns
  { pattern: />([A-Z][a-z]+\s[A-Z][a-z]+)<\//, replacement: '>$1</' },
];

function fixBrokenClasses(content) {
  let modified = false;
  let newContent = content;
  
  // Apply fixes
  FIXES.forEach(({ pattern, replacement }) => {
    const before = newContent;
    newContent = newContent.replace(pattern, replacement);
    if (before !== newContent) {
      modified = true;
    }
  });
  
  // Fix specific Vue template expressions that got broken
  newContent = newContent.replace(/class="([^"]*)\s+([\w.]+)\s*}}">/g, 'class="$1">{{ $2 }}">');
  newContent = newContent.replace(/class="([^"]*)\s+([\w.]+)\s*<\/p>/g, 'class="$1">{{ $2 }}</p>');
  newContent = newContent.replace(/class="([^"]*)\s+([\w.]+)\s*<\/h/g, 'class="$1">{{ $2 }}</h');
  newContent = newContent.replace(/class="([^"]*)\s+([\w.]+)\s*<\/dd>/g, 'class="$1">{{ $2 }}</dd>');
  newContent = newContent.replace(/class="([^"]*)\s+([\w.]+)\s*<\/dt>/g, 'class="$1">{{ $2 }}</dt>');
  newContent = newContent.replace(/class="([^"]*)\s+([\w.]+)\s*<\/span>/g, 'class="$1">{{ $2 }}</span>');
  
  // Fix some specific content patterns
  newContent = newContent.replace(/class="([^"]*)\s+your email address\.\.\.">/g, 'class="$1">Verifying your email address...">');
  newContent = newContent.replace(/class="([^"]*)\s+message }}">/g, 'class="$1">{{ message }}">');
  newContent = newContent.replace(/class="([^"]*)\s+description }}">/g, 'class="$1">{{ description }}">');
  newContent = newContent.replace(/class="([^"]*)\s+welcomeMessage }}">/g, 'class="$1">{{ welcomeMessage }}">');
  newContent = newContent.replace(/class="([^"]*)\s+totalProjects }}">/g, 'class="$1">{{ totalProjects }}">');
  newContent = newContent.replace(/class="([^"]*)\s+activeCount }}">/g, 'class="$1">{{ activeCount }}">');
  newContent = newContent.replace(/class="([^"]*)\s+projects<\/h/g, 'class="$1">No projects</h');
  newContent = newContent.replace(/class="([^"]*)\s+tasks yet<\/h/g, 'class="$1">No tasks yet</h');
  newContent = newContent.replace(/class="([^"]*)\s+started by creating/g, 'class="$1">Get started by creating');
  
  if (newContent !== content) {
    modified = true;
  }
  
  return { content: newContent, modified };
}

function processFile(filePath) {
  console.log(`\n📄 Processing: ${filePath}`);
  
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const { content: newContent, modified } = fixBrokenClasses(content);
    
    if (modified) {
      fs.writeFileSync(filePath, newContent);
      console.log(`  ✅ Fixed broken class attributes!`);
      return true;
    } else {
      console.log(`  ⏭️  No broken classes found`);
      return false;
    }
  } catch (error) {
    console.error(`  ❌ Error processing file: ${error.message}`);
    return null;
  }
}

function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log(`
🔧 Broken Class Attribute Fixer
Usage:
  node fix-broken-classes.cjs <file-or-pattern>
  
Examples:
  node fix-broken-classes.cjs "src/**/*.vue"          # Fix all Vue files
  node fix-broken-classes.cjs src/components/Button.vue    # Single file
  
Options:
  --dry-run    Show what would be fixed without modifying files
    `);
    process.exit(0);
  }
  
  const isDryRun = args.includes('--dry-run');
  const pattern = args.find(arg => !arg.startsWith('--'));
  
  if (!pattern) {
    console.error('❌ No file pattern provided!');
    process.exit(1);
  }
  
  // Find files matching the pattern
  const files = glob.sync(pattern, {
    ignore: ['**/node_modules/**', '**/dist/**', '**/build/**']
  });
  
  if (files.length === 0) {
    console.error(`❌ No files found matching pattern: ${pattern}`);
    process.exit(1);
  }
  
  console.log(`🔍 Found ${files.length} file(s) to check`);
  
  if (isDryRun) {
    console.log('🔄 DRY RUN MODE - No files will be modified');
  }
  
  let fixedCount = 0;
  let cleanCount = 0;
  let errorCount = 0;
  
  files.forEach(file => {
    if (isDryRun) {
      console.log(`\n📄 Would check: ${file}`);
      const content = fs.readFileSync(file, 'utf-8');
      const { modified } = fixBrokenClasses(content);
      if (modified) {
        console.log('  → Would be fixed');
        fixedCount++;
      } else {
        console.log('  → Already clean');
        cleanCount++;
      }
    } else {
      const result = processFile(file);
      if (result === true) fixedCount++;
      else if (result === false) cleanCount++;
      else errorCount++;
    }
  });
  
  // Summary
  console.log('\n📊 Fix Summary:');
  console.log(`  ✅ Fixed: ${fixedCount} file(s)`);
  console.log(`  ✨ Clean: ${cleanCount} file(s)`);
  if (errorCount > 0) {
    console.log(`  ❌ Errors: ${errorCount} file(s)`);
  }
  
  if (isDryRun) {
    console.log('\n💡 Run without --dry-run to apply fixes');
  }
}

// Run the script
main();