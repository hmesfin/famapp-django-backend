#!/usr/bin/env node

/**
 * Dark Mode Duplicate Fixer
 * Removes conflicting dark mode classes that got duplicated
 * 
 * This fixes issues like: "dark:text-gray-100 dark:text-gray-800"
 * Keeping only the first dark variant for each property type
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Regex to find multiple dark: classes for the same property
const DUPLICATE_PATTERNS = [
  // Text colors
  /(\bdark:text-\S+)(\s+dark:text-\S+)+/g,
  // Background colors  
  /(\bdark:bg-\S+)(\s+dark:bg-\S+)+/g,
  // Border colors
  /(\bdark:border-\S+)(\s+dark:border-\S+)+/g,
  // Divide colors
  /(\bdark:divide-\S+)(\s+dark:divide-\S+)+/g,
  // Ring colors
  /(\bdark:ring-\S+)(\s+dark:ring-\S+)+/g,
  // Placeholder colors
  /(\bdark:placeholder-\S+)(\s+dark:placeholder-\S+)+/g,
  // Hover states
  /(\bdark:hover:text-\S+)(\s+dark:hover:text-\S+)+/g,
  /(\bdark:hover:bg-\S+)(\s+dark:hover:bg-\S+)+/g,
  /(\bdark:hover:border-\S+)(\s+dark:hover:border-\S+)+/g,
  // Focus states
  /(\bdark:focus:border-\S+)(\s+dark:focus:border-\S+)+/g,
  /(\bdark:focus:ring-\S+)(\s+dark:focus:ring-\S+)+/g,
];

function removeDuplicateDarkClasses(content) {
  let modified = false;
  let newContent = content;
  
  DUPLICATE_PATTERNS.forEach(pattern => {
    const originalContent = newContent;
    newContent = newContent.replace(pattern, (match, firstClass, duplicates) => {
      console.log(`  ✓ Removing duplicate: ${match} → ${firstClass}`);
      return firstClass;
    });
    if (originalContent !== newContent) {
      modified = true;
    }
  });
  
  return { content: newContent, modified };
}

function processFile(filePath) {
  console.log(`\n📄 Processing: ${filePath}`);
  
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const { content: newContent, modified } = removeDuplicateDarkClasses(content);
    
    if (modified) {
      fs.writeFileSync(filePath, newContent);
      console.log(`  ✅ Fixed duplicate dark mode classes!`);
      return true;
    } else {
      console.log(`  ⏭️  No duplicates found`);
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
🔧 Dark Mode Duplicate Fixer
Usage:
  node fix-dark-duplicates.cjs <file-or-pattern>
  
Examples:
  node fix-dark-duplicates.cjs "src/**/*.vue"          # Fix all Vue files
  node fix-dark-duplicates.cjs src/components/Button.vue    # Single file
  
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
      const { modified } = removeDuplicateDarkClasses(content);
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