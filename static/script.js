        //Form Submission Handling
        document.getElementById('search-form').addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent default form submission
            const query = document.getElementById('query').value;
            fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `query=${encodeURIComponent(query)}`
            })
            .then(response => response.text())
            .then(html => {
                document.getElementById('results-container').innerHTML = html;
            })
            .catch(error => console.error('Error fetching search results:', error));
        });
        //Autocomplete Suggestions
        document.getElementById('query').addEventListener('input', function() {
            const query = this.value;
            if (query.length > 0) {
                fetch('/autocomplete', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `query=${encodeURIComponent(query)}`
                })
                .then(response => response.json())
                .then(data => {
                    const suggestionsList = document.getElementById('suggestions-list');
                    suggestionsList.innerHTML = ''; // Clear previous suggestions
                    // Show corrected query
                    if (query !== data.corrected_query) {
                        const correctedItem = document.createElement('li');
                        correctedItem.textContent = `Did you mean: ${data.corrected_query}?`;
                        correctedItem.style.fontWeight = 'bold';
                        correctedItem.addEventListener('click', () => {
                            document.getElementById('query').value = data.corrected_query;
                            suggestionsList.innerHTML = '';
                        });
                        suggestionsList.appendChild(correctedItem);
                    }
                    // Add suggestions to the list
                    data.suggestions.forEach(suggestion => {
                        const suggestionItem = document.createElement('li');
                        suggestionItem.textContent = suggestion;
                        suggestionItem.addEventListener('click', () => {
                            document.getElementById('query').value = suggestion;
                            suggestionsList.innerHTML = '';
                        });
                        suggestionsList.appendChild(suggestionItem);
                    });
                })
                .catch(error => console.error('Error fetching suggestions:', error));
            } else {
                document.getElementById('suggestions-list').innerHTML = ''; // Clear suggestions if input is empty
            }
        });