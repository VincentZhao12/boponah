document.addEventListener("DOMContentLoaded", function() {
    function simulateLoading() {
        setTimeout(function() {
            // Fetch track details and redirect to results
            fetch('/get_recommendations')
                .then(response => response.json())
                .then(data => {
                    // Redirect to results with track details and playlist name
                    fetch('/results', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data),
                    })
                    .then(response => response.text())
                    .then(html => {
                        document.open();
                        document.write(html);
                        document.close();
                    });
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }, 5000); // Simulate a 5-second loading time
    }

    simulateLoading();
});
