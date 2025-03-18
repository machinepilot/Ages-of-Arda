/**
 * Cursor Rules Integration
 * 
 * Provides bidirectional synchronization between documentation and Cursor rules:
 * - Extracts documentation from Cursor rules
 * - Updates Cursor rules based on documentation changes
 * - Creates new documentation from rules when needed
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');
const yaml = require('js-yaml');

// Configuration
const CONFIG_FILE = path.resolve('docs/_config.yml');
let config;

try {
    config = yaml.load(fs.readFileSync(CONFIG_FILE, 'utf8'));
} catch (error) {
    console.error('Error loading config file:', error);
    process.exit(1);
}

// Paths
const DOCS_DIR = path.resolve('docs/_source');
const RULE_DIR = path.resolve(config.cursor_rules.rule_directory || '../.cursor/rules');

/**
 * Find all documents with links to Cursor rules
 */
function findDocumentsWithRuleLinks() {
    console.log('Finding documents with rule links...');
    
    // Get all markdown files
    const files = glob.sync(`${DOCS_DIR}/**/*.md`);
    
    // Filter for those with cursor_rule: true or cursor_rules array
    return files
        .map(file => {
            try {
                const content = fs.readFileSync(file, 'utf8');
                const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
                
                if (!frontmatterMatch) {
                    return null;
                }
                
                const frontmatter = yaml.load(frontmatterMatch[1]);
                
                if (frontmatter.cursor_rule === true || 
                   (frontmatter.cursor_rules && frontmatter.cursor_rules.length > 0)) {
                    return {
                        path: file,
                        frontmatter,
                        content: frontmatterMatch[2]
                    };
                }
                
                return null;
            } catch (error) {
                console.error(`Error processing file ${file}:`, error);
                return null;
            }
        })
        .filter(Boolean);
}

/**
 * Find rules that don't have corresponding documentation
 */
function findOrphanedRules() {
    console.log('Finding orphaned rules...');
    
    // Get all rules
    const rules = glob.sync(`${RULE_DIR}/**/*.mdc`);
    
    // Get all documents with rule links
    const docRules = findDocumentsWithRuleLinks();
    
    // Create a set of rule paths that are already linked
    const linkedRules = new Set();
    
    docRules.forEach(doc => {
        if (doc.frontmatter.cursor_rule === true) {
            // This creates a rule, but it's not linked to an existing one
            return;
        }
        
        if (doc.frontmatter.cursor_rules) {
            doc.frontmatter.cursor_rules.forEach(rule => {
                linkedRules.add(path.resolve(RULE_DIR, rule));
            });
        }
    });
    
    // Return rules that aren't linked to any document
    return rules.filter(rule => !linkedRules.has(path.resolve(rule)));
}

/**
 * Update document from rule
 */
function updateDocFromRule(docPath, rulePath) {
    console.log(`Updating doc ${docPath} from rule ${rulePath}...`);
    
    try {
        // Read the rule file
        const ruleContent = fs.readFileSync(rulePath, 'utf8');
        const ruleMatch = ruleContent.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
        
        if (!ruleMatch) {
            console.error(`Rule file ${rulePath} has invalid format.`);
            return false;
        }
        
        const ruleFrontmatter = yaml.load(ruleMatch[1]);
        const ruleBody = ruleMatch[2];
        
        // Read the doc file
        const docContent = fs.readFileSync(docPath, 'utf8');
        const docMatch = docContent.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
        
        if (!docMatch) {
            console.error(`Doc file ${docPath} has invalid format.`);
            return false;
        }
        
        const docFrontmatter = yaml.load(docMatch[1]);
        
        // Update doc frontmatter from rule frontmatter
        docFrontmatter.title = ruleFrontmatter.title;
        docFrontmatter.updated = new Date().toISOString().split('T')[0];
        
        // Generate the new doc content
        const newDocContent = `---\n${yaml.dump(docFrontmatter)}---\n\n${ruleBody}`;
        
        // Write the updated doc
        fs.writeFileSync(docPath, newDocContent);
        console.log(`Updated doc: ${docPath}`);
        
        return true;
    } catch (error) {
        console.error(`Error updating doc from rule:`, error);
        return false;
    }
}

/**
 * Update rule from document
 */
