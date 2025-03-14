// Middle-earth Interaction Scripts

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the Middle-earth theme elements
    initializeArdaCompass();
    initializeTimeline();
    initializeMistAnimations();
    initializeTorchlightEffects();
    initializeLoreNuggets();
    initializeRelicCards();
    initializeCompanionGear();
    initializeScribesQuill();
    
    // Apply theme styles to existing content
    applyThemeStyles();
});

// Arda Compass - Draggable Widget
function initializeArdaCompass() {
    // Create compass element if it doesn't exist
    if (!document.querySelector('.arda-compass')) {
        const compass = document.createElement('div');
        compass.className = 'arda-compass';
        document.body.appendChild(compass);
        
        // Make compass draggable
        makeElementDraggable(compass);
        
        // Add rotation functionality
        compass.addEventListener('wheel', function(e) {
            e.preventDefault();
            
            // Rotate the compass
            const currentRotation = getComputedStyle(compass).getPropertyValue('transform');
            let newRotation = 0;
            
            if (currentRotation !== 'none') {
                const values = currentRotation.split('(')[1].split(')')[0].split(',');
                const angle = Math.round(Math.atan2(values[1], values[0]) * (180/Math.PI));
                newRotation = angle + (e.deltaY > 0 ? 15 : -15);
            } else {
                newRotation = e.deltaY > 0 ? 15 : -15;
            }
            
            compass.style.transform = `rotate(${newRotation}deg)`;
            
            // Change page based on rotation
            if (newRotation % 120 < 15 && newRotation % 120 > -15) {
                // First Age section
                highlightAge('first');
            } else if (newRotation % 120 < 135 && newRotation % 120 > 105) {
                // Second Age section
                highlightAge('second');
            } else if (newRotation % 120 < -105 && newRotation % 120 > -135) {
                // Third Age section
                highlightAge('third');
            }
        });
        
        // Add click functionality
        compass.addEventListener('click', function() {
            // Toggle visibility of the timeline
            const timeline = document.querySelector('.age-timeline');
            if (timeline) {
                timeline.style.display = timeline.style.display === 'none' ? 'flex' : 'none';
            }
        });
    }
}

// Timeline Bar with Age Orbs
function initializeTimeline() {
    // Create timeline if it doesn't exist
    if (!document.querySelector('.age-timeline')) {
        const timeline = document.createElement('div');
        timeline.className = 'age-timeline';
        
        // Create the three orbs for different ages
        const firstAgeOrb = createTimelineOrb('first-age', 'I');
        const secondAgeOrb = createTimelineOrb('second-age', 'II');
        const thirdAgeOrb = createTimelineOrb('third-age', 'III');
        
        // Create connectors between orbs
        const connector1 = document.createElement('div');
        connector1.className = 'timeline-connector';
        
        const connector2 = document.createElement('div');
        connector2.className = 'timeline-connector';
        
        // Append all elements to timeline
        timeline.appendChild(firstAgeOrb);
        timeline.appendChild(connector1);
        timeline.appendChild(secondAgeOrb);
        timeline.appendChild(connector2);
        timeline.appendChild(thirdAgeOrb);
        
        // Insert timeline at the top of the content
        const content = document.getElementById('content');
        if (content) {
            content.insertBefore(timeline, content.firstChild);
        } else {
            document.body.insertBefore(timeline, document.body.firstChild);
        }
        
        // Add draggable functionality to timeline
        makeTimelineDraggable(timeline);
    }
}

// Create a timeline orb for a specific age
function createTimelineOrb(className, label) {
    const orb = document.createElement('div');
    orb.className = `timeline-orb ${className}`;
    orb.textContent = label;
    
    // Add click functionality to navigate to age section
    orb.addEventListener('click', function() {
        // Simple navigation to corresponding sections
        const age = className.split('-')[0];
        
        if (age === 'first') {
            window.location.href = getPathToRoot() + 'game-design/timeline.html#first-age';
        } else if (age === 'second') {
            window.location.href = getPathToRoot() + 'game-design/timeline.html#second-age';
        } else if (age === 'third') {
            window.location.href = getPathToRoot() + 'game-design/timeline.html#third-age';
        }
    });
    
    return orb;
}

