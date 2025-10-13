#!/usr/bin/env node

/**
 * Dark Mode Migration Script
 * Ham Dog & TC's automated dark mode converter!
 * 
 * This script automatically adds Tailwind dark mode classes to Vue components
 * Run it on any component that needs dark mode support!
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Color mapping rules - the DRY way!
const COLOR_MAPPINGS = {
  // Text colors
  'text-gray-900': 'text-gray-900 dark:text-gray-100',
  'text-gray-800': 'text-gray-800 dark:text-gray-200',
  'text-gray-700': 'text-gray-700 dark:text-gray-300',
  'text-gray-600': 'text-gray-600 dark:text-gray-400',
  'text-gray-500': 'text-gray-500 dark:text-gray-400',
  'text-gray-400': 'text-gray-400 dark:text-gray-500',
  'text-gray-300': 'text-gray-300 dark:text-gray-600',
  'text-gray-200': 'text-gray-200 dark:text-gray-700',
  'text-gray-100': 'text-gray-100 dark:text-gray-800',
  
  // Background colors
  'bg-white': 'bg-white dark:bg-gray-800',
  'bg-gray-50': 'bg-gray-50 dark:bg-gray-900',
  'bg-gray-100': 'bg-gray-100 dark:bg-gray-800',
  'bg-gray-200': 'bg-gray-200 dark:bg-gray-700',
  'bg-gray-300': 'bg-gray-300 dark:bg-gray-600',
  'bg-gray-400': 'bg-gray-400 dark:bg-gray-500',
  'bg-gray-500': 'bg-gray-500 dark:bg-gray-400',
  'bg-gray-600': 'bg-gray-600 dark:bg-gray-300',
  'bg-gray-700': 'bg-gray-700 dark:bg-gray-200',
  'bg-gray-800': 'bg-gray-800 dark:bg-gray-100',
  'bg-gray-900': 'bg-gray-900 dark:bg-gray-50',
  
  // Border colors
  'border-gray-200': 'border-gray-200 dark:border-gray-700',
  'border-gray-300': 'border-gray-300 dark:border-gray-600',
  'border-gray-400': 'border-gray-400 dark:border-gray-500',
  'border-gray-500': 'border-gray-500 dark:border-gray-400',
  'border-gray-600': 'border-gray-600 dark:border-gray-300',
  'border-gray-700': 'border-gray-700 dark:border-gray-200',
  
  // Divide colors (for borders between elements)
  'divide-gray-200': 'divide-gray-200 dark:divide-gray-700',
  'divide-gray-300': 'divide-gray-300 dark:divide-gray-600',
  
  // Ring colors (for focus states)
  'ring-gray-200': 'ring-gray-200 dark:ring-gray-700',
  'ring-gray-300': 'ring-gray-300 dark:ring-gray-600',
  
  // Placeholder colors
  'placeholder-gray-400': 'placeholder-gray-400 dark:placeholder-gray-500',
  'placeholder-gray-500': 'placeholder-gray-500 dark:placeholder-gray-400',
  
  // Special cases for hover states
  'hover:bg-gray-50': 'hover:bg-gray-50 dark:hover:bg-gray-700',
  'hover:bg-gray-100': 'hover:bg-gray-100 dark:hover:bg-gray-700',
  'hover:bg-gray-200': 'hover:bg-gray-200 dark:hover:bg-gray-600',
  'hover:text-gray-900': 'hover:text-gray-900 dark:hover:text-gray-100',
  'hover:text-gray-700': 'hover:text-gray-700 dark:hover:text-gray-300',
  'hover:text-gray-600': 'hover:text-gray-600 dark:hover:text-gray-400',
  'hover:text-gray-500': 'hover:text-gray-500 dark:hover:text-gray-400',
  
  // Focus states
  'focus:border-gray-300': 'focus:border-gray-300 dark:focus:border-gray-600',
  'focus:ring-gray-200': 'focus:ring-gray-200 dark:focus:ring-gray-700',
  
  // Blue colors (keep them vibrant in dark mode)
  'text-blue-600': 'text-blue-600 dark:text-blue-400',
  'text-blue-500': 'text-blue-500 dark:text-blue-400',
  'bg-blue-50': 'bg-blue-50 dark:bg-blue-900/20',
  'bg-blue-100': 'bg-blue-100 dark:bg-blue-900/50',
  'bg-blue-600': 'bg-blue-600 dark:bg-blue-500',
  'hover:text-blue-600': 'hover:text-blue-600 dark:hover:text-blue-400',
  'hover:bg-blue-700': 'hover:bg-blue-700 dark:hover:bg-blue-600',
  
  // Red colors (for errors/dangers)
  'text-red-600': 'text-red-600 dark:text-red-400',
  'text-red-500': 'text-red-500 dark:text-red-400',
  'bg-red-50': 'bg-red-50 dark:bg-red-900/20',
  'bg-red-100': 'bg-red-100 dark:bg-red-900/50',
  'border-red-300': 'border-red-300 dark:border-red-700',
  
  // Green colors (for success)
  'text-green-600': 'text-green-600 dark:text-green-400',
  'text-green-500': 'text-green-500 dark:text-green-400',
  'bg-green-50': 'bg-green-50 dark:bg-green-900/20',
  'bg-green-100': 'bg-green-100 dark:bg-green-900/50',
  
  // Yellow colors (for warnings)
  'text-yellow-600': 'text-yellow-600 dark:text-yellow-400',
  'text-yellow-500': 'text-yellow-500 dark:text-yellow-400',
  'bg-yellow-50': 'bg-yellow-50 dark:bg-yellow-900/20',
  'bg-yellow-100': 'bg-yellow-100 dark:bg-yellow-900/50',
};

// Patterns to skip (already have dark mode or shouldn't change)
const SKIP_PATTERNS = [
  /dark:/,                    // Already has dark mode
  /class=["'][^"']*dark:/,    // Already has dark mode in class
  /bg-opacity-/,              // Opacity utilities work in both modes
  /text-opacity-/,            // Opacity utilities work in both modes
  /bg-transparent/,           // Transparent is universal
  /text-transparent/,         // Transparent is universal
  /text-white/,               // White text (usually on colored backgrounds)
  /text-black/,               // Black text (usually on colored backgrounds)
  /bg-blue-[567]\d\d/,        // Colored backgrounds (blue 500+)
  /bg-red-[567]\d\d/,         // Colored backgrounds (red 500+)
  /bg-green-[567]\d\d/,       // Colored backgrounds (green 500+)
  /bg-yellow-[567]\d\d/,      // Colored backgrounds (yellow 500+)
];

function shouldSkipLine(line) {
  return SKIP_PATTERNS.some(pattern => pattern.test(line));
}

function migrateClasses(content) {
  const lines = content.split('\n');
  let modified = false;
  
  const processedLines = lines.map(line => {
    // Skip if line already has dark mode or shouldn't be modified
    if (shouldSkipLine(line)) {
      return line;
    }
    
    let newLine = line;
    let lineModified = false;
    
    // Apply each mapping
    for (const [pattern, replacement] of Object.entries(COLOR_MAPPINGS)) {
      // Create regex that matches the pattern as a whole word in class attribute
      const regex = new RegExp(`(class=["'][^"']*)(\\b${pattern}\\b)(?![^"']*dark:)`, 'g');
      
      if (regex.test(newLine)) {
        newLine = newLine.replace(regex, `$1${replacement}`);
        lineModified = true;
        modified = true;
        console.log(`  ✓ Migrated: ${pattern} → ${replacement}`);
      }
    }
    
    return newLine;
  });
  
  return {
    content: processedLines.join('\n'),
    modified
  };
}

function processFile(filePath) {
  console.log(`\n📄 Processing: ${filePath}`);
  
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const { content: newContent, modified } = migrateClasses(content);
    
    if (modified) {
      fs.writeFileSync(filePath, newContent);
      console.log(`  ✅ Successfully migrated dark mode classes!`);
      return true;
    } else {
      console.log(`  ⏭️  No changes needed (already migrated or no applicable patterns)`);
      return false;
    }
  } catch (error) {
    console.error(`  ❌ Error processing file: ${error.message}`);
    return false;
  }
}

function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log(`
🌙 Dark Mode Migration Tool
Usage:
  node migrate-dark-mode.js <file-or-pattern>
  
Examples:
  node migrate-dark-mode.js src/components/MyComponent.vue    # Single file
  node migrate-dark-mode.js "src/components/**/*.vue"          # All components
  node migrate-dark-mode.js "src/views/**/*.vue"              # All views
  node migrate-dark-mode.js "src/**/*.vue"                    # All Vue files
  
