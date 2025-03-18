// Get the root path based on the current page
function getRootPath() {
    const path = window.location.pathname;
    const parts = path.split('/');
    
    // If we're in a subdirectory (developer-guides or game-design)
    if (parts.length > 2) {
        return '../';
    }
    
    return './';
}

// Load sidebar content
function loadSidebar(sidebarPath) {
    const rootPath = getRootPath();
    const xhr = new XMLHttpRequest();
    
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            document.getElementById('sidebar-container').innerHTML = xhr.responseText;
            
            // Update links to be relative to the current page
            const links = document.querySelectorAll('#sidebar-container a');
            links.forEach(link => {
                // Skip if the link is already absolute
                if (link.href.startsWith('http')) {
                    return;
                }
                
                // Fix the relative path
                const href = link.getAttribute('href');
                if (href && !href.startsWith('/') && !href.startsWith('http')) {
                    link.href = rootPath + href;
                }
            });
            
            // Add active class to current page link
            const currentPath = window.location.pathname;
            const currentPageLink = document.querySelector(`#sidebar-container a[href$="${currentPath}"]`);
            if (currentPageLink) {
                currentPageLink.classList.add('active');
                
                // Expand parent if in a dropdown
                const parentDropdown = currentPageLink.closest('.dropdown-content');
                if (parentDropdown) {
                    parentDropdown.style.display = 'block';
                    parentDropdown.previousElementSibling.classList.add('active');
                }
            }
            
            // Set up dropdown toggles
            initializeSidebar();
        }
    };
    
    xhr.open('GET', rootPath + sidebarPath, true);
    xhr.send();
}

// Initialize sidebar interactions
function initializeSidebar() {
    // Toggle sidebar on mobile
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            const sidebar = document.querySelector('.sidebar');
            sidebar.classList.toggle('open');
        });
    }
    
    // Toggle dropdowns
    const dropdownButtons = document.querySelectorAll('.dropdown-btn');
    dropdownButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.classList.toggle('active');
            const dropdownContent = this.nextElementSibling;
            if (dropdownContent.style.display === 'block') {
                dropdownContent.style.display = 'none';
            } else {
                dropdownContent.style.display = 'block';
            }
        });
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