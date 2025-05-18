/**
 * Main JavaScript file for Disaster Tweet Analyzer
 */

// Document ready function
document.addEventListener("DOMContentLoaded", function () {
  // Dark mode toggle functionality
  initDarkMode();

  // Initialize tooltips and popovers if Bootstrap is present
  if (typeof bootstrap !== "undefined") {
    var tooltipTriggerList = [].slice.call(
      document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    var popoverTriggerList = [].slice.call(
      document.querySelectorAll('[data-bs-toggle="popover"]')
    );
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
      return new bootstrap.Popover(popoverTriggerEl);
    });
  }

  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
        });
      }
    });
  });

  // Initialize validation for any forms with the 'needs-validation' class
  var forms = document.querySelectorAll(".needs-validation");
  Array.prototype.slice.call(forms).forEach(function (form) {
    form.addEventListener(
      "submit",
      function (event) {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add("was-validated");
      },
      false
    );
  });
});

// Initialize dark mode
function initDarkMode() {
  const darkModeToggle = document.getElementById("dark-mode-toggle");
  const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");

  // Check for saved user preference, if any, on page load
  const currentTheme = localStorage.getItem("theme");
  if (currentTheme == "dark") {
    document.body.classList.add("dark-mode");
    updateDarkModeIcon(true);
  } else if (currentTheme == "light") {
    document.body.classList.remove("dark-mode");
    updateDarkModeIcon(false);
  } else if (prefersDarkScheme.matches) {
    // If no saved preference, respect OS preference
    document.body.classList.add("dark-mode");
    updateDarkModeIcon(true);
  }

  // Add click event to button
  if (darkModeToggle) {
    darkModeToggle.addEventListener("click", function () {
      // Toggle dark mode class on body
      const isDarkMode = document.body.classList.toggle("dark-mode");

      // Update icon
      updateDarkModeIcon(isDarkMode);

      // Store user preference
      localStorage.setItem("theme", isDarkMode ? "dark" : "light");
    });
  }
}

// Update dark mode toggle icon
function updateDarkModeIcon(isDarkMode) {
  const darkModeToggle = document.getElementById("dark-mode-toggle");
  if (darkModeToggle) {
    const icon = darkModeToggle.querySelector("i");
    if (icon) {
      if (isDarkMode) {
        icon.classList.remove("fa-moon");
        icon.classList.add("fa-sun");
      } else {
        icon.classList.remove("fa-sun");
        icon.classList.add("fa-moon");
      }
    }
  }
}

// Function to show loading spinner
function showLoading(elementId, message = "Loading...") {
  const element = document.getElementById(elementId);
  if (element) {
    element.innerHTML = `
            <div class="text-center">
                <span class="loader"></span>
                <p class="mt-3">${message}</p>
            </div>
        `;
  }
}

// Function to hide loading spinner
function hideLoading(elementId, content) {
  const element = document.getElementById(elementId);
  if (element) {
    element.innerHTML = content;
  }
}

// Twitter authentication functions
async function authenticateWithTwitter() {
  try {
    const response = await fetch("/auth/twitter");
    const data = await response.json();
    if (data.auth_url) {
      window.location.href = data.auth_url;
    } else {
      console.error("Failed to get authentication URL");
    }
  } catch (error) {
    console.error("Error during Twitter authentication:", error);
  }
}

// Prediction functions for disaster tweets
async function predictTweet(event) {
  event.preventDefault();

  const tweetText = document.getElementById("tweet-text").value.trim();
  if (!tweetText) {
    alert("Please enter a tweet to analyze");
    return;
  }

  // Show loading state
  showLoading("result", "Analyzing tweet...");

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ tweet: tweetText }),
    });

    const data = await response.json();

    // Display results
    const resultElement = document.getElementById("result");
    resultElement.classList.add("show");

    let resultHTML = "";
    if (data.is_disaster) {
      resultHTML = `
                <div class="alert alert-danger" role="alert">
                    <h4 class="alert-heading"><i class="fas fa-exclamation-triangle"></i> Disaster Tweet Detected!</h4>
                    <p>This tweet appears to be about a real disaster or emergency.</p>
                    <hr>
                    <p class="mb-0">Confidence: ${(
                      data.confidence * 100
                    ).toFixed(2)}%</p>
                </div>
            `;

      if (data.locations && data.locations.length > 0) {
        resultHTML += `
                    <div class="card mt-3">
                        <div class="card-header">
                            <i class="fas fa-map-marker-alt"></i> Locations Mentioned
                        </div>
                        <div class="card-body">
                            <ul class="list-group">
                                ${data.locations
                                  .map(
                                    (loc) =>
                                      `<li class="list-group-item">${loc}</li>`
                                  )
                                  .join("")}
                            </ul>
                        </div>
                    </div>
                `;
      }

      if (data.disaster_type) {
        resultHTML += `
                    <div class="card mt-3">
                        <div class="card-header">
                            <i class="fas fa-tag"></i> Disaster Type
                        </div>
                        <div class="card-body">
                            <p class="card-text">${data.disaster_type}</p>
                        </div>
                    </div>
                `;
      }
    } else {
      resultHTML = `
                <div class="alert alert-success" role="alert">
                    <h4 class="alert-heading"><i class="fas fa-check-circle"></i> Not a Disaster Tweet</h4>
                    <p>This tweet does not appear to be about a real disaster or emergency.</p>
                    <hr>
                    <p class="mb-0">Confidence: ${(
                      data.confidence * 100
                    ).toFixed(2)}%</p>
                </div>
            `;
    }

    if (data.sentiment) {
      resultHTML += `
                <div class="card mt-3">
                    <div class="card-header">
                        <i class="fas fa-smile"></i> Sentiment Analysis
                    </div>
                    <div class="card-body">
                        <p class="card-text">Sentiment: ${
                          data.sentiment.label
                        } (${(data.sentiment.score * 100).toFixed(2)}%)</p>
                    </div>
                </div>
            `;
    }

    hideLoading("result", resultHTML);
  } catch (error) {
    console.error("Error predicting tweet:", error);
    hideLoading(
      "result",
      `
            <div class="alert alert-warning" role="alert">
                <h4 class="alert-heading"><i class="fas fa-exclamation-circle"></i> Error</h4>
                <p>An error occurred while analyzing the tweet. Please try again.</p>
            </div>
        `
    );
  }
}