// Make timeline draggable horizontally
function makeTimelineDraggable(timeline) {
    let isDragging = false;
    let startPosition = 0;
    let startScroll = 0;
    
    timeline.addEventListener('mousedown', function(e) {
        isDragging = true;
        startPosition = e.clientX;
        startScroll = timeline.scrollLeft;
        timeline.style.cursor = 'grabbing';
    });
    
    document.addEventListener('mousemove', function(e) {
        if (!isDragging) return;
        
        const distance = e.clientX - startPosition;
        timeline.scrollLeft = startScroll - distance;
        
        // Change appearance based on scroll position
        const scrollPercent = timeline.scrollLeft / (timeline.scrollWidth - timeline.clientWidth);
        
        if (scrollPercent < 0.33) {
            highlightAge('first');
        } else if (scrollPercent < 0.66) {
            highlightAge('second');
        } else {
            highlightAge('third');
        }
    });
    
    document.addEventListener('mouseup', function() {
        if (isDragging) {
            isDragging = false;
            timeline.style.cursor = 'grab';
        }
    });
}

// Highlight the active age in the timeline
function highlightAge(age) {
    const orbs = document.querySelectorAll('.timeline-orb');
    orbs.forEach(orb => {
        orb.style.transform = 'scale(1)';
        orb.style.boxShadow = '0 0 15px var(--shadow-dark)';
    });
    
    const activeOrb = document.querySelector(`.timeline-orb.${age}-age`);
    if (activeOrb) {
        activeOrb.style.transform = 'scale(1.2)';
        activeOrb.style.boxShadow = '0 0 20px var(--shadow-dark), 0 0 40px var(--elvish-glow)';
    }
}

// Mist Animation overlays for lore sections
function initializeMistAnimations() {
    // Add mist overlay to lore sections
    const loreSections = document.querySelectorAll('.card, .feature-card');
    loreSections.forEach(section => {
        const mist = document.createElement('div');
        mist.className = 'mist-overlay';
        section.style.position = 'relative';
        section.appendChild(mist);
    });
}

// Torchlight flicker effect for companion sections
function initializeTorchlightEffects() {
    // Find companion related sections
    const companionSections = findCompanionSections();
    
    companionSections.forEach(section => {
        const torch = document.createElement('div');
        torch.className = 'torchlight';
        section.style.position = 'relative';
        section.appendChild(torch);
    });
}

// Find sections related to companions
function findCompanionSections() {
    const sections = [];
    
    // Look for headings or content mentioning companions
    document.querySelectorAll('h1, h2, h3, h4, p').forEach(element => {
        if (element.textContent.toLowerCase().includes('companion')) {
            // Find the parent section
            let section = element.closest('.card') || element.closest('.feature-card');
            
            if (!section) {
                // If no direct card parent, look for a parent element to add effect to
                let parent = element.parentElement;
                while (parent && parent.tagName !== 'BODY' && parent.id !== 'content' && parent.id !== 'bodyContent') {
                    if (parent.children.length > 1) {
                        section = parent;
                        break;
                    }
                    parent = parent.parentElement;
                }
            }
            
            if (section && !sections.includes(section)) {
                sections.push(section);
            }
        }
    });
    
    return sections;
}

// Lore Nuggets - Interactive tooltips with lore
function initializeLoreNuggets() {
    // Find lore-rich text
    insertLoreNuggets();
    
    // Add hover effect to show lore content
    document.addEventListener('mouseover', function(e) {
        if (e.target.closest('.lore-nugget-icon')) {
            const content = e.target.closest('.lore-nugget').querySelector('.lore-nugget-content');
            if (content) {
                content.style.opacity = '1';
                content.style.transform = 'translateX(-50%) scale(1)';
            }
        }
    });
    
    document.addEventListener('mouseout', function(e) {
        if (e.target.closest('.lore-nugget-icon')) {
            const content = e.target.closest('.lore-nugget').querySelector('.lore-nugget-content');
            if (content) {
                content.style.opacity = '0';
                content.style.transform = 'translateX(-50%) scale(0)';
            }
        }
    });
}

