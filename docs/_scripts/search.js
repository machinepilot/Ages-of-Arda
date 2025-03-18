/**
 * Ages of Arda Documentation Search System
 * 
 * Generates a search index for all documentation and provides search functionality
 * With support for future lore system integration
 */

const fs = require('fs');
const path = require('path');
const lunr = require('lunr');
const yaml = require('js-yaml');
const marked = require('marked');

// Configuration
let config;
try {
    const CONFIG_FILE = path.resolve('./_config.yml');
    config = yaml.load(fs.readFileSync(CONFIG_FILE, 'utf8'));
} catch (error) {
    console.error('Error loading config file:', error);
    process.exit(1);
}

// Define paths
const SOURCE_DIR = path.resolve('./_source');
const WIKI_DIR = path.resolve('../wiki');

// Helper for getting all markdown files recursively
const getAllMarkdownFiles = function(dirPath, arrayOfFiles) {
    const files = fs.readdirSync(dirPath);
    
    arrayOfFiles = arrayOfFiles || [];
    
    files.forEach(file => {
        const filePath = path.join(dirPath, file);
        if (fs.statSync(filePath).isDirectory()) {
            arrayOfFiles = getAllMarkdownFiles(filePath, arrayOfFiles);
        } else if (file.endsWith('.md')) {
            arrayOfFiles.push(filePath);
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

// Extract plain text from markdown (for indexing)
function extractTextFromMarkdown(markdown) {
    // Create a simple renderer that just returns the text
    const textRenderer = new marked.Renderer();
    textRenderer.paragraph = function(text) { return text + '\n'; };
    textRenderer.heading = function(text) { return text + '\n'; };
    textRenderer.list = function(text) { return text + '\n'; };
    textRenderer.listitem = function(text) { return '- ' + text + '\n'; };
    textRenderer.link = function(href, title, text) { return text; };
    textRenderer.image = function(href, title, text) { return text; };
    textRenderer.code = function(code) { return code + '\n'; };
    
    const html = marked.parse(markdown, { renderer: textRenderer });
    
    // Clean up the HTML to get plain text
    return html.replace(/<[^>]*>/g, '');
}

// Build search index from all markdown files
function buildSearchIndex() {
    console.log('Building search index...');
    
    // Get all markdown files
    const files = getAllMarkdownFiles(SOURCE_DIR);
    console.log(`Found ${files.length} markdown files for indexing`);
    
    // Process each file and prepare for indexing
    const documents = files.map(file => {
        try {
            const content = fs.readFileSync(file, 'utf8');
            const { frontmatter, markdown } = parseFrontmatter(content);
            
            if (!frontmatter) {
                console.warn(`No frontmatter found in ${file}, skipping...`);
                return null;
            }
            
            const relativePath = path.relative(SOURCE_DIR, file);
            const section = relativePath.split(path.sep)[0];
            const category = relativePath.split(path.sep).length > 1 ? relativePath.split(path.sep)[1] : 'unknown';
            
            // Determine URL in the wiki
            let url;
            if (section === 'development') {
                url = `${config.wiki.development_section}/${frontmatter.id || path.basename(file, '.md')}.html`;
            } else if (section === 'gameplay') {
                url = `${config.wiki.gameplay_section}/${frontmatter.id || path.basename(file, '.md')}.html`;
            } else {
                url = `${frontmatter.id || path.basename(file, '.md')}.html`;
            }
            
            // Extract plain text for better indexing
            const plainText = extractTextFromMarkdown(markdown);
            
            return {
                id: frontmatter.id || path.basename(file, '.md'),
                title: frontmatter.title || 'Untitled',
                content: plainText,
                section: section,
                category: category,
                url: url,
                // Store the original document for future reference
                document: {
                    path: file,
                    relativePath: relativePath,
                    frontmatter: frontmatter
                }
            };
        } catch (error) {
            console.error(`Error processing file ${file}:`, error);
            return null;
        }
    }).filter(Boolean);
    
    console.log(`Prepared ${documents.length} documents for indexing`);
    
    // Create a moduler search index structure that can later incorporate lore
    const searchData = {
        documentation: {
            // Build the Lunr index
            index: lunr(function() {
                this.ref('id');
                this.field('title', { boost: 10 });
                this.field('content');
                this.field('section');
                this.field('category');
                
                // Add each document to the index
                documents.forEach(doc => {
                    this.add(doc);
                });
            }),
            
            // Store the document lookup map
            documents: documents.reduce((map, doc) => {
                map[doc.id] = doc;
                return map;
            }, {})
        },
        
        // Reserved for future lore system
        lore: null
    };
    
    // Write the search index to a file
    const outputPath = path.join(WIKI_DIR, 'search-index.json');
    
    // Only save what's needed for client-side search (reduces file size)
    const clientSearchData = {
        documentation: {
            index: searchData.documentation.index,
            documents: Object.keys(searchData.documentation.documents).reduce((map, id) => {
                const doc = searchData.documentation.documents[id];
                map[id] = {
                    id: doc.id,
                    title: doc.title,
                    section: doc.section,
                    category: doc.category,
                    url: doc.url
                };
                return map;
            }, {})
        },
        // Reserved for future lore system
        lore: null
    };
    
    fs.writeFileSync(outputPath, JSON.stringify(clientSearchData));
    console.log(`Search index written to ${outputPath}`);
    
    return searchData;
}

// Function to search the index (server-side) - for future usge
function search(query, options = {}) {
    const searchData = JSON.parse(fs.readFileSync(path.join(WIKI_DIR, 'search-index.json'), 'utf8'));
    
    const results = {
        documentation: [],
        lore: []
    };
    
    // Search documentation
    try {
        const documentationResults = searchData.documentation.index.search(query);
        results.documentation = documentationResults.map(result => {
            const doc = searchData.documentation.documents[result.ref];
            return {
                id: doc.id,
                title: doc.title,
                url: doc.url,
                section: doc.section,
                category: doc.category,
                score: result.score
            };
        });
    } catch (error) {
        console.error('Error searching documentation:', error);
    }
    
    // Reserved for future lore search
    
    return results;
}

// If this script is run directly, build the search index
if (require.main === module) {
    buildSearchIndex();
}

module.exports = {
    buildSearchIndex,
    search
}; 