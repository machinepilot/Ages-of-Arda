/**
 * Ages of Arda Documentation Search
 * Client-side search implementation using pre-built Lunr.js index
 */

// Search state
let searchIndex = null;
let documentsMap = {};
let isSearchLoaded = false;
let isSearching = false;
let minSearchChars = 3;

// DOM Elements
let searchInput;
let searchButton;
let searchSuggestions;
let loadingIndicator;

// Initialize search functionality when the page is loaded
document.addEventListener('DOMContentLoaded', initializeSearch);

// Main initialization function
function initializeSearch() {
    // Create search UI if it doesn't exist
    createSearchUI();
    
    // Set up event listeners for search
    setupEventListeners();
    
    // Preload search index for better UX
    setTimeout(loadSearchIndex, 1000);
}

// Create the search UI elements and add them to the page
function createSearchUI() {
    // Create header if not exists
    createHeader();
    
    // Create search container
    const searchContainer = document.createElement('div');
    searchContainer.className = 'search-container';
    
    // Create search input
    searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = 'Search documentation...';
    searchInput.className = 'search-input';
    searchInput.setAttribute('aria-label', 'Search documentation');
    
    // Create search button
    searchButton = document.createElement('button');
    searchButton.className = 'search-button';
    searchButton.innerHTML = '<span class="search-icon">🔍</span>';
    searchButton.setAttribute('aria-label', 'Search');
    
    // Create loading indicator
    loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'search-loading';
    loadingIndicator.innerHTML = '<span class="loading-spinner"></span>';
    loadingIndicator.style.display = 'none';
    
    // Create search suggestions container
    searchSuggestions = document.createElement('div');
    searchSuggestions.className = 'search-suggestions';
    searchSuggestions.style.display = 'none';
    
    // Assemble the search UI
    searchContainer.appendChild(searchInput);
    searchContainer.appendChild(searchButton);
    searchContainer.appendChild(loadingIndicator);
    searchContainer.appendChild(searchSuggestions);
    
    // Add search to the header
    const header = document.querySelector('.main-header');
    if (header) {
        header.appendChild(searchContainer);
    }
}

// Create the main header for the layout if not exists
function createHeader() {
    if (document.querySelector('.main-header')) {
        return;
    }
    
    // Determine the path to the root directory
    const rootPath = getRootPath();
    
    // Create header
    const header = document.createElement('div');
    header.className = 'main-header';
    
    // Create left side with logo and title
    const headerLeft = document.createElement('div');
    headerLeft.className = 'header-left';
    
    // Add logo
    const logoImg = document.createElement('img');
    logoImg.src = `${rootPath}images/ages-of-arda-logo.svg`;
    logoImg.alt = 'Ages of Arda';
    logoImg.className = 'header-logo';
    
    // Add title
    const title = document.createElement('h1');
    title.className = 'header-title';
    title.textContent = 'Ages of Arda';
    
    // Add mobile menu toggle
    const menuToggle = document.createElement('button');
    menuToggle.className = 'mobile-menu-toggle';
    menuToggle.innerHTML = '☰';
    menuToggle.setAttribute('aria-label', 'Toggle navigation');
    
    // Assemble the header
    headerLeft.appendChild(logoImg);
    headerLeft.appendChild(title);
    header.appendChild(menuToggle);
    header.appendChild(headerLeft);
    
    // Add to the body
    document.body.insertBefore(header, document.body.firstChild);
    
    // Setup mobile menu toggle
    menuToggle.addEventListener('click', () => {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.classList.toggle('active');
        }
    });
}