// Insert lore nuggets at appropriate places
function insertLoreNuggets() {
    // Keywords that should trigger lore nuggets
    const loreKeywords = [
        'Silmaril', 'Ring of Power', 'One Ring', 'Mordor', 'Gondor', 'Rivendell', 
        'Moria', 'Balrog', 'Sauron', 'Gandalf', 'Aragorn', 'Frodo', 'Galadriel',
        'Elrond', 'Fëanor', 'Túrin', 'Beren', 'Lúthien', 'Middle-earth'
    ];
    
    // Lore content for each keyword (simplified)
    const loreContent = {
        'Silmaril': 'Jewels crafted by Fëanor that contain the light of the Two Trees of Valinor. Their theft by Morgoth led to the exile of the Noldor.',
        'Ring of Power': 'Magic rings created by the Elven-smiths with Sauron\'s guidance. Three for Elves, Seven for Dwarves, Nine for Men, and One for Sauron himself.',
        'One Ring': 'The master ring forged by Sauron in the fires of Mount Doom. It has the power to control all other Rings of Power.',
        'Mordor': 'Dark realm east of Gondor where Sauron established his fortress of Barad-dûr. Surrounded by mountains and home to Mount Doom.',
        'Gondor': 'Kingdom of Men founded by Elendil and his sons after the fall of Númenor. Known for its white city Minas Tirith.',
        'Rivendell': 'Elven refuge established by Elrond in the Second Age. Known as Imladris in Sindarin, it served as a sanctuary and meeting place.',
        'Moria': 'Ancient Dwarven kingdom beneath the Misty Mountains, also called Khazad-dûm. Later inhabited by Orcs and a Balrog.',
        'Balrog': 'Demons of shadow and flame, corrupted Maiar who served Morgoth. One dwelled in Moria and was defeated by Gandalf.',
        'Sauron': 'The Dark Lord, originally a Maia of Aulë who became Morgoth\'s lieutenant and later attempted to conquer Middle-earth through the One Ring.',
        'Gandalf': 'One of the Istari (wizards), a Maia sent to Middle-earth to oppose Sauron. Also known as Mithrandir and the Grey Pilgrim.',
        'Aragorn': 'Descendant of Elendil and heir to the throne of Gondor who led the War of the Ring and was crowned King Elessar.',
        'Frodo': 'Hobbit who inherited the One Ring and undertook the quest to destroy it in Mount Doom, accompanied by the Fellowship.',
        'Galadriel': 'Powerful Elven queen, bearer of Nenya, one of the Three Rings. Ruled Lothlórien with her husband Celeborn.',
        'Elrond': 'Half-elven lord of Rivendell, bearer of Vilya, one of the Three Rings. Father of Arwen and founder of the Last Homely House.',
        'Fëanor': 'Greatest of the Noldor Elves, creator of the Silmarils and the Fëanorian script. His oath to recover the Silmarils led to tragedy.',
        'Túrin': 'Tragic hero of the First Age, son of Húrin, whose life was cursed by Morgoth. His tale is told in the Narn i Chîn Húrin.',
        'Beren': 'Mortal Man who fell in love with the Elven princess Lúthien. Their quest to recover a Silmaril from Morgoth\'s crown is legendary.',
        'Lúthien': 'Elven princess who fell in love with the mortal Beren. Her dance before Morgoth allowed them to steal a Silmaril.',
        'Middle-earth': 'The central continent of Arda where most of Tolkien\'s stories take place, home to Men, Elves, Dwarves, Hobbits, and other races.'
    };
    
    // Look for these keywords in paragraphs
    document.querySelectorAll('p, li').forEach(element => {
        let html = element.innerHTML;
        
        loreKeywords.forEach(keyword => {
            // Only replace if not already in a link or lore nugget
            if (html.indexOf(keyword) !== -1 && 
                !html.includes(`<a href=`) && 
                !html.includes(`class="lore-nugget"`)) {
                
                // Create nugget HTML
                const nuggetType = keyword.includes('Ring') ? 'ring' : 'sword';
                const nuggetHtml = `
                    <span class="lore-nugget">
                        <span class="lore-nugget-icon ${nuggetType}"></span>
                        <span class="lore-nugget-content">${loreContent[keyword] || keyword}</span>
                        ${keyword}
                    </span>
                `;
                
                // Replace only the first occurrence to avoid too many nuggets
                html = html.replace(keyword, nuggetHtml);
                element.innerHTML = html;
                
                // Only add one nugget per element to avoid clutter
                return;
            }
        });
    });
}

