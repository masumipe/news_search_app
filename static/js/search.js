// Search form handler
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.querySelector('form[method="POST"]');
    
    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            // Prevent default submission for now
            event.preventDefault();
            
            // Get form values
            const topic = document.querySelector('input[name="topic"]').value;
            const region = document.querySelector('input[name="region"]').value;
            const priority_region = document.querySelector('input[name="priority_region"]').value;
            
            // Show loading message
            document.querySelector('h1').textContent = 'Searching...';
            
            // Simulate search delay
            setTimeout(function() {
                // Create search results page
                const resultsPage = document.createElement('div');
                resultsPage.innerHTML = `
                    <div class="container">
                        <h1>Search Results</h1>
                        {% for result in results %}
                        <div class="result">
                            <h2>{{ result.summary }}</h2>
                            <p><a href="{{ result.website }}">{{ result.website }}</a></p>
                        </div>
                        {% endfor %}
                        <a href="/">Back to Home</a>
                    </div>
                `;
                
                // Show results
                document.querySelector('h1').textContent = 'Search Results';
                document.body.innerHTML = resultsPage.innerHTML;
            }, 500);
        });
    }
});
