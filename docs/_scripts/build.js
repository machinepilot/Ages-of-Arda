/**
 * Ages of Arda Documentation Build System
 * 
 * Processes source documentation and generates multiple outputs:
 * - Wiki HTML files
 * - Cursor rules
 * - GitHub documentation
 */

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');
const marked = require('marked');
const handlebars = require('handlebars');
const glob = require('glob');

// Build context for documentation processing
class BuildContext {
    constructor(config) {
        this.config = config;
        this.documents = [];
        this.templates = {};
        this.outputFormats = config.outputs || [];
        this.sourceDir = path.resolve(config.docs_directory || '_source');
    }

    // Load all document sources
    loadDocuments() {
        console.log('Loading documents from:', this.sourceDir);
        
        // Find all markdown files in source directory
        const files = glob.sync(`${this.sourceDir}/**/*.md`);
        
        this.documents = files.map(file => {
            try {
                const content = fs.readFileSync(file, 'utf8');
                const relativePath = path.relative(this.sourceDir, file);
                
                // Parse frontmatter and content
                const { frontmatter, markdown } = this.parseFrontmatter(content);
                
                return {
                    path: file,
                    relativePath,
                    frontmatter: frontmatter || {},
                    content: markdown || content,
                    section: this.getSectionFromPath(relativePath),
                    category: this.getCategoryFromPath(relativePath)
                };
            } catch (error) {
                console.error(`Error loading document ${file}:`, error);
                return null;
            }
        }).filter(Boolean);
        
        console.log(`Loaded ${this.documents.length} documents`);
        return this;
    }
    
    // Extract section from file path
    getSectionFromPath(relativePath) {
        const parts = relativePath.split(path.sep);
        return parts[0] || 'unknown';
    }
    
    // Extract category from file path
    getCategoryFromPath(relativePath) {
        const parts = relativePath.split(path.sep);
        return parts.length > 1 ? parts[1] : 'unknown';
    }

    // Parse frontmatter from markdown content
    parseFrontmatter(content) {
        const frontmatterRegex = /^---\n([\s\S]*?)\n---\n([\s\S]*)$/;
        const match = content.match(frontmatterRegex);
        
        if (!match) {
            return { frontmatter: null, markdown: content };
        }
        
        try {
            const frontmatter = yaml.load(match[1]);
            const markdown = match[2];
            return { frontmatter, markdown };
        } catch (error) {
            console.error('Error parsing frontmatter:', error);
            return { frontmatter: null, markdown: content };
        }
    }

    // Load template files
    loadTemplates() {
        const templateDir = path.resolve('./_templates');
        
        console.log('Loading templates from:', templateDir);
        
        try {
            const files = glob.sync(path.join(templateDir, '**', '*.hbs'));
            console.log('Template files found:', files);
            
            files.forEach(file => {
                const templateName = path.basename(file, '.hbs');
                const templateContent = fs.readFileSync(file, 'utf8');
                this.templates[templateName] = handlebars.compile(templateContent);
            });
            
            console.log(`Loaded ${Object.keys(this.templates).length} templates`);
        } catch (error) {
            console.error('Error loading templates:', error);
        }
        
        return this;
    }

    // Generate all outputs
    generateOutputs() {
        console.log('Generating outputs...');
        
        // Process each output format
        this.outputFormats.forEach(output => {
            if (!output.active) {
                console.log(`Skipping inactive output: ${output.name}`);
                return;
            }
            
            console.log(`Generating output: ${output.name}`);
            
            switch (output.name) {
                case 'wiki':
                    this.generateWikiOutput(output);
                    break;
                case 'cursor_rules':
                    this.generateCursorRules(output);
                    break;
                case 'github_docs':
                    this.generateGithubDocs(output);
                    break;
                default:
                    console.warn(`Unknown output format: ${output.name}`);
            }
        });
        
        return this;
    }