// Relic Cards - Flippable lore items
function initializeRelicCards() {
    // Find sections that might benefit from relic cards
    const artifactSections = findArtifactSections();
    
    // Add relic cards to these sections
    artifactSections.forEach(section => {
        // Extract content for cards
        const title = section.querySelector('h3, h4')?.textContent || 'Artifact of Power';
        const content = section.querySelector('p')?.textContent || 'An ancient relic with mysterious powers.';
        
        // Create relic card
        const relicCard = createRelicCard(title, content);
        
        // Insert card into the section
        section.appendChild(relicCard);
    });
}

// Find sections related to artifacts
function findArtifactSections() {
    const sections = [];
    const artifactKeywords = ['ring', 'artifact', 'weapon', 'sword', 'bow', 'silmaril', 'palantír', 'palantir'];
    
    // Look for headings mentioning artifacts
    document.querySelectorAll('h3, h4').forEach(heading => {
        if (artifactKeywords.some(keyword => heading.textContent.toLowerCase().includes(keyword))) {
            // Find a suitable container for the card
            let section = heading.closest('.card') || heading.closest('.feature-card');
            
            if (!section) {
                // Create a new section if needed
                section = document.createElement('div');
                section.className = 'card';
                heading.parentNode.insertBefore(section, heading.nextSibling);
                
                // Move relevant content into the section
                let sibling = heading.nextSibling;
                while (sibling && sibling.nodeName === 'P') {
                    const nextSibling = sibling.nextSibling;
                    section.appendChild(sibling);
                    sibling = nextSibling;
                }
            }
            
            if (!sections.includes(section)) {
                sections.push(section);
            }
        }
    });
    
    return sections;
}

// Create a relic card element
function createRelicCard(title, content) {
    const card = document.createElement('div');
    card.className = 'relic-card';
    
    card.innerHTML = `
        <div class="relic-card-inner">
            <div class="relic-card-front">
                <div class="relic-card-title">${title}</div>
                <img class="relic-card-image" src="images/artifacts/${title.toLowerCase().replace(/\s+/g, '-')}.png" onerror="this.src='images/artifact-default.png'">
                <div>Click to reveal lore</div>
            </div>
            <div class="relic-card-back">
                <div class="relic-card-title">${title}</div>
                <p>${content}</p>
            </div>
        </div>
    `;
    
    return card;
}

// Companion Gear - Interactive equipment
function initializeCompanionGear() {
    // Find companion sections
    const companionSections = findCompanionSections();
    
    // Add gear interaction to companion sections
    companionSections.forEach(section => {
        // Create gear interaction UI
        const gearUI = createCompanionGearUI();
        
        // Add it to the section
        section.appendChild(gearUI);
    });
}

// Create companion gear UI
function createCompanionGearUI() {
    const gearContainer = document.createElement('div');
    gearContainer.className = 'companion-gear';
    
    // Create companion portrait
    const portrait = document.createElement('div');
    portrait.className = 'companion-portrait';
    
    // Try to find a relevant image or use default
    let portraitImage = 'images/companions/default.png';
    
    // Look for companion name in nearby heading
    const section = gearContainer.closest('.card') || gearContainer.closest('section');
    if (section) {
        const heading = section.querySelector('h2, h3, h4');
        if (heading) {
            const name = heading.textContent.trim();
            portraitImage = `images/companions/${name.toLowerCase().replace(/\s+/g, '-')}.png`;
        }
    }
    
    portrait.style.backgroundImage = `url('${portraitImage}')`;
    
    // Create gear rack
    const gearRack = document.createElement('div');
    gearRack.className = 'gear-rack';
    
    // Add some sample gear items
    const gearItems = [
        { name: 'sword', image: 'images/gear/sword.png' },
        { name: 'bow', image: 'images/gear/bow.png' },
        { name: 'shield', image: 'images/gear/shield.png' },
        { name: 'helm', image: 'images/gear/helm.png' },
        { name: 'armor', image: 'images/gear/armor.png' },
        { name: 'potion', image: 'images/gear/potion.png' }
    ];
    
    gearItems.forEach(item => {
        const gearItem = document.createElement('div');
        gearItem.className = 'gear-item';
        gearItem.setAttribute('data-gear', item.name);
        
        const img = document.createElement('img');
        img.src = item.image;
        img.alt = item.name;
        img.onerror = function() { this.src = 'images/gear/default.png'; };
        
        gearItem.appendChild(img);
        gearRack.appendChild(gearItem);
        
        // Make gear item draggable
        makeGearDraggable(gearItem, portrait);
    });
    
    gearContainer.appendChild(portrait);
    gearContainer.appendChild(gearRack);
    
    return gearContainer;
}