Options:
  --dry-run    Show what would be changed without modifying files
  --verbose    Show detailed migration info
    `);
    process.exit(0);
  }
  
  const isDryRun = args.includes('--dry-run');
  const isVerbose = args.includes('--verbose');
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
  
  console.log(`🔍 Found ${files.length} file(s) to process`);
  
  if (isDryRun) {
    console.log('🔄 DRY RUN MODE - No files will be modified');
  }
  
  let successCount = 0;
  let skipCount = 0;
  let errorCount = 0;
  
  files.forEach(file => {
    if (isDryRun) {
      console.log(`\n📄 Would process: ${file}`);
      const content = fs.readFileSync(file, 'utf-8');
      const { modified } = migrateClasses(content);
      if (modified) {
        console.log('  → Would be modified');
        successCount++;
      } else {
        console.log('  → Would be skipped');
        skipCount++;
      }
    } else {
      const result = processFile(file);
      if (result === true) successCount++;
      else if (result === false) skipCount++;
      else errorCount++;
    }
  });
  
  // Summary
  console.log('\n📊 Migration Summary:');
  console.log(`  ✅ Modified: ${successCount} file(s)`);
  console.log(`  ⏭️  Skipped: ${skipCount} file(s)`);
  if (errorCount > 0) {
    console.log(`  ❌ Errors: ${errorCount} file(s)`);
  }
  
  if (isDryRun) {
    console.log('\n💡 Run without --dry-run to apply changes');
  }
}

// Run the script
main();