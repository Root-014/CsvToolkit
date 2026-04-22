// Web Application TypeScript
class CSVAnalysisApp {
    private apiUrl: string = 'http://localhost:5000';
    private currentConversationId: string | null = null;

    constructor() {
        this.initializeEventListeners();
        this.checkApiConnection();
    }

    private initializeEventListeners(): void {
        const fileInput = document.getElementById('fileInput') as HTMLInputElement;
        const uploadArea = document.getElementById('uploadArea') as HTMLElement;
        const analyzeBtn = document.getElementById('analyzeBtn') as HTMLButtonElement;

        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }

        if (uploadArea) {
            uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
            uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        }

        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.handleAnalysis());
        }
    }

    private async checkApiConnection(): Promise<void> {
        try {
            const response = await fetch(`${this.apiUrl}/api/health`);
            if (response.ok) {
                console.log('API connected successfully');
            }
        } catch (error) {
            console.warn('API not available:', error);
        }
    }

    private handleFileSelect(event: Event): void {
        const input = event.target as HTMLInputElement;
        if (input.files && input.files.length > 0) {
            this.uploadFile(input.files[0]);
        }
    }

    private handleDragOver(event: DragEvent): void {
        event.preventDefault();
        event.stopPropagation();
        const uploadArea = document.getElementById('uploadArea');
        if (uploadArea) {
            uploadArea.style.borderColor = '#764ba2';
            uploadArea.style.background = '#f0f2ff';
        }
    }

    private handleDrop(event: DragEvent): void {
        event.preventDefault();
        event.stopPropagation();
        const uploadArea = document.getElementById('uploadArea');
        if (uploadArea) {
            uploadArea.style.borderColor = '#667eea';
            uploadArea.style.background = '#f8f9ff';
        }

        if (event.dataTransfer && event.dataTransfer.files.length > 0) {
            this.uploadFile(event.dataTransfer.files[0]);
        }
    }

    private async uploadFile(file: File): Promise<void> {
        const formData = new FormData();
        formData.append('file', file);

        this.showLoading(true);

        try {
            const response = await fetch(`${this.apiUrl}/api/upload`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.showFileInfo(file, data.metadata);
                this.showAnalysisSection();
            } else {
                alert(`Upload failed: ${data.error}`);
            }
        } catch (error) {
            console.error('Upload error:', error);
            alert('Failed to upload file. Please check if the backend is running.');
        } finally {
            this.showLoading(false);
        }
    }

    private showFileInfo(file: File, metadata: any): void {
        const fileInfo = document.getElementById('fileInfo');
        if (fileInfo) {
            fileInfo.innerHTML = `
                <strong>File uploaded:</strong> ${file.name}<br>
                <strong>Size:</strong> ${this.formatFileSize(file.size)}<br>
                <strong>Shape:</strong> ${metadata.shape[0]} rows × ${metadata.shape[1]} columns<br>
                <strong>Columns:</strong> ${metadata.columns.length}
            `;
            fileInfo.style.display = 'block';
        }
    }

    private formatFileSize(bytes: number): string {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    private showAnalysisSection(): void {
        const analysisSection = document.getElementById('analysisSection');
        if (analysisSection) {
            analysisSection.style.display = 'block';
        }
    }

    private async handleAnalysis(): Promise<void> {
        const requestText = (document.getElementById('analysisRequest') as HTMLTextAreaElement).value.trim();

        if (!requestText) {
            alert('Please enter an analysis request');
            return;
        }

        const metadataText = this.getCurrentMetadata();

        this.showLoading(true);
        this.showConversationSection();

        try {
            const response = await fetch(`${this.apiUrl}/api/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    request: requestText,
                    metadata: metadataText
                })
            });

            const data = await response.json();

            if (data.success) {
                this.currentConversationId = data.conv_id;
                this.addMessage('user', requestText);
                this.addMessage('system', 'Analysis started. Please wait...');

                // Poll for conversation updates
                this.pollConversation(data.conv_id);

                // Show results after a delay
                setTimeout(() => this.loadReport(data.report_filename), 3000);
            } else {
                this.addMessage('error', `Analysis failed: ${data.error}`);
            }
        } catch (error) {
            console.error('Analysis error:', error);
            this.addMessage('error', 'Failed to analyze. Please check if the backend is running.');
        } finally {
            this.showLoading(false);
        }
    }

    private getCurrentMetadata(): string {
        return document.getElementById('fileInfo')?.textContent || '';
    }

    private showConversationSection(): void {
        const conversationSection = document.getElementById('conversationSection');
        if (conversationSection) {
            conversationSection.style.display = 'block';
        }
    }

    private addMessage(type: 'user' | 'system' | 'error', content: string): void {
        const conversationHistory = document.getElementById('conversationHistory');
        if (!conversationHistory) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        const timestamp = new Date().toLocaleTimeString();
        messageDiv.innerHTML = `
            <div class="message-header">
                ${type === 'user' ? 'You' : type === 'system' ? 'System' : 'Error'} - ${timestamp}
            </div>
            <div class="message-content">${content}</div>
        `;

        conversationHistory.appendChild(messageDiv);
        conversationHistory.scrollTop = conversationHistory.scrollHeight;
    }

    private async pollConversation(convId: string): Promise<void> {
        const pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`${this.apiUrl}/api/conversation/${convId}`);
                const data = await response.json();

                if (data.status === 'completed' || data.status === 'error') {
                    clearInterval(pollInterval);
                    this.addMessage('system', 'Analysis completed!');
                }
            } catch (error) {
                console.error('Poll error:', error);
                clearInterval(pollInterval);
            }
        }, 2000);

        // Stop polling after 60 seconds
        setTimeout(() => clearInterval(pollInterval), 60000);
    }

    private async loadReport(filename: string): Promise<void> {
        try {
            const response = await fetch(`${this.apiUrl}/api/report/${filename}`);
            const content = await response.text();

            this.displayMarkdown(content);
            this.showResultsSection();

            // Show download button
            const downloadBtn = document.getElementById('downloadBtn');
            if (downloadBtn) {
                downloadBtn.style.display = 'inline-block';
                downloadBtn.onclick = () => this.downloadReport(filename);
            }
        } catch (error) {
            console.error('Failed to load report:', error);
            this.addMessage('error', 'Failed to load the report');
        }
    }

    private displayMarkdown(content: string): void {
        const markdownContent = document.getElementById('markdownContent');
        if (!markdownContent) return;

        // Configure marked for better rendering
        marked.setOptions({
            breaks: true,
            gfm: true
        });

        const html = marked.parse(content);
        const cleanHtml = DOMPurify.sanitize(html as string);

        markdownContent.innerHTML = cleanHtml;
    }

    private showResultsSection(): void {
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
    }

    private downloadReport(filename: string): void {
        const link = document.createElement('a');
        link.href = `${this.apiUrl}/api/report/${filename}`;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    private showLoading(show: boolean): void {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = show ? 'flex' : 'none';
        }
    }
}

// Initialize the application when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new CSVAnalysisApp();
});

// Add health check endpoint to backend
declare global {
    namespace Express {
        interface Request {
            apiUrl?: string;
        }
    }
}