// Make gear items draggable onto companion portrait
function makeGearDraggable(gearItem, portrait) {
    gearItem.addEventListener('mousedown', function(e) {
        e.preventDefault();
        
        // Create a draggable clone
        const clone = gearItem.cloneNode(true);
        clone.style.position = 'absolute';
        clone.style.zIndex = '1000';
        clone.style.opacity = '0.8';
        document.body.appendChild(clone);
        
        // Position the clone
        updatePosition(e, clone);
        
        // Move the clone with the mouse
        function moveHandler(e) {
            updatePosition(e, clone);
        }
        
        // Handle drop
        function dropHandler(e) {
            document.removeEventListener('mousemove', moveHandler);
            document.removeEventListener('mouseup', dropHandler);
            
            // Check if dropped on portrait
            const portraitRect = portrait.getBoundingClientRect();
            const cloneRect = clone.getBoundingClientRect();
            
            if (
                cloneRect.right > portraitRect.left && 
                cloneRect.left < portraitRect.right && 
                cloneRect.bottom > portraitRect.top && 
                cloneRect.top < portraitRect.bottom
            ) {
                // Successfully equipped
                applyGearToPortrait(portrait, gearItem.getAttribute('data-gear'));
            }
            
            // Remove the clone
            clone.remove();
        }
        
        document.addEventListener('mousemove', moveHandler);
        document.addEventListener('mouseup', dropHandler);
    });
}

// Position a draggable element at mouse coordinates
function updatePosition(e, element) {
    element.style.left = (e.clientX - element.offsetWidth / 2) + 'px';
    element.style.top = (e.clientY - element.offsetHeight / 2) + 'px';
}

// Apply gear effect to companion portrait
function applyGearToPortrait(portrait, gearType) {
    // Visual effect based on gear type
    switch (gearType) {
        case 'sword':
            portrait.style.borderColor = 'var(--dwarf-gold)';
            portrait.style.boxShadow = '0 0 20px var(--elvish-glow)';
            break;
        case 'bow':
            portrait.style.transform = 'scale(1.05)';
            portrait.style.filter = 'brightness(1.2)';
            break;
        case 'shield':
            portrait.style.border = '5px solid var(--dwarf-bronze)';
            portrait.style.boxShadow = '0 0 15px var(--dwarf-bronze)';
            break;
        case 'helm':
            // Add a helm overlay
            let helmOverlay = portrait.querySelector('.helm-overlay');
            if (!helmOverlay) {
                helmOverlay = document.createElement('div');
                helmOverlay.className = 'helm-overlay';
                helmOverlay.style.position = 'absolute';
                helmOverlay.style.top = '0';
                helmOverlay.style.left = '0';
                helmOverlay.style.width = '100%';
                helmOverlay.style.height = '30%';
                helmOverlay.style.backgroundImage = 'url("images/gear/helm-overlay.png")';
                helmOverlay.style.backgroundSize = 'contain';
                helmOverlay.style.backgroundRepeat = 'no-repeat';
                helmOverlay.style.backgroundPosition = 'top center';
                helmOverlay.style.pointerEvents = 'none';
                portrait.appendChild(helmOverlay);
            }
            break;
        case 'armor':
            portrait.style.backgroundBlendMode = 'overlay';
            portrait.style.backgroundColor = 'rgba(184, 115, 51, 0.3)';
            break;
        case 'potion':
            // Glow effect
            portrait.style.animation = 'glow 2s infinite alternate';
            if (!document.querySelector('#glow-keyframes')) {
                const style = document.createElement('style');
                style.id = 'glow-keyframes';
                style.textContent = `
                    @keyframes glow {
                        0% { box-shadow: 0 0 10px var(--dwarf-bronze); }
                        100% { box-shadow: 0 0 20px var(--elvish-glow); }
                    }
                `;
                document.head.appendChild(style);
            }
            break;
    }
}

