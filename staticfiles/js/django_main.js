// Main JavaScript file for Django-based Disaster Tweet Analyzer

// Initialize all functionality when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS animation library
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true,
        mirror: false
    });
    
    // Navbar scrolling effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Scroll to top button
    const scrollTopBtn = document.createElement('div');
    scrollTopBtn.className = 'scroll-top-btn';
    scrollTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    document.body.appendChild(scrollTopBtn);
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            scrollTopBtn.classList.add('visible');
        } else {
            scrollTopBtn.classList.remove('visible');
        }
    });
    
    scrollTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    // Tweet Analyzer functionality
    const tweetInput = document.getElementById('tweetInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultsContainer = document.getElementById('resultsContainer');
    
    if (analyzeBtn && tweetInput) {
        analyzeBtn.addEventListener('click', analyzeTweet);
    }
    
    // Function to handle tweet analysis
    function analyzeTweet() {
        const tweet = tweetInput.value.trim();
        
        if (!tweet) {
            showAlert('Please enter a tweet to analyze', 'warning');
            return;
        }
        
        // Show loading spinner and hide results
        if (loadingSpinner) loadingSpinner.classList.remove('d-none');
        if (resultsContainer) resultsContainer.style.display = 'none';
        
        // Get CSRF token from cookie for Django
        const csrftoken = getCookie('csrftoken');
        
        // Make API request
        fetch('/api/analyze-tweet/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ tweet: tweet })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Hide loading spinner
            if (loadingSpinner) loadingSpinner.classList.add('d-none');
            
            // Update the UI with results
            updateResults(data);
            
            // Show results container
            if (resultsContainer) {
                resultsContainer.style.display = 'block';
                
                // Scroll to results
                resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (loadingSpinner) loadingSpinner.classList.add('d-none');
            showAlert('An error occurred while analyzing the tweet. Please try again.', 'danger');
        });
    }
    
    // Function to update results in the UI
    function updateResults(data) {
        if (!resultsContainer) return;
        
        // Update prediction
        const prediction = data.prediction.prediction;
        const probability = (data.prediction.probability * 100).toFixed(2);
        
        const predictionResult = document.getElementById('predictionResult');
        const predictionConfidence = document.getElementById('predictionConfidence');
        const predictionProgressBar = document.getElementById('predictionProgressBar');
        const predictionIcon = document.getElementById('predictionIcon');
        
        if (predictionResult) predictionResult.textContent = prediction;
        if (predictionConfidence) predictionConfidence.textContent = `${probability}% confidence`;
        if (predictionProgressBar) {
            predictionProgressBar.style.width = `${probability}%`;
            
            // Update colors based on prediction
            if (prediction === 'Disaster') {
                predictionProgressBar.className = 'progress-bar progress-bar-striped progress-bar-animated bg-danger';
                if (predictionIcon) predictionIcon.className = 'fas fa-exclamation-circle text-danger';
            } else {
                predictionProgressBar.className = 'progress-bar progress-bar-striped progress-bar-animated bg-success';
                if (predictionIcon) predictionIcon.className = 'fas fa-check-circle text-success';
            }
        }
        
        // Update sentiment
        const positiveSentiment = document.getElementById('positiveSentiment');
        const neutralSentiment = document.getElementById('neutralSentiment');
        const negativeSentiment = document.getElementById('negativeSentiment');
        const compoundSentiment = document.getElementById('compoundSentiment');
        
        if (positiveSentiment) positiveSentiment.textContent = `${(data.sentiment.pos * 100).toFixed(2)}%`;
        if (neutralSentiment) neutralSentiment.textContent = `${(data.sentiment.neu * 100).toFixed(2)}%`;
        if (negativeSentiment) negativeSentiment.textContent = `${(data.sentiment.neg * 100).toFixed(2)}%`;
        if (compoundSentiment) compoundSentiment.textContent = data.sentiment.compound.toFixed(2);
        
        // Update disaster types
        const noDisasterTypes = document.getElementById('noDisasterTypes');
        const disasterTypesList = document.getElementById('disasterTypesList');
        
        if (disasterTypesList) {
            disasterTypesList.innerHTML = '';
            
            if (Object.keys(data.disaster_types).length === 0) {
                if (noDisasterTypes) noDisasterTypes.style.display = 'block';
                disasterTypesList.style.display = 'none';
            } else {
                if (noDisasterTypes) noDisasterTypes.style.display = 'none';
                disasterTypesList.style.display = 'flex';
                
                // Map of disaster types to colors and icons
                const disasterColors = {
                    'earthquake': 'danger',
                    'flood': 'primary',
                    'hurricane': 'warning',
                    'wildfire': 'danger',
                    'tornado': 'warning',
                    'storm': 'info',
                    'tsunami': 'primary',
                    'drought': 'warning',
                    'landslide': 'secondary',
                    'volcanic eruption': 'danger',
                    'explosion': 'danger',
                    'fire': 'danger',
                    'pandemic': 'danger',
                    'chemical spill': 'warning',
                    'oil spill': 'dark',
                    'nuclear accident': 'danger',
                    'plane crash': 'dark',
                    'train derailment': 'warning',
                    'mass shooting': 'danger',
                    'terrorist attack': 'danger',
                    'cyber attack': 'info',
                    'food poisoning': 'warning',
                    'water contamination': 'info'
                };
                
                const iconMap = {
                    'earthquake': 'fa-house-damage',
                    'flood': 'fa-water',
                    'hurricane': 'fa-wind',
                    'wildfire': 'fa-fire',
                    'tornado': 'fa-wind',
                    'storm': 'fa-cloud-showers-heavy',
                    'tsunami': 'fa-water',
                    'drought': 'fa-sun',
                    'landslide': 'fa-mountain',
                    'volcanic eruption': 'fa-mountain',
                    'explosion': 'fa-bomb',
                    'fire': 'fa-fire',
                    'pandemic': 'fa-virus',
                    'chemical spill': 'fa-biohazard',
                    'oil spill': 'fa-oil-can',
                    'nuclear accident': 'fa-radiation',
                    'plane crash': 'fa-plane',
                    'train derailment': 'fa-train',
                    'mass shooting': 'fa-bullseye',
                    'terrorist attack': 'fa-bomb',
                    'cyber attack': 'fa-shield-alt',
                    'food poisoning': 'fa-utensils',
                    'water contamination': 'fa-tint-slash'
                };
                
                // Add each disaster type to the list
                Object.entries(data.disaster_types).forEach(([type, keywords]) => {
                    const color = disasterColors[type] || 'primary';
                    const icon = iconMap[type] || 'fa-exclamation-triangle';
                    
                    const disasterTypeDiv = document.createElement('div');
                    disasterTypeDiv.className = 'col-md-6 mb-3';
                    disasterTypeDiv.innerHTML = `
                        <div class="p-3 bg-${color} bg-opacity-10 rounded-3 border border-${color} d-flex align-items-center">
                            <i class="fas ${icon} text-${color} me-3"></i>
                            <div>
                                <h5 class="mb-1 text-capitalize">${type}</h5>
                                <p class="mb-0 small">${keywords.join(', ')}</p>
                            </div>
                        </div>
                    `;
                    
                    disasterTypesList.appendChild(disasterTypeDiv);
                });
            }
        }
        
        // Update locations
        const noLocations = document.getElementById('noLocations');
        const locationsList = document.getElementById('locationsList');
        
        if (locationsList) {
            locationsList.innerHTML = '';
            
            if (data.locations.length === 0) {
                if (noLocations) noLocations.style.display = 'block';
                locationsList.style.display = 'none';
            } else {
                if (noLocations) noLocations.style.display = 'none';
                locationsList.style.display = 'block';
                
                // Add each location to the list
                const locationsHTML = data.locations.map(location => `
                    <span class="badge bg-info text-dark me-2 mb-2 p-2">
                        <i class="fas fa-map-marker-alt me-1"></i> ${location}
                    </span>
                `).join('');
                
                locationsList.innerHTML = locationsHTML;
            }
        }
    }
    
    // Function to show alert messages
    function showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.setAttribute('role', 'alert');
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Find a suitable container for the alert
        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
            
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                alertDiv.classList.remove('show');
                setTimeout(() => alertDiv.remove(), 300);
            }, 5000);
        }
    }
    
    // Function to get cookie by name (for CSRF token)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Stats counter animation
    const stats = document.querySelectorAll('.stat-number');
    if (stats.length > 0) {
        const statsSection = document.querySelector('.stats-section');
        if (statsSection) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        countUp();
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.1 });
            
            observer.observe(statsSection);
        }
        
        function countUp() {
            stats.forEach(stat => {
                const target = parseInt(stat.getAttribute('data-count'));
                const count = +stat.innerText.replace(/,/g, '').replace(/\+/g, '');
                const speed = 50;
                
                if (count < target) {
                    stat.innerText = Math.ceil(count + target / speed) + (stat.innerText.includes('+') ? '+' : '');
                    setTimeout(countUp, 20);
                } else {
                    stat.innerText = target.toLocaleString() + (stat.innerText.includes('+') ? '+' : '');
                }
            });
        }
    }
});