// Set up sidebar enhancements
function setupSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (!sidebar) return;
    
    // Add toggle button to collapse/expand sidebar
    const toggleButton = document.createElement('button');
    toggleButton.className = 'sidebar-toggle';
    toggleButton.innerHTML = '<span class="sidebar-toggle-icon">◀</span>';
    toggleButton.setAttribute('aria-label', 'Toggle sidebar');
    
    sidebar.appendChild(toggleButton);
    
    // Convert h2 headers to collapsible sections
    const headers = sidebar.querySelectorAll('h2');
    headers.forEach(header => {
        // Create a section title
        const sectionTitle = document.createElement('div');
        sectionTitle.className = 'sidebar-section-title';
        sectionTitle.innerHTML = `
            <span>${header.textContent}</span>
            <span class="section-toggle">▼</span>
        `;
        
        // Find the next ul element
        const nextUl = header.nextElementSibling;
        if (nextUl && nextUl.tagName === 'UL') {
            // Create a section container
            const section = document.createElement('div');
            section.className = 'sidebar-section';
            
            // Create content container
            const content = document.createElement('div');
            content.className = 'sidebar-section-content expanded';
            content.appendChild(nextUl.cloneNode(true));
            
            // Add toggle functionality
            sectionTitle.addEventListener('click', () => {
                content.classList.toggle('expanded');
                const toggle = sectionTitle.querySelector('.section-toggle');
                toggle.textContent = content.classList.contains('expanded') ? '▼' : '▶';
            });
            
            // Replace the original elements
            section.appendChild(sectionTitle);
            section.appendChild(content);
            header.parentNode.replaceChild(section, header);
            nextUl.remove();
        }
    });
    
    // Add click handler for the toggle button
    toggleButton.addEventListener('click', () => {
        sidebar.classList.toggle('sidebar-collapsed');
        document.querySelector('.content-container').classList.toggle('content-container-full');
    });
}

// Set up all event listeners
function setupEventListeners() {
    // Add search input event listener with debounce
    let debounceTimeout;
    searchInput.addEventListener('input', () => {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(handleSearchInput, 300);
    });
    
    // Search button click
    searchButton.addEventListener('click', () => {
        searchInput.focus();
    });
    
    // Keyboard navigation
    searchInput.addEventListener('keydown', handleSearchKeyboard);
    
    // Global keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl+K or / to focus search (when not already in an input)
        if ((e.ctrlKey && e.key === 'k') || 
            (e.key === '/' && document.activeElement.tagName !== 'INPUT' && 
             document.activeElement.tagName !== 'TEXTAREA')) {
            e.preventDefault();
            searchInput.focus();
        }
        
        // Escape to clear search
        if (e.key === 'Escape' && document.activeElement === searchInput) {
            searchInput.value = '';
            hideSuggestions();
            searchInput.blur();
        }
    });
    
    // Click outside to close suggestions
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !searchSuggestions.contains(e.target)) {
            hideSuggestions();
        }
    });
    
    // Setup sidebar once DOM is fully loaded
    setTimeout(setupSidebar, 500);
    
    // Setup reading progress indicator
    setupReadingProgress();
}

// Handle keyboard navigation in search suggestions
function handleSearchKeyboard(e) {
    // Only handle when suggestions are visible
    if (searchSuggestions.style.display !== 'block') return;
    
    const suggestions = searchSuggestions.querySelectorAll('.search-suggestion');
    if (suggestions.length === 0) return;
    
    // Find the currently active suggestion
    const activeIndex = Array.from(suggestions).findIndex(
        item => item.classList.contains('active')
    );
    
    switch (e.key) {
        case 'ArrowDown':
            e.preventDefault();
            navigateResults(activeIndex < suggestions.length - 1 ? activeIndex + 1 : 0);
            break;
            
        case 'ArrowUp':
            e.preventDefault();
            navigateResults(activeIndex > 0 ? activeIndex - 1 : suggestions.length - 1);
            break;
            
        case 'Enter':
            e.preventDefault();
            const activeSuggestion = searchSuggestions.querySelector('.search-suggestion.active');
            if (activeSuggestion) {
                const link = activeSuggestion.getAttribute('data-url');
                if (link) window.location.href = link;
            }
            break;
    }
}

// Navigate between search results
function navigateResults(index) {
    const suggestions = searchSuggestions.querySelectorAll('.search-suggestion');
    
    // Remove active class from all suggestions
    suggestions.forEach(item => item.classList.remove('active'));
    
    // Add active class to the current suggestion
    if (suggestions[index]) {
        suggestions[index].classList.add('active');
        suggestions[index].scrollIntoView({
            block: 'nearest',
            behavior: 'smooth'
        });
    }
}

