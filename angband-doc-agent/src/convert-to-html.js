/**
 * Convert Markdown test results to HTML
 * 
 * This script converts the Markdown test results to HTML for better offline viewing.
 */

const fs = require('fs');
const path = require('path');
const marked = require('marked');

// Check if marked is installed
try {
  require.resolve('marked');
} catch (e) {
  console.log('The "marked" package is not installed. Installing now...');
  require('child_process').execSync('npm install marked', { stdio: 'inherit' });
  console.log('Marked installed successfully.');
}

// Configuration
const inputFile = path.join(__dirname, 'mcp-test-results.md');
const outputFile = path.join(__dirname, 'mcp-test-results.html');

// CSS styles for the HTML output
const styles = `
<style>
  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
    background-color: #f9f9f9;
  }
  h1 {
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
  }
  h2 {
    color: #2980b9;
    margin-top: 30px;
  }
  h3 {
    color: #3498db;
    margin-top: 25px;
    border-left: 4px solid #3498db;
    padding-left: 10px;
  }
  h4 {
    color: #16a085;
  }
  strong {
    color: #2c3e50;
  }
  hr {
    border: 0;
    height: 1px;
    background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0));
    margin: 30px 0;
  }
  code {
    background-color: #f8f8f8;
    border: 1px solid #ddd;
    border-radius: 3px;
    font-family: Consolas, Monaco, 'Andale Mono', monospace;
    padding: 2px 4px;
  }
  pre {
    background-color: #f8f8f8;
    border: 1px solid #ddd;
    border-radius: 3px;
    padding: 10px;
    overflow: auto;
  }
  blockquote {
    border-left: 4px solid #ccc;
    margin-left: 0;
    padding-left: 15px;
    color: #555;
  }
  .narrative {
    background-color: #f0f7fb;
    border-left: 5px solid #3498db;
    padding: 15px;
    margin: 15px 0;
    border-radius: 3px;
  }
  .metadata {
    background-color: #f8f9fa;
    padding: 10px;
    border-radius: 3px;
    margin-bottom: 15px;
  }
  .importance-high {
    color: #e74c3c;
    font-weight: bold;
  }
  .importance-medium {
    color: #f39c12;
    font-weight: bold;
  }
  .importance-low {
    color: #27ae60;
    font-weight: bold;
  }
</style>
`;

// Convert Markdown to HTML
function convertToHtml() {
  try {
    // Read the Markdown file
    const markdown = fs.readFileSync(inputFile, 'utf8');
    
    // Convert Markdown to HTML
    let html = marked.parse(markdown);
    
    // Add custom styling for narratives
    html = html.replace(/<p><strong>Narrative:<\/strong><\/p>\n<p>([^<]+)<\/p>/g, 
      '<p><strong>Narrative:</strong></p><div class="narrative">$1</div>');
    
    // Add custom styling for metadata
    html = html.replace(/<p><strong>(Style|Tone|Character|Is Spoken|Importance):<\/strong>([^<]+)<\/p>/g, 
      '<p class="metadata"><strong>$1:</strong>$2</p>');
    
    // Add importance classes
    html = html.replace(/Importance:<\/strong> (\d+)/g, (match, importance) => {
      const importanceNum = parseInt(importance);
      let importanceClass = 'importance-medium';
      
      if (importanceNum >= 80) {
        importanceClass = 'importance-high';
      } else if (importanceNum < 50) {
        importanceClass = 'importance-low';
      }
      
      return `Importance:</strong> <span class="${importanceClass}">${importance}</span>`;
    });
    
    // Create the complete HTML document
    const htmlDocument = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lute the Bard - MCP Test Results</title>
  ${styles}
</head>
<body>
  ${html}
  <footer style="margin-top: 50px; text-align: center; color: #7f8c8d; font-size: 0.9em;">
    <p>Generated on ${new Date().toLocaleString()} | Tower of Babel - Angband Variant</p>
  </footer>
</body>
</html>
    `;
    
    // Write the HTML file
    fs.writeFileSync(outputFile, htmlDocument);
    
    console.log(`Conversion complete! HTML file saved to: ${outputFile}`);
  } catch (error) {
    console.error('Error converting Markdown to HTML:', error);
  }
}

// Run the conversion
convertToHtml(); 