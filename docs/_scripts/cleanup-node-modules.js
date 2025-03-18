/**
 * Cleanup script to remove Node.js module documentation
 * 
 * This script removes documentation files that were generated from node_modules
 * which are not relevant to our project.
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Find files from node_modules
function findNodeModulesDocs() {
    // Look for migration report first
    const reportPath = path.resolve('_source/migration-report.json');
    
    if (fs.existsSync(reportPath)) {
        console.log('Using migration report to identify node_modules docs...');
        const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
        
        const nodeModuleFiles = report.filter(entry => 
            entry.sourceFile.includes('node_modules') || 
            // Also include files from common node.js modules
            entry.metadata.title.match(/^(lodash|express|react|angular|vue|webpack|babel|typescript|eslint|prettier|mocha|jest|chai)$/)
        );
        
        return nodeModuleFiles.map(entry => entry.targetFile);
    }
    
    // If no report, use glob pattern matching
    console.log('No migration report found, using glob patterns...');
    
    const guidesDirPath = path.resolve('_source/development/guides');
    const files = glob.sync(`${guidesDirPath}/*.md`);
    
    return files.filter(file => {
        const content = fs.readFileSync(file, 'utf8');
        const filename = path.basename(file);
        
        // Check if the file is likely from node_modules
        return (
            filename.match(/^(readme|license|changelog|history|security|api)\.md$/i) ||
            content.includes('npm') || 
            content.includes('node_modules') ||
            content.includes('package.json')
        );
    });
}

// Remove files
function removeFiles(files) {
    console.log(`Found ${files.length} files to remove.`);
    
    let removed = 0;
    let errors = 0;
    
    files.forEach(file => {
        try {
            if (fs.existsSync(file)) {
                fs.unlinkSync(file);
                console.log(`Removed: ${file}`);
                removed++;
            }
        } catch (error) {
            console.error(`Error removing ${file}:`, error);
            errors++;
        }
    });
    
    console.log(`\nCleanup complete:`);
    console.log(`  ${removed} files removed`);
    console.log(`  ${errors} errors encountered`);
}

// Main function
function main() {
    const filesToRemove = findNodeModulesDocs();
    removeFiles(filesToRemove);
}

// Run the script
main(); 