// Handle input in the search field
function handleSearchInput() {
    const query = searchInput.value.trim();
    
    if (query.length >= minSearchChars) {
        if (isSearchLoaded) {
            performSearch(query);
        } else {
            loadSearchIndex();
        }
    } else {
        hideSuggestions();
    }
}

// Show the search suggestions
function showSuggestions() {
    searchSuggestions.style.display = 'block';
}

// Hide the search suggestions
function hideSuggestions() {
    searchSuggestions.style.display = 'none';
}

// Load the search index if not already loaded
function loadSearchIndex() {
    if (isSearchLoaded || isSearching) return;
    
    isSearching = true;
    loadingIndicator.style.display = 'block';
    
    // Determine the path to the root directory
    const rootPath = getRootPath();
    
    fetch(`${rootPath}search-index.json`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load search index');
            }
            return response.json();
        })
        .then(data => {
            searchIndex = data.documentation.index;
            documentsMap = data.documentation.documents;
            isSearchLoaded = true;
            isSearching = false;
            loadingIndicator.style.display = 'none';
            
            // If there's a query in the input, perform the search
            const query = searchInput.value.trim();
            if (query.length >= minSearchChars) {
                performSearch(query);
            }
        })
        .catch(error => {
            console.error('Error loading search index:', error);
            isSearching = false;
            loadingIndicator.style.display = 'none';
        });
}

// Execute the search with the given query
function performSearch(query) {
    if (!searchIndex) return;
    
    try {
        // Set a default empty results array
        let results = [];
        
        // Perform the search using Lunr.js
        results = lunr.Index.load(searchIndex).search(query);
        
        // Limit the number of results to improve performance
        results = results.slice(0, 10);
        
        // Format and display the results
        displaySuggestions(query, results);
    } catch (error) {
        console.error('Search error:', error);
        // Show an error message in the suggestions
        searchSuggestions.innerHTML = `
            <div class="search-suggestion">
                Error performing search. Please try a different query.
            </div>
        `;
        showSuggestions();
    }
}

// Display search results as suggestions
function displaySuggestions(query, results) {
    // Clear previous results
    searchSuggestions.innerHTML = '';
    
    if (results.length === 0) {
        // No results message
        searchSuggestions.innerHTML = `
            <div class="search-suggestion">
                No matching documents found for "${query}".
            </div>
        `;
    } else {
        // Display each result as a suggestion
        results.forEach((result, index) => {
            const doc = documentsMap[result.ref];
            if (!doc) return;
            
            // Determine the full URL (accounting for nested directories)
            const rootPath = getRootPath();
            const fullUrl = `${rootPath}${doc.url}`;
            
            const suggestionEl = document.createElement('div');
            suggestionEl.className = 'search-suggestion';
            suggestionEl.setAttribute('data-url', fullUrl);
            if (index === 0) suggestionEl.classList.add('active');
            
            suggestionEl.innerHTML = `
                <div class="search-suggestion-title">${doc.title}</div>
                <div class="search-suggestion-path">${doc.section}/${doc.category}</div>
            `;
            
            // Add click handler
            suggestionEl.addEventListener('click', () => {
                window.location.href = fullUrl;
            });
            
            searchSuggestions.appendChild(suggestionEl);
        });
    }
    
    showSuggestions();
}

// Setup reading progress indicator
function setupReadingProgress() {
    // Only create on content pages
    if (!document.querySelector('main')) return;
    
    // Create progress bar
    const progressBar = document.createElement('div');
    progressBar.className = 'reading-progress';
    document.body.appendChild(progressBar);
    
    // Update progress bar on scroll
    window.addEventListener('scroll', () => {
        const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
        const height = 
            document.documentElement.scrollHeight - 
            document.documentElement.clientHeight;
        
        const scrollPercentage = (scrollTop / height) * 100;
        progressBar.style.width = scrollPercentage + '%';
    });
}

// Get the path to the root directory
function getRootPath() {
    const path = window.location.pathname;
    const parts = path.split('/');
    
    // If we're in a subdirectory (developer-guides or game-design)
    if (parts.length > 2) {
        return '../';
    }
    
    return './';
}
