document.addEventListener('DOMContentLoaded', () => {
    // Chat Elements
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    // File Upload Elements
    const fileInput = document.getElementById('file-input');
    const filePreviewArea = document.getElementById('file-preview-area');
    const previewFilename = document.getElementById('preview-filename');
    const clearFileBtn = document.getElementById('clear-file');

    // Workspace Elements
    const fileManager = document.getElementById('file-manager');
    const refreshFilesBtn = document.getElementById('refresh-files-btn');
    const viewerFilename = document.getElementById('viewer-filename');
    const viewerCode = document.getElementById('viewer-code');

    let currentUploadFile = null;

    // --- Markdown & Highlight Setup ---
    marked.setOptions({
        highlight: function (code, lang) {
            const language = hljs.getLanguage(lang) ? lang : 'plaintext';
            return hljs.highlight(code, { language }).value;
        },
        breaks: true
    });

    // --- Chat Input Logic ---
    chatInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        if (this.value === '') this.style.height = 'auto';
    });

    chatInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    // --- File Upload UI Logic ---
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            currentUploadFile = e.target.files[0];
            previewFilename.textContent = currentUploadFile.name;
            filePreviewArea.classList.remove('hidden');
        }
    });

    clearFileBtn.addEventListener('click', (e) => {
        e.preventDefault();
        currentUploadFile = null;
        fileInput.value = '';
        filePreviewArea.classList.add('hidden');
    });

    // --- Main Chat Submission ---
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const text = chatInput.value.trim();
        if (!text && !currentUploadFile) return;

        chatInput.value = '';
        chatInput.style.height = 'auto';

        let finalPayloadText = text;

        // 1. Handle File Upload if Present
        if (currentUploadFile) {
            const formData = new FormData();
            formData.append('file', currentUploadFile);

            appendMessage('user', `[Attached File: ${currentUploadFile.name}]\n${finalPayloadText}`);

            try {
                const res = await fetch('/api/upload', { method: 'POST', body: formData });
                const data = await res.json();
                if (data.filepath) {
                    finalPayloadText = `[User uploaded file located at: ${data.filepath}]\n${finalPayloadText}`;
                }
            } catch (err) {
                console.error("Upload error:", err);
            }
            // Clear attachment visual
            currentUploadFile = null;
            fileInput.value = '';
            filePreviewArea.classList.add('hidden');
        } else {
            appendMessage('user', finalPayloadText);
        }

        // 2. Show Typing Indicator
        const typingId = showTyping();

        // 3. Send to Backend Router
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: finalPayloadText })
            });
            const data = await response.json();

            removeTyping(typingId);

            if (data.response) {
                appendMessage('ai', data.response);
                // After AI responds, it might have created a file. Let's refresh the file manager automatically!
                if (data.response.includes('Successfully created file')) {
                    loadFiles();
                }
            } else if (data.error) {
                appendMessage('ai', `**Error:** ${data.error}`);
            }
        } catch (error) {
            removeTyping(typingId);
            appendMessage('ai', `**Connection Error:** Could not reach the backend API.`);
            console.error(error);
        }
    });

    // --- Chat UI Helpers ---
    function appendMessage(sender, text) {
        const div = document.createElement('div');
        div.className = `message ${sender}-message`;

        let contentHtml = marked.parse(text);

        if (sender === 'ai') {
            div.innerHTML = `
                <div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>
                <div class="msg-content">${contentHtml}</div>
            `;
        } else {
            div.innerHTML = `
                <div class="msg-avatar"><i class="fa-regular fa-user"></i></div>
                <div class="msg-content">${contentHtml}</div>
            `;
        }

        chatMessages.appendChild(div);

        // Highlight generated code
        div.querySelectorAll('pre code').forEach((el) => {
            hljs.highlightElement(el);
        });

        scrollToBottom();
    }

    function showTyping() {
        const id = 'typing-' + Date.now();
        const div = document.createElement('div');
        div.className = 'message ai-message typing-elm';
        div.id = id;
        div.innerHTML = `
            <div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="msg-content">
                <div class="typing-dots"><span></span><span></span><span></span></div>
            </div>
        `;
        chatMessages.appendChild(div);
        scrollToBottom();
        return id;
    }

    function removeTyping(id) {
        const elm = document.getElementById(id);
        if (elm) elm.remove();
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // --- Workspace / File Manager Logic ---
    async function loadFiles() {
        try {
            const res = await fetch('/api/files');
            const data = await res.json();

            fileManager.innerHTML = '';

            if (data.files && data.files.length === 0) {
                fileManager.innerHTML = '<div class="file-item loading">No files in directory.</div>';
                return;
            }

            // Always show parent directory indicator for context
            const dirNode = document.createElement('div');
            dirNode.className = 'folder-item';
            dirNode.innerHTML = '<i class="fa-solid fa-folder-open text-orange"></i> <span>Workspace</span>';
            fileManager.appendChild(dirNode);

            data.files.forEach(file => {
                const fNode = document.createElement('div');
                fNode.className = 'file-item';
                // Pick icon based on extension
                let icon = 'fa-file-lines';
                if (file.endsWith('.py')) icon = 'fa-brands fa-python text-blue';
                if (file.endsWith('.txt')) icon = 'fa-file-alt text-muted';
                if (file.endsWith('.md')) icon = 'fa-file-code text-purple';
                if (file.endsWith('.env')) icon = 'fa-sliders text-green';

                fNode.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${file}</span>`;

                fNode.addEventListener('click', () => {
                    // Update UI selection
                    document.querySelectorAll('.file-item').forEach(el => el.classList.remove('selected'));
                    fNode.classList.add('selected');
                    loadFileContent(file);
                });

                fileManager.appendChild(fNode);
            });

        } catch (e) {
            fileManager.innerHTML = '<div class="file-item loading" style="color:red;">Error loading files</div>';
        }
    }

    async function loadFileContent(filename) {
        viewerFilename.textContent = 'Loading...';
        viewerCode.textContent = '...';

        try {
            const res = await fetch(`/api/files/${encodeURIComponent(filename)}`);
            const data = await res.json();

            if (data.error) throw new Error(data.error);

            viewerFilename.textContent = filename;
            viewerCode.textContent = data.content;

            // Determine language for highlighting
            viewerCode.className = '';
            if (filename.endsWith('.py')) viewerCode.classList.add('language-python');
            else if (filename.endsWith('.js')) viewerCode.classList.add('language-javascript');
            else if (filename.endsWith('.html')) viewerCode.classList.add('language-html');
            else if (filename.endsWith('.css')) viewerCode.classList.add('language-css');
            else if (filename.endsWith('.md')) viewerCode.classList.add('language-markdown');
            else viewerCode.classList.add('language-plaintext');

            hljs.highlightElement(viewerCode);

        } catch (e) {
            viewerFilename.textContent = 'Error';
            viewerCode.textContent = `Could not load file:\n${e.message}`;
            viewerCode.className = 'language-plaintext';
        }
    }

    refreshFilesBtn.addEventListener('click', () => {
        const icon = refreshFilesBtn.querySelector('i');
        icon.style.transform = 'rotate(180deg)';
        setTimeout(() => icon.style.transform = '', 300);
        loadFiles();
    });

    // Initial load
    loadFiles();
});
