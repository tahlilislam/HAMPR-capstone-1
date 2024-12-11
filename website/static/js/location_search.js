$('#location_general').on('input', async function() {
    let query = $(this).val().trim();
    if (query.length >= 3) {
        try {
            const response = await axios.get('http://api.geonames.org/postalCodeSearchJSON?', {
                params: {
                    postalcode: query,
                    maxRows: 5, // Limit the number of suggestions
                    username: 'tlilz' // Store geoname username as environment variable
                }
            });

            const suggestions = response.data.geonames.map(function(location) {
                return `<div class="suggestion">${location.placeName}, ${location.countryCode}</div>`;
            });
            $('#location_suggestions').html(suggestions.join(''));

            // Handle suggestion selection
            $('.suggestion').on('click', function() {
                $('#location_general').val($(this).text());
                $('#location_suggestions').html('');
            });
        } catch (error) {
            console.error('Error fetching location suggestions:', error);
        }
    } else {
        $('#location_suggestions').html('');
    }
});
