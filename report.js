document.addEventListener("DOMContentLoaded", function () {
    const generateReportBtn = document.getElementById("generate-btn");
    const fileInput = document.getElementById('fileInput');
    const genBtn = document.getElementById('gen-btn');
    const statusMessage = document.getElementById('statusMessage');

    // Show status message with animation
    function showStatus(message, isError = false) {
        statusMessage.textContent = message;
        statusMessage.className = isError ? 'error' : 'success';
        statusMessage.style.display = 'block';
    }

    // Hide status message after delay
    function hideStatus() {
        setTimeout(() => {
            statusMessage.textContent = '';
            statusMessage.className = '';
            statusMessage.style.display = 'none';
        }, 3000);
    }

    async function downloadReport(url, filename) {
        try {
            showStatus('Generating report...');
            const response = await fetch(url, { 
                method: 'POST',
                headers: {
                    'Accept': 'application/pdf'
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const blob = await response.blob();
            const link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            window.URL.revokeObjectURL(link.href);
            link.remove();

            showStatus('✅ Report downloaded successfully!');
            hideStatus();
        } catch (error) {
            console.error('Error:', error);
            showStatus(`❌ ${error.message || 'Failed to generate report. Please try again.'}`, true);
            hideStatus();
        }
    }

    // Handle file upload and report generation
    genBtn.addEventListener('click', async function() {
        if (!fileInput.files.length) {
            showStatus('❌ Please select a file first', true);
            return;
        }

        const file = fileInput.files[0];
        const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
        
        if (!allowedTypes.includes(file.type)) {
            showStatus('❌ Invalid file type. Please upload PDF, DOCX, or TXT files only.', true);
            return;
        }

        showStatus('Generating report...');
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:5000/generate-report-from-file', {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/pdf'
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const blob = await response.blob();
            const link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = 'health_report.pdf';
            document.body.appendChild(link);
            link.click();
            window.URL.revokeObjectURL(link.href);
            link.remove();

            showStatus('✅ Report downloaded successfully!');
            hideStatus();
        } catch (error) {
            console.error('Error:', error);
            showStatus(`❌ ${error.message || 'Failed to generate report. Please try again.'}`, true);
            hideStatus();
        }
    });

    // Handle direct data report generation
    generateReportBtn.addEventListener('click', function() {
        downloadReport('http://localhost:5000/generate-report', 'health_report.pdf');
    });
});
