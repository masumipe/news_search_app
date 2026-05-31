// Search form handler
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.querySelector('form[method="POST"]');
    
    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            // Get form values
            const topic = document.querySelector('input[name="topic"]').value;
            const region = document.querySelector('input[name="region"]').value;
            const priority_region = document.querySelector('input[name="priority_region"]').value;
            
            // Show loading message
            document.querySelector('h1').textContent = 'Searching...';
            console.log("Submitting search with:", { topic, region, priority_region });
            // Submit form normally to Flask backend
            searchForm.submit();
        });
    }
});