function updateRuleFromDoc(rulePath, docPath) {
    console.log(`Updating rule ${rulePath} from doc ${docPath}...`);
    
    try {
        // Read the doc file
        const docContent = fs.readFileSync(docPath, 'utf8');
        const docMatch = docContent.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
        
        if (!docMatch) {
            console.error(`Doc file ${docPath} has invalid format.`);
            return false;
        }
        
        const docFrontmatter = yaml.load(docMatch[1]);
        const docBody = docMatch[2];
        
        // Ensure rule directory exists
        const ruleDir = path.dirname(rulePath);
        if (!fs.existsSync(ruleDir)) {
            fs.mkdirSync(ruleDir, { recursive: true });
        }
        
        // Check if rule exists
        const ruleExists = fs.existsSync(rulePath);
        let ruleFrontmatter;
        
        if (ruleExists) {
            // Read existing rule
            const ruleContent = fs.readFileSync(rulePath, 'utf8');
            const ruleMatch = ruleContent.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
            
            if (ruleMatch) {
                ruleFrontmatter = yaml.load(ruleMatch[1]);
            } else {
                ruleFrontmatter = {};
            }
        } else {
            ruleFrontmatter = {};
        }
        
        // Update rule frontmatter
        ruleFrontmatter.title = docFrontmatter.title;
        ruleFrontmatter.glob = docFrontmatter.glob || ruleFrontmatter.glob || "**/*";
        ruleFrontmatter.priority = docFrontmatter.priority || ruleFrontmatter.priority || 500;
        
        if (docFrontmatter.related) {
            ruleFrontmatter.related = docFrontmatter.related;
        }
        
        // Generate the new rule content
        const newRuleContent = `---\n${yaml.dump(ruleFrontmatter)}---\n\n${docBody}`;
        
        // Write the updated rule
        fs.writeFileSync(rulePath, newRuleContent);
        console.log(`${ruleExists ? 'Updated' : 'Created'} rule: ${rulePath}`);
        
        return true;
    } catch (error) {
        console.error(`Error updating rule from doc:`, error);
        return false;
    }
}

/**
 * Generate document from rule
 */
function generateDocFromRule(rulePath) {
    console.log(`Generating doc from rule ${rulePath}...`);
    
    try {
        // Read the rule file
        const ruleContent = fs.readFileSync(rulePath, 'utf8');
        const ruleMatch = ruleContent.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
        
        if (!ruleMatch) {
            console.error(`Rule file ${rulePath} has invalid format.`);
            return false;
        }
        
        const ruleFrontmatter = yaml.load(ruleMatch[1]);
        const ruleBody = ruleMatch[2];
        
        // Determine the document section and category
        const section = 'development';
        const category = path.basename(path.dirname(rulePath)) === RULE_DIR ? 
            'guides' : path.basename(path.dirname(rulePath));
        
        // Generate a document ID
        const id = path.basename(rulePath, '.mdc');
        
        // Create document frontmatter
        const docFrontmatter = {
            title: ruleFrontmatter.title,
            id,
            section,
            category,
            created: new Date().toISOString().split('T')[0],
            updated: new Date().toISOString().split('T')[0],
            version: '0.1.0',
            auto_generated: true,
            cursor_rules: [path.relative(RULE_DIR, rulePath)],
            tags: ['cursor-rule', category]
        };
        
        // Generate document content
        const docContent = `---\n${yaml.dump(docFrontmatter)}---\n\n${ruleBody}`;
        
        // Determine output path
        const outputDir = path.join(DOCS_DIR, section, category);
        
        // Ensure output directory exists
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        
        // Write document file
        const outputPath = path.join(outputDir, `${id}.md`);
        fs.writeFileSync(outputPath, docContent);
        console.log(`Generated doc: ${outputPath}`);
        
        return true;
    } catch (error) {
        console.error(`Error generating doc from rule:`, error);
        return false;
    }
}

/**
 * Sync documentation with Cursor rules
 */
function syncCursorRules() {
    console.log('Syncing documentation with Cursor rules...');
    
    // Find documents with rule links
    const ruleDocs = findDocumentsWithRuleLinks();
    console.log(`Found ${ruleDocs.length} documents with rule links.`);
    
    // Process each document
    ruleDocs.forEach(doc => {
        // If document should become a rule
        if (doc.frontmatter.cursor_rule === true) {
            // Determine rule path
            let ruleCategory = doc.frontmatter.rule_category || path.basename(path.dirname(doc.path));
            let rulePath = path.join(RULE_DIR, ruleCategory, `${doc.frontmatter.id || path.basename(doc.path, '.md')}.mdc`);
            
            // Update the rule
            updateRuleFromDoc(rulePath, doc.path);
        }
        
        // If document links to existing rules
        if (doc.frontmatter.cursor_rules && doc.frontmatter.cursor_rules.length > 0) {
            doc.frontmatter.cursor_rules.forEach(ruleRef => {
                const rulePath = path.join(RULE_DIR, ruleRef);
                
                if (doc.frontmatter.auto_generated) {
                    // Document is generated from rule - update from rule
                    updateDocFromRule(doc.path, rulePath);
                } else {
                    // Rule should reflect documentation - update rule
                    updateRuleFromDoc(rulePath, doc.path);
                }
            });
        }
    });
    
    // Find orphaned rules
    const orphanedRules = findOrphanedRules();
    console.log(`Found ${orphanedRules.length} orphaned rules.`);
    
    // Generate documentation from orphaned rules
    orphanedRules.forEach(rule => {
        generateDocFromRule(rule);
    });
    
    console.log('Cursor rules sync completed.');
}

// Run the sync
syncCursorRules(); 