/**
 * Index Page Generator
 * 
 * Creates index pages for the wiki with links to all available documents
 */

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');
const handlebars = require('handlebars');

// Configuration
const CONFIG_FILE = path.resolve('./_config.yml');
const WIKI_DIR = path.resolve('../wiki');
const DOCS_DIR = path.resolve('./_source');

// Load configuration
let config;
try {
    config = yaml.load(fs.readFileSync(CONFIG_FILE, 'utf8'));
} catch (error) {
    console.error('Error loading config file:', error);
    process.exit(1);
}

// Helper functions
const getAllFiles = function(dirPath, arrayOfFiles, extension) {
    if (!fs.existsSync(dirPath)) {
        console.log(`Directory does not exist: ${dirPath}`);
        return arrayOfFiles || [];
    }
    
    const files = fs.readdirSync(dirPath);
    
    arrayOfFiles = arrayOfFiles || [];
    
    files.forEach(file => {
        const filePath = path.join(dirPath, file);
        if (fs.statSync(filePath).isDirectory()) {
            arrayOfFiles = getAllFiles(filePath, arrayOfFiles, extension);
        } else {
            if (file.endsWith(extension)) {
                arrayOfFiles.push(filePath);
            }
        }
    });
    
    return arrayOfFiles;
};

// Parse frontmatter from markdown content
function parseFrontmatter(content) {
    const frontmatterRegex = /^---\s*[\r\n]+([\s\S]*?)[\r\n]+---\s*[\r\n]+([\s\S]*)$/;
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

/**
 * Generate index pages for the wiki
 */
function generateIndexPages() {
    console.log('Generating wiki index pages...');
    
    // Get all markdown files in the docs directory
    const files = getAllFiles(DOCS_DIR, [], '.md');
    
    // Parse all files to get their metadata
    const documents = files.map(file => {
        try {
            const content = fs.readFileSync(file, 'utf8');
            const { frontmatter } = parseFrontmatter(content);
            
            if (!frontmatter) {
                return null;
            }
            
            // Determine section from file path
            const relativePath = path.relative(DOCS_DIR, file);
            const parts = relativePath.split(path.sep);
            const section = parts[0] || 'unknown';
            const category = parts.length > 1 ? parts[1] : 'unknown';
            
            return {
                path: file,
                id: frontmatter.id || path.basename(file, '.md'),
                title: frontmatter.title || path.basename(file, '.md'),
                section,
                category,
                tags: frontmatter.tags || [],
                updated: frontmatter.updated || new Date().toISOString().split('T')[0]
            };
        } catch (error) {
            console.error(`Error processing file ${file}:`, error);
            return null;
        }
    }).filter(Boolean);
    
    // Group documents by section and category
    const documentsBySection = {};
    
    documents.forEach(doc => {
        if (!documentsBySection[doc.section]) {
            documentsBySection[doc.section] = {};
        }
        
        if (!documentsBySection[doc.section][doc.category]) {
            documentsBySection[doc.section][doc.category] = [];
        }
        
        documentsBySection[doc.section][doc.category].push(doc);
    });
    
    // Create the main index page template
    const mainIndexTemplate = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ages of Arda Documentation</title>
    <link rel="stylesheet" href="styles.css">
    <link rel="stylesheet" href="middle-earth-theme.css">
    <script src="sidebar.js" defer></script>
    <script src="middle-earth-interaction.js" defer></script>
</head>
<body>
    <!-- Include sidebar -->
    <div id="sidebar-container"></div>
    
    <div class="content-container">
        <header>
            <h1>Ages of Arda Documentation</h1>
        </header>
        
        <main>
            <div class="index-sections">
                <div class="index-section">
                    <h2>Development Documentation</h2>
                    <p>Technical documentation for Ages of Arda developers</p>
                    <a href="developer-guides/index.html" class="section-link">
                        <div class="section-card">
                            <h3>View Development Documentation</h3>
                            <p>Guides, Architecture, Reference</p>
                        </div>
                    </a>
                </div>
                
                <div class="index-section">
                    <h2>Gameplay Documentation</h2>
                    <p>Game guides and information for players</p>
                    <a href="game-design/index.html" class="section-link">
                        <div class="section-card">
                            <h3>View Gameplay Documentation</h3>
                            <p>Guides, Reference</p>
                        </div>
                    </a>
                </div>
            </div>
        </main>
        
        <footer>
            <p>Ages of Arda - A First Age Angband Variant</p>
        </footer>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            loadSidebar('sidebar.html');
        });
    </script>
