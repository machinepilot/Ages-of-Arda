// Function to load the sidebar content
function loadSidebar() {
    // Determine the relative path to the root based on current page depth
    const path = getPathToRoot();
    
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
                
                // Highlight the current page in the navigation
                highlightCurrentPage();
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

// Create a fallback sidebar with minimal navigation if the sidebar fails to load
function createFallbackSidebar() {
    const sidebarElement = document.querySelector('.sidebar');
    if (sidebarElement) {
        const path = getPathToRoot();
        sidebarElement.innerHTML = `
            <h2>Navigation</h2>
            <ul>
                <li><a href="${path}index.html">Home</a></li>
                <li><a href="${path}development-story.html">Development Story</a></li>
            </ul>
        `;
    }
}

// Determine the path to the root directory based on the current URL
function getPathToRoot() {
    let path = '';
    const pathParts = window.location.pathname.split('/');
    const fileName = pathParts[pathParts.length - 1];
    
    // Filter out empty parts and Windows drive letters (like C:)
    const filteredParts = pathParts.filter(part => 
        part !== '' && 
        !part.includes(':') && 
        part !== 'index.html'
    );
    
    // If we're at the root or directly in the wiki directory, no need for ../
    if (filteredParts.length <= 1 || fileName === '' || fileName === 'index.html') {
        return './';
    }
    
    // Add '../' for each directory level deep we are
    for (let i = 1; i < filteredParts.length; i++) {
        path += '../';
    }
    
    return path;
}

// Fix the links in the sidebar to point to the correct relative path
function fixSidebarLinks(path) {
    if (path === './') return; // No need to fix links at root level
    
    const links = document.querySelectorAll('.sidebar a');
    links.forEach(link => {
        const href = link.getAttribute('href');
        
        // Skip links that are already absolute or have a protocol
        if (!href || href.startsWith('http') || href.startsWith('//') || href.startsWith('#')) {
            return;
        }
        
        // Fix the link based on its current path
        if (href.startsWith('./')) {
            // Convert ./file.html to ../file.html or ../../file.html depending on depth
            link.setAttribute('href', path + href.substring(2));
        } else if (!href.startsWith('../')) {
            // For links like 'file.html', add the path prefix
            link.setAttribute('href', path + href);
        }
        
        // Special case for the home link - ensure it goes to the root
        if (href === 'index.html' || href === './index.html') {
            link.setAttribute('href', path + 'index.html');
        }
    });
    
    // Also fix image sources
    const images = document.querySelectorAll('.sidebar img');
    images.forEach(img => {
        const src = img.getAttribute('src');
        if (src && !src.startsWith('http') && !src.startsWith('//') && !src.startsWith('../')) {
            img.setAttribute('src', path + src);
        }
    });
}

// Highlight the current page in the navigation
function highlightCurrentPage() {
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll('.sidebar a');
    const currentFileName = currentPath.split('/').pop();
    
    links.forEach(link => {
        const href = link.getAttribute('href');
        if (href) {
            const hrefFileName = href.split('/').pop();
            // Check if this link points to the current page
            if (hrefFileName === currentFileName || 
                (currentFileName === '' && hrefFileName === 'index.html')) {
                link.classList.add('active');
                // Also highlight the parent list item
                const parentLi = link.closest('li');
                if (parentLi) {
                    parentLi.classList.add('active');
                }
            }
        }
    });
}

// Load the sidebar when the DOM is ready
document.addEventListener('DOMContentLoaded', loadSidebar); 