/**
 * Documentation Migration Tool
 * 
 * Helps migrate existing documentation to the new unified system:
 * - Parses existing README files
 * - Extracts content and metadata
 * - Creates properly formatted documents in the new system
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');
const yaml = require('js-yaml');

// Configuration
const sourceDirectories = [
    '../.docs',
    '../wiki',
    '..'  // Root directory
];

const targetDirectory = './_source';
const configFile = './_config.yml';

// Load configuration
let config;
try {
    config = yaml.load(fs.readFileSync(configFile, 'utf8'));
} catch (error) {
    console.error('Error loading config file:', error);
    process.exit(1);
}

// Helper: Extract title from markdown content
function extractTitle(content) {
    const titleMatch = content.match(/^#\s+(.+)$/m);
    return titleMatch ? titleMatch[1].trim() : null;
}

// Helper: Generate a slug from a string
function slugify(text) {
    return text
        .toLowerCase()
        .replace(/[^\w ]+/g, '')
        .replace(/ +/g, '-');
}

// Helper: Determine document section and category
function determineCategory(filePath, content) {
    // Default values
    let section = 'development';
    let category = 'guides';
    
    // Try to determine from file path
    const lowerPath = filePath.toLowerCase();
    
    // Check for gameplay-related content
    if (
        lowerPath.includes('game-design') || 
        lowerPath.includes('gameplay') || 
        lowerPath.includes('lore') ||
        lowerPath.includes('quick_start')
    ) {
        section = 'gameplay';
        
        if (lowerPath.includes('lore')) {
            category = 'reference';
        } else {
            category = 'guides';
        }
    } 
    // Check for development-related content
    else {
        if (
            lowerPath.includes('architecture') || 
            lowerPath.includes('system') ||
            lowerPath.includes('implementation')
        ) {
            category = 'architecture';
        } else if (
            lowerPath.includes('api') || 
            lowerPath.includes('reference')
        ) {
            category = 'reference';
        } else {
            category = 'guides';
        }
    }
    
    return { section, category };
}

// Helper: Check if content is related to cursor rules
function isCursorRule(filePath, content) {
    const lowerPath = filePath.toLowerCase();
    const lowerContent = content.toLowerCase();
    
    return (
        lowerPath.includes('rules') || 
        lowerPath.includes('cursor') ||
        lowerContent.includes('cursor rule') ||
        lowerContent.includes('cursor guidelines')
    );
}

// Helper: Extract metadata from content
function extractMetadata(filePath, content) {
    const metadata = {};
    
    // Try to extract title
    metadata.title = extractTitle(content) || path.basename(filePath, path.extname(filePath));
    
    // Generate ID
    metadata.id = slugify(metadata.title);
    
    // Determine category
    const { section, category } = determineCategory(filePath, content);
    metadata.section = section;
    metadata.category = category;
    
    // Created and updated dates from file stats
    const stats = fs.statSync(filePath);
    metadata.created = new Date(stats.birthtime).toISOString().split('T')[0];
    metadata.updated = new Date(stats.mtime).toISOString().split('T')[0];
    
    // Generate version (0.1.0 for initial conversion)
    metadata.version = '0.1.0';
    
    // Check if this should be a cursor rule
    if (isCursorRule(filePath, content)) {
        metadata.cursor_rule = true;
        metadata.glob = '**/*';
        metadata.priority = 500;
    }
    
    return metadata;
}

// Process a single file
function processFile(filePath) {
    console.log(`Processing file: ${filePath}`);
    
    try {
        // Read file content
        const content = fs.readFileSync(filePath, 'utf8');
        
        // Extract metadata
        const metadata = extractMetadata(filePath, content);
        
        // Generate output path
        const outputDir = path.join(targetDirectory, metadata.section, metadata.category);
        const outputFile = path.join(outputDir, `${metadata.id}.md`);
        
        // Ensure output directory exists
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        
        // Check if file already has frontmatter
        let finalContent;
        if (content.startsWith('---')) {
            console.log('  File already has frontmatter, appending metadata...');
            // Extract existing frontmatter
            const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
            if (match) {
                const existingFrontmatter = yaml.load(match[1]);
                const documentContent = match[2];
                
                // Merge with extracted metadata (existing takes precedence)
                const mergedFrontmatter = { ...metadata, ...existingFrontmatter };
                
                // Rebuild content with merged frontmatter
                finalContent = `---\n${yaml.dump(mergedFrontmatter)}---\n\n${documentContent}`;
            } else {
                // Invalid frontmatter, use extracted
                finalContent = `---\n${yaml.dump(metadata)}---\n\n${content}`;
            }
        } else {
            // Add new frontmatter
            finalContent = `---\n${yaml.dump(metadata)}---\n\n${content}`;
        }
        
        // Write to output file
        fs.writeFileSync(outputFile, finalContent);
        console.log(`  Migrated to: ${outputFile}`);
        
        return {
            sourceFile: filePath,
            targetFile: outputFile,
            metadata
        };
    } catch (error) {
        console.error(`  Error processing ${filePath}:`, error);
        return null;
    }
}

// Main migration function
function migrateDocumentation() {
    console.log('Starting documentation migration...');
    
    let totalFiles = 0;
    let migratedFiles = 0;
    const results = [];
    
    // Process each source directory
    sourceDirectories.forEach(sourceDir => {
        console.log(`Scanning directory: ${sourceDir}`);
        
        // Find markdown files
        const files = glob.sync(`${sourceDir}/**/*.md`);
        totalFiles += files.length;
        
        // Also include README files without extensions
        const readmeFiles = glob.sync(`${sourceDir}/**/README*`).filter(file => 
            !file.endsWith('.md')
        );
        totalFiles += readmeFiles.length;
        
        // Process markdown files
        files.forEach(file => {
            // Skip files in the new docs directory
            if (file.startsWith('./docs/_source')) {
                return;
            }
            
            const result = processFile(file);
            if (result) {
                results.push(result);
                migratedFiles++;
            }
        });
        
        // Process README files
        readmeFiles.forEach(file => {
            const result = processFile(file);
            if (result) {
                results.push(result);
                migratedFiles++;
            }
        });
    });
    
    console.log('\nMigration Summary:');
    console.log(`Total files scanned: ${totalFiles}`);
    console.log(`Successfully migrated: ${migratedFiles}`);
    
    // Generate a migration report
    const reportPath = path.join(targetDirectory, 'migration-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));
    console.log(`Migration report written to: ${reportPath}`);
}

// Run the migration
migrateDocumentation(); 