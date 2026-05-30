// Settings form handler
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form[method="POST"]');
    
    if (form) {
        form.addEventListener('submit', function(event) {
            // Prevent default submission for now
            event.preventDefault();
            
            // Get form values
            const formData = new FormData(form);
            const host = formData.get('host') || formData.get('ollama_host');
            const port = formData.get('port') || formData.get('ollama_port');
            const model = formData.get('model') || formData.get('ollama_model');
            
            // Show success message
            alert('Settings saved successfully!');
            
            // Optionally submit the form
            // form.submit();
        });
    }
});