</body>
</html>`;
    
    // Create section index page template
    const sectionIndexTemplate = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{sectionTitle}} | Ages of Arda</title>
    <link rel="stylesheet" href="../styles.css">
    <link rel="stylesheet" href="../middle-earth-theme.css">
    <script src="../sidebar.js" defer></script>
    <script src="../middle-earth-interaction.js" defer></script>
</head>
<body class="{{section}}-section">
    <!-- Include sidebar -->
    <div id="sidebar-container"></div>
    
    <div class="content-container">
        <header>
            <h1>{{sectionTitle}}</h1>
            <p>{{sectionDescription}}</p>
        </header>
        
        <main>
            <div class="category-list">
                {{#each categories}}
                <div class="category">
                    <h2>{{this.title}}</h2>
                    <div class="document-list">
                        {{#each this.documents}}
                        <a href="{{this.id}}.html" class="document-link">
                            <div class="document-card">
                                <h3>{{this.title}}</h3>
                                <div class="document-meta">
                                    <span class="updated">Updated: {{this.updated}}</span>
                                </div>
                            </div>
                        </a>
                        {{/each}}
                    </div>
                </div>
                {{/each}}
            </div>
        </main>
        
        <footer>
            <p>Ages of Arda - A First Age Angband Variant</p>
        </footer>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            loadSidebar('../sidebar.html');
        });
    </script>
</body>
</html>`;
    
    // Compile the templates
    const sectionTemplate = handlebars.compile(sectionIndexTemplate);
    
    // Generate the main index page
    fs.writeFileSync(path.join(WIKI_DIR, 'index.html'), mainIndexTemplate);
    console.log(`Generated main index page: ${path.join(WIKI_DIR, 'index.html')}`);
    
    // Generate section index pages
    const sectionMappings = {
        development: {
            directory: config.wiki.development_section,
            title: "Development Documentation",
            description: "Technical documentation for Ages of Arda developers"
        },
        gameplay: {
            directory: config.wiki.gameplay_section,
            title: "Gameplay Documentation",
            description: "Game guides and information for players"
        }
    };
    
    // Process each section
    Object.keys(documentsBySection).forEach(section => {
        const mapping = sectionMappings[section];
        if (!mapping) {
            console.warn(`Unknown section: ${section}`);
            return;
        }
        
        const categories = [];
        
        // Process each category in the section
        Object.keys(documentsBySection[section]).forEach(category => {
            // Sort documents by title
            const documents = documentsBySection[section][category].sort((a, b) => 
                a.title.localeCompare(b.title)
            );
            
            categories.push({
                title: category.charAt(0).toUpperCase() + category.slice(1),
                documents
            });
        });
        
        // Sort categories alphabetically
        categories.sort((a, b) => a.title.localeCompare(b.title));
        
        // Generate the section index page
        const sectionDir = path.join(WIKI_DIR, mapping.directory);
        const indexPath = path.join(sectionDir, 'index.html');
        
        const sectionContent = sectionTemplate({
            sectionTitle: mapping.title,
            sectionDescription: mapping.description,
            section,
            categories
        });
        
        fs.writeFileSync(indexPath, sectionContent);
        console.log(`Generated section index page: ${indexPath}`);
    });
}

// Run the index page generator
generateIndexPages(); 