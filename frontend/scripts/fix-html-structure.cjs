#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Pattern to find broken class attributes - classes that were moved outside their quotes
const brokenPattern = /">[a-zA-Z\-:]+"/g;

function fixBrokenClasses(content) {
  let fixed = content;
  let count = 0;
  
  // Fix pattern like: class="some-class">another-class">
  // Should become: class="some-class another-class">
  fixed = fixed.replace(/">([\w\-:]+)"/g, (match, classes) => {
    count++;
    return ' ' + classes + '"';
  });
  
  return { fixed, count };
}

function processFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const { fixed, count } = fixBrokenClasses(content);
  
  if (count > 0) {
    fs.writeFileSync(filePath, fixed);
    console.log(`✅ Fixed ${count} broken class attributes in ${path.relative(process.cwd(), filePath)}`);
    return count;
  }
  
  return 0;
}

function main() {
  const srcDir = path.join(process.cwd(), 'src');
  const pattern = path.join(srcDir, '**/*.vue');
  
  console.log('🔍 Searching for Vue files with broken HTML structure...\n');
  
  const files = glob.sync(pattern);
  let totalFiles = 0;
  let totalFixes = 0;
  
  files.forEach(file => {
    const fixes = processFile(file);
    if (fixes > 0) {
      totalFiles++;
      totalFixes += fixes;
    }
  });
  
  console.log('\n' + '='.repeat(50));
  console.log(`✨ Fixed ${totalFixes} broken class attributes across ${totalFiles} files`);
}

main();