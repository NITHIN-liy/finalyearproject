document.addEventListener('DOMContentLoaded', () => {
    // Theme Management
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;
    
    // Check saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    htmlElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    themeToggle.addEventListener('click', () => {
        const currentTheme = htmlElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        htmlElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });

    function updateThemeIcon(theme) {
        const icon = themeToggle.querySelector('i');
        if (icon) {
            icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        }
    }

    // Loading State
    const actionForm = document.getElementById('analysis-form');
    const loadingOverlay = document.getElementById('loading-overlay');

    if (actionForm) {
        actionForm.addEventListener('submit', () => {
            loadingOverlay.style.display = 'flex';
        });
    }

    // Notice Drafting (AJAX)
    const draftBtn = document.getElementById('draft-notice-btn');
    if (draftBtn) {
        draftBtn.addEventListener('click', async () => {
            const analysisData = JSON.parse(draftBtn.getAttribute('data-analysis'));
            
            loadingOverlay.style.display = 'flex';
            const loadingText = loadingOverlay.querySelector('p');
            if (loadingText) loadingText.innerText = "Drafting Legal Notice...";

            try {
                const response = await fetch('/draft_notice', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ analysis: analysisData })
                });

                const result = await response.json();
                
                if (result.notice_text) {
                    showNoticeModal(result.notice_text);
                } else {
                    alert('Drafting failed: ' + (result.error || 'Unknown error'));
                }
            } catch (error) {
                alert('Connection error: ' + error);
            } finally {
                loadingOverlay.style.display = 'none';
                if (loadingText) loadingText.innerText = "Analyzing Legal Problem...";
            }
        });
    }

    // Markdown Parsing
    const markdownContainers = document.querySelectorAll('.markdown-content');
    if (window.marked) {
        markdownContainers.forEach(container => {
            const rawText = container.innerText;
            container.innerHTML = marked.parse(rawText);
        });
    }

    function showNoticeModal(text) {
        const modal = document.createElement('div');
        modal.className = 'notice-modal';
        modal.innerHTML = `
            <div class="card" id="notice-card" style="max-width: 800px; width: 95%; max-height: 90vh; overflow-y: auto; position: relative; padding: 3rem;">
                <button class="btn no-print" style="position: absolute; top: 1rem; right: 1rem;" onclick="this.closest('.notice-modal').remove()">×</button>
                
                <div class="print-header no-print" style="text-align: center; margin-bottom: 2rem;">
                    <h2 style="margin-bottom: 0.5rem;">Drafted Legal Notice</h2>
                    <p class="text-muted">Review and export your formal notice.</p>
                </div>

                <div id="notice-body" style="white-space: pre-wrap; font-family: 'Times New Roman', Times, serif; font-size: 1.1rem; line-height: 1.5; color: #000; background: white; padding: 2.5rem; border: 1px solid #ddd; border-radius: 4px; box-shadow: inset 0 0 10px rgba(0,0,0,0.02);">
                    ${text}
                </div>

                <div style="margin-top: 2rem; display: flex; gap: 1rem; justify-content: center;" class="no-print">
                    <button class="btn btn-primary" onclick="copyToClipboard(\`${text.replace(/`/g, '\\`')}\`)">
                        <i class="fas fa-copy"></i> Copy Text
                    </button>
                    <button class="btn" style="background: var(--slate-800); color: white;" onclick="window.print()">
                        <i class="fas fa-print"></i> Print Notice
                    </button>
                    <button class="btn" style="background: var(--slate-200); color: var(--slate-900);" onclick="downloadTxt(\`${text.replace(/`/g, '\\`')}\`)">
                        <i class="fas fa-download"></i> Download .txt
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    // Mobile Menu Toggle
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
            const icon = menuToggle.querySelector('i');
            if (sidebar.classList.contains('active')) {
                icon.className = 'fas fa-times';
            } else {
                icon.className = 'fas fa-bars';
            }
        });
    }
});

// Global Helpers
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('Copied to clipboard!');
    });
}

function downloadTxt(text) {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'Legal_Notice.txt';
    a.click();
}