// Scribe's Quill - Interactive note feature
function initializeScribesQuill() {
    // Find community sections
    const communitySections = document.querySelectorAll('.tavern-board');
    
    if (communitySections.length === 0) {
        // Create a tavern board if none exists
        createTavernBoard();
    }
    
    // Add quill button to each section
    communitySections.forEach(section => {
        const quillButton = document.createElement('button');
        quillButton.className = 'scribes-quill';
        quillButton.textContent = 'Leave a Note';
        
        quillButton.addEventListener('click', function() {
            promptForNote(section);
        });
        
        section.appendChild(quillButton);
    });
}

// Create a tavern board community section
function createTavernBoard() {
    // Look for a suitable location
    const content = document.getElementById('bodyContent') || document.getElementById('content');
    
    if (content) {
        // Create the tavern board
        const tavernBoard = document.createElement('div');
        tavernBoard.className = 'tavern-board';
        
        // Add a header
        const header = document.createElement('h2');
        header.textContent = 'Community Tavern';
        
        // Add the board to the page
        content.appendChild(header);
        content.appendChild(tavernBoard);
        
        // Add some initial notes
        addTavernNote(tavernBoard, 'Seeking brave companions for a journey to Moria. Inquire at the Prancing Pony.', -3);
        addTavernNote(tavernBoard, 'Lost: One magic ring. Small, gold, tends to disappear. Reward offered.', 5);
    }
}

// Prompt user for a note
function promptForNote(tavernBoard) {
    const noteText = prompt('What would you like to scribe on the tavern board?');
    
    if (noteText && noteText.trim()) {
        // Add the note with a random rotation
        const rotation = Math.random() * 10 - 5; // -5 to 5 degrees
        addTavernNote(tavernBoard, noteText, rotation);
    }
}

// Add a note to the tavern board
function addTavernNote(tavernBoard, text, rotation) {
    const note = document.createElement('div');
    note.className = 'tavern-note';
    note.textContent = text;
    note.style.setProperty('--rotation', `${rotation}deg`);
    
    // Add note with animation
    note.style.opacity = '0';
    note.style.transform = `rotate(${rotation}deg) translateY(20px)`;
    tavernBoard.appendChild(note);
    
    // Animate in
    setTimeout(() => {
        note.style.transition = 'all 0.5s ease';
        note.style.opacity = '1';
        note.style.transform = `rotate(${rotation}deg) translateY(0)`;
    }, 10);
}

// Make an element draggable
function makeElementDraggable(element) {
    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    
    element.addEventListener('mousedown', dragMouseDown);
    
    function dragMouseDown(e) {
        e.preventDefault();
        
        // Get the mouse cursor position at startup
        pos3 = e.clientX;
        pos4 = e.clientY;
        
        document.addEventListener('mouseup', closeDragElement);
        document.addEventListener('mousemove', elementDrag);
    }
    
    function elementDrag(e) {
        e.preventDefault();
        
        // Calculate the new cursor position
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        
        // Set the element's new position
        element.style.top = (element.offsetTop - pos2) + "px";
        element.style.left = (element.offsetLeft - pos1) + "px";
    }
    
    function closeDragElement() {
        // Stop moving when mouse button is released
        document.removeEventListener('mouseup', closeDragElement);
        document.removeEventListener('mousemove', elementDrag);
    }
}

// Apply theme styles to existing content
function applyThemeStyles() {
    // Add theme class to body
    document.body.classList.add('middle-earth-theme');
    
    // Update existing elements with theme styles
    styleExistingCards();
    convertListsToIconLists();
    addBardicStyleToText();
    
    // Create image placeholders
    createRequiredImages();
}

