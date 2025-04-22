/**
 * NLP Knowledge Base
 * Main JavaScript file for enhanced functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize code syntax highlighting if highlight.js is available
    if (typeof hljs !== 'undefined') {
        document.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
        
        // Add code-block class to pre elements containing code
        document.querySelectorAll('pre').forEach((block) => {
            if (!block.classList.contains('code-block') && block.querySelector('code')) {
                block.classList.add('code-block');
            }
        });
    }
    
    // Auto-format HTML content in post descriptions and answers
    document.querySelectorAll('.post-description, .post-answer').forEach(element => {
        // Replace consecutive newlines with proper paragraph breaks
        const content = element.innerHTML;
        if (content.includes('<p>') || content.includes('<pre>')) {
            // Content is already formatted with HTML
            return;
        }
        
        // Basic formatting for plain text content
        element.innerHTML = formatTextContent(content);
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            
            if (href !== '#' && href.startsWith('#')) {
                e.preventDefault();
                
                const targetElement = document.querySelector(href);
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 80,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
    
    // Show active tab based on URL hash
    const urlHash = window.location.hash;
    if (urlHash) {
        const tabElement = document.querySelector(`a[data-bs-toggle="tab"][href="${urlHash}"], button[data-bs-toggle="tab"][data-bs-target="${urlHash}"]`);
        if (tabElement) {
            const tab = new bootstrap.Tab(tabElement);
            tab.show();
            
            // Smooth scroll to the tab
            window.scrollTo({
                top: tabElement.offsetTop - 80,
                behavior: 'smooth'
            });
        }
    }
    
    // Add 'active' class to navbar item based on current path
    const currentPath = window.location.pathname;
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath.startsWith(href) && href !== '/')) {
            link.classList.add('active');
        }
    });
    
    // Back to top button
    const backToTopButton = document.getElementById('back-to-top');
    if (backToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.classList.add('show');
            } else {
                backToTopButton.classList.remove('show');
            }
        });
        
        backToTopButton.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Initialize dark mode
    initDarkMode();
});

/**
 * Format plain text content with basic HTML structure
 * @param {string} text - The text content to format
 * @return {string} Formatted HTML content
 */
function formatTextContent(text) {
    if (!text) return '';
    
    // Replace URLs with clickable links
    text = text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
    
    // Format code blocks (text between backticks)
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Split by double newlines for paragraphs
    const paragraphs = text.split(/\n\s*\n/);
    
    // Join paragraphs with proper HTML tags
    return paragraphs.map(p => `<p>${p.trim()}</p>`).join('');
}

/**
 * Copy text to clipboard
 * @param {string} text - The text to copy
 * @return {Promise} Promise that resolves when copying is complete
 */
function copyToClipboard(text) {
    // Use the modern Clipboard API if available
    if (navigator.clipboard && navigator.clipboard.writeText) {
        return navigator.clipboard.writeText(text);
    }
    
    // Fallback for older browsers
    return new Promise((resolve, reject) => {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';  // Prevent scrolling to bottom
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();
        
        try {
            const successful = document.execCommand('copy');
            document.body.removeChild(textarea);
            if (successful) {
                resolve();
            } else {
                reject(new Error('Unable to copy text'));
            }
        } catch (err) {
            document.body.removeChild(textarea);
            reject(err);
        }
    });
}

/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - The type of notification (success, error, warning, info)
 * @param {number} duration - Duration in milliseconds
 */
function showNotification(message, type = 'success', duration = 3000) {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    // Toast content
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // Add to container
    toastContainer.appendChild(toastEl);
    
    // Initialize and show the toast
    const toast = new bootstrap.Toast(toastEl, {
        autohide: true,
        delay: duration
    });
    toast.show();
    
    // Remove from DOM after hiding
    toastEl.addEventListener('hidden.bs.toast', function() {
        toastEl.remove();
    });
}

// Dark Mode Functionality
function initDarkMode() {
    // Check for saved user preference, default to light
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    // Apply the saved theme or default
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-mode');
        document.getElementById('darkModeToggle').checked = true;
    }
    
    // Listen for toggle changes
    document.getElementById('darkModeToggle').addEventListener('change', function(e) {
        if (e.target.checked) {
            document.body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('theme', 'light');
        }
    });
} 