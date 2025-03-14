// Function to load the sidebar content
function loadSidebar() {
    // Determine the relative path to the root based on current page depth
    let path = '';
    const pathParts = window.location.pathname.split('/');
    const fileName = pathParts[pathParts.length - 1];
    const isInSubdirectory = pathParts.length > 2 && fileName !== '';
    
    // Add '../' for each level of depth
    if (isInSubdirectory) {
        const depth = pathParts.slice(0, -1).filter(part => part !== '' && !part.includes(':')).length - 1;
        for (let i = 0; i < depth; i++) {
            path += '../';
        }
    }
    
    // Default to current directory if we're at root
    if (path === '') {
        path = './';
    }
    
    console.log('Path prefix for sidebar:', path);
    
    // Load the sidebar content
    fetch(path + 'sidebar.html')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to load sidebar: ${response.status} ${response.statusText}`);
            }
            return response.text();
        })
        .then(data => {
            // Replace the sidebar content
            const sidebarElement = document.querySelector('.sidebar');
            if (sidebarElement) {
                sidebarElement.innerHTML = data;
                
                // Fix the links in the sidebar based on current depth
                fixSidebarLinks(path);
            } else {
                console.error('Sidebar element not found in the document');
            }
        })
        .catch(error => {
            console.error('Error loading sidebar:', error);
            // Fallback: If sidebar.html fails to load, create a minimal navigation
            createFallbackSidebar();
        });
}

// Function to create a fallback sidebar if the sidebar.html fails to load
function createFallbackSidebar() {
    const sidebarElement = document.querySelector('.sidebar');
    if (sidebarElement) {
        sidebarElement.innerHTML = `
            <h2>Navigation</h2>
            <ul>
                <li><a href="${getPathToRoot()}index.html">Home</a></li>
                <li><a href="${getPathToRoot()}ai-architecture/overview.html">AI Overview</a></li>
            </ul>
        `;
    }
}

// Helper function to get path to root
function getPathToRoot() {
    let path = '';
    const pathParts = window.location.pathname.split('/');
    const fileName = pathParts[pathParts.length - 1];
    const isInSubdirectory = pathParts.length > 2 && fileName !== '';
    
    if (isInSubdirectory) {
        const depth = pathParts.slice(0, -1).filter(part => part !== '' && !part.includes(':')).length - 1;
        for (let i = 0; i < depth; i++) {
            path += '../';
        }
    }
    
    return path === '' ? './' : path;
}

// Function to fix links in the sidebar based on page depth
function fixSidebarLinks(path) {
    const links = document.querySelectorAll('.sidebar a');
    
    links.forEach(link => {
        // Don't modify links that are already absolute or have protocol
        if (!link.href.startsWith('http') && !link.href.startsWith('javascript:')) {
            // Get the href value
            const href = link.getAttribute('href');
            
            // If it's a relative link (doesn't start with /)
            if (href && !href.startsWith('/')) {
                // Update the href with the correct path
                link.href = path + href;
            }
        }
    });
    
    // Fix image paths in the sidebar
    const images = document.querySelectorAll('.sidebar img');
    images.forEach(img => {
        const src = img.getAttribute('src');
        if (src && !src.startsWith('/') && !src.startsWith('http')) {
            img.src = path + src;
        }
    });
    
    // Highlight the current page in the navigation
    highlightCurrentPage();
}

// Function to highlight the current page in the navigation
function highlightCurrentPage() {
    const currentPath = window.location.pathname;
    const currentFile = currentPath.split('/').pop();
    
    const links = document.querySelectorAll('.sidebar a');
    links.forEach(link => {
        const linkPath = link.getAttribute('href');
        const linkFile = linkPath.split('/').pop();
        
        if (linkFile === currentFile || 
            (currentPath.includes(linkPath) && linkPath !== 'index.html')) {
            link.style.fontWeight = 'bold';
            link.style.textDecoration = 'underline';
            
            // Also highlight the parent section
            const parentLi = link.closest('li');
            if (parentLi) {
                parentLi.style.backgroundColor = 'rgba(0, 0, 0, 0.05)';
            }
        }
    });
}

// Load the sidebar when the document is ready
document.addEventListener('DOMContentLoaded', loadSidebar); 