// Style existing cards with Middle-earth theme
function styleExistingCards() {
    // Apply styles to cards and feature cards
    document.querySelectorAll('.card, .feature-card').forEach(card => {
        card.style.position = 'relative';
        card.style.overflow = 'hidden';
        
        // Add scroll-like borders
        const before = document.createElement('div');
        before.className = 'scroll-edge top';
        before.style.position = 'absolute';
        before.style.top = '0';
        before.style.left = '0';
        before.style.width = '100%';
        before.style.height = '10px';
        before.style.background = 'linear-gradient(to bottom, var(--dwarf-bronze), transparent)';
        
        const after = document.createElement('div');
        after.className = 'scroll-edge bottom';
        after.style.position = 'absolute';
        after.style.bottom = '0';
        after.style.left = '0';
        after.style.width = '100%';
        after.style.height = '10px';
        after.style.background = 'linear-gradient(to top, var(--dwarf-bronze), transparent)';
        
        card.appendChild(before);
        card.appendChild(after);
    });
}

// Convert standard lists to themed icon lists
function convertListsToIconLists() {
    document.querySelectorAll('ul:not(.sidebar ul)').forEach(ul => {
        ul.style.listStyleType = 'none';
        ul.style.paddingLeft = '20px';
        
        Array.from(ul.children).forEach(li => {
            li.style.position = 'relative';
            li.style.paddingLeft = '25px';
            li.style.marginBottom = '10px';
            
            const icon = document.createElement('span');
            icon.textContent = '➳';
            icon.style.position = 'absolute';
            icon.style.left = '0';
            icon.style.color = 'var(--dwarf-bronze)';
            
            li.insertBefore(icon, li.firstChild);
        });
    });
}

// Add bardic style to text content
function addBardicStyleToText() {
    // Look for paragraphs that could be enhanced with bardic style
    document.querySelectorAll('p').forEach(p => {
        // Skip paragraphs that are likely technical or very short
        if (p.textContent.length < 50 || p.textContent.includes('function') || p.textContent.includes('var ')) {
            return;
        }
        
        // Modify text to have more bardic quality
        let text = p.textContent;
        
        // Replace technical terms with more evocative language
        text = text.replace(/implemented/g, 'crafted')
                  .replace(/developed/g, 'forged')
                  .replace(/created/g, 'conjured')
                  .replace(/used/g, 'wielded')
                  .replace(/function/g, 'enchantment')
                  .replace(/system/g, 'arcane system')
                  .replace(/user/g, 'traveler')
                  .replace(/click/g, 'touch')
                  .replace(/javascript/g, 'ancient runes');
        
        p.textContent = text;
        
        // Add artistic first letter for some paragraphs (first in section)
        if (p.previousElementSibling && p.previousElementSibling.tagName.match(/H[1-6]/)) {
            const firstLetter = p.textContent.charAt(0);
            const restOfText = p.textContent.substring(1);
            
            p.innerHTML = `<span style="float: left; font-size: 3em; line-height: 0.8; margin-right: 5px; font-family: 'Cinzel', serif; color: var(--dwarf-bronze);">${firstLetter}</span>${restOfText}`;
        }
    });
}

// Create placeholder images needed for the theme
function createRequiredImages() {
    // List of required images
    const requiredImages = [
        'images/compass-icon.png',
        'images/ring-icon.png',
        'images/sword-icon.png',
        'images/artifact-default.png',
        'images/companions/default.png',
        'images/gear/default.png',
        'images/gear/sword.png',
        'images/gear/bow.png',
        'images/gear/shield.png',
        'images/gear/helm.png',
        'images/gear/armor.png',
        'images/gear/potion.png',
        'images/gear/helm-overlay.png'
    ];
    
    // Check if images directory exists and create placeholders
    const imagesDir = document.querySelector('img[src^="images/"]');
    
    if (imagesDir) {
        // Images directory likely exists
        console.log('Images directory exists, would create placeholder images if this were a complete implementation.');
    } else {
        console.log('Images directory not found, would create directory and placeholder images if this were a complete implementation.');
    }
}

// Helper function to get path to root (borrowed from sidebar.js)
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