    // Generate wiki website files
    generateWikiOutput(output) {
        console.log('Generating wiki output...');
        
        const outputPath = path.resolve(output.path);
        const template = this.templates[output.template];
        
        if (!template) {
            console.error(`Template not found: ${output.template}`);
            return;
        }
        
        // Process each document for wiki output
        this.documents.forEach(doc => {
            // Determine output path based on section
            let targetDir;
            if (doc.section === 'development') {
                targetDir = path.join(outputPath, this.config.wiki.development_section);
            } else if (doc.section === 'gameplay') {
                targetDir = path.join(outputPath, this.config.wiki.gameplay_section);
            } else {
                targetDir = outputPath;
            }
            
            // Create directory if it doesn't exist
            if (!fs.existsSync(targetDir)) {
                fs.mkdirSync(targetDir, { recursive: true });
            }
            
            // Convert markdown to HTML
            const htmlContent = marked.parse(doc.content);
            
            // Generate HTML file name
            const descriptor = doc.frontmatter.id || path.basename(doc.path, '.md');
            const htmlFileName = `${descriptor}.html`;
            const outputFilePath = path.join(targetDir, htmlFileName);
            
            // Render the template with document content
            const rendered = template({
                title: doc.frontmatter.title || 'Untitled',
                content: htmlContent,
                frontmatter: doc.frontmatter,
                section: doc.section,
                category: doc.category
            });
            
            // Write the HTML file
            fs.writeFileSync(outputFilePath, rendered);
            console.log(`Generated wiki page: ${outputFilePath}`);
        });
    }

    // Generate Cursor rules files
    generateCursorRules(output) {
        console.log('Generating Cursor rules...');
        
        const outputPath = path.resolve(output.path);
        const template = this.templates[output.template];
        
        if (!template) {
            console.error(`Template not found: ${output.template}`);
            return;
        }
        
        // Filter documents that should be converted to rules
        const ruleDocuments = this.documents.filter(doc => 
            doc.frontmatter.cursor_rule === true || 
            (doc.frontmatter.cursor_rules && doc.frontmatter.cursor_rules.length > 0)
        );
        
        ruleDocuments.forEach(doc => {
            // Determine rule directory
            let ruleCategory = doc.frontmatter.rule_category || doc.category;
            let targetDir = path.join(outputPath, ruleCategory);
            
            // Create directory if it doesn't exist
            if (!fs.existsSync(targetDir)) {
                fs.mkdirSync(targetDir, { recursive: true });
            }
            
            // Generate rule file name (.mdc extension)
            const descriptor = doc.frontmatter.id || path.basename(doc.path, '.md');
            const ruleFileName = `${descriptor}.mdc`;
            const outputFilePath = path.join(targetDir, ruleFileName);
            
            // Build frontmatter for the rule
            const ruleFrontmatter = {
                title: doc.frontmatter.title || 'Untitled Rule',
                glob: doc.frontmatter.glob || "**/*",
                priority: doc.frontmatter.priority || 500,
                related: doc.frontmatter.related || []
            };
            
            // Render the rule template
            const rendered = template({
                frontmatter: ruleFrontmatter,
                content: doc.content
            });
            
            // Write the rule file
            fs.writeFileSync(outputFilePath, rendered);
            console.log(`Generated cursor rule: ${outputFilePath}`);
        });
    }

    // Generate GitHub documentation files
    generateGithubDocs(output) {
        console.log('Generating GitHub documentation...');
        
        const outputPath = path.resolve(output.path);
        const template = this.templates[output.template];
        
        if (!template) {
            console.error(`Template not found: ${output.template}`);
            return;
        }
        
        // Filter documents that should be published as GitHub docs
        const githubDocs = this.documents.filter(doc => 
            doc.frontmatter.github_doc === true || 
            doc.frontmatter.publish_to && doc.frontmatter.publish_to.includes('github')
        );
        
        githubDocs.forEach(doc => {
            // Determine output path based on frontmatter
            let outputDir = outputPath;
            if (doc.frontmatter.github_path) {
                outputDir = path.join(outputPath, doc.frontmatter.github_path);
                
                // Create directory if it doesn't exist
                if (!fs.existsSync(outputDir)) {
                    fs.mkdirSync(outputDir, { recursive: true });
                }
            }
            
            // Generate file name
            const fileName = doc.frontmatter.github_filename || 
                             (doc.frontmatter.id ? `${doc.frontmatter.id}.md` : path.basename(doc.path));
            
            const outputFilePath = path.join(outputDir, fileName);
            
            // Render the template
            const rendered = template({
                frontmatter: doc.frontmatter,
                content: doc.content
            });
            
            // Write the file
            fs.writeFileSync(outputFilePath, rendered);
            console.log(`Generated GitHub doc: ${outputFilePath}`);
        });
    }
}

// Main function to run the build process
function main() {
    try {
        // Load configuration
        const configPath = path.resolve('./_config.yml');
        const config = yaml.load(fs.readFileSync(configPath, 'utf8'));
        
        console.log('Loaded configuration:', configPath);
        
        // Create build context
        const context = new BuildContext(config);
        
        // Run build process
        context
            .loadTemplates()
            .loadDocuments()
            .generateOutputs();
        
        console.log('Documentation build completed successfully');
    } catch (error) {
        console.error('Error building documentation:', error);
        process.exit(1);
    }
}

// Run the build
main(); 