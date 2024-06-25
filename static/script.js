document.addEventListener("DOMContentLoaded", function() {
    let loadingProgress = document.getElementById("loading-progress");
    let resultContainer = document.getElementById("result-container");
    let loadingContainer = document.getElementById("loading-container");
  
    function simulateLoading() {
      let width = 0;
      let interval = setInterval(function() {
        if (width >= 100) {
          clearInterval(interval);
          loadingContainer.style.display = "none";
          resultContainer.style.display = "block";
        } else {
          width++;
          loadingProgress.style.width = width + "%";
        }
      }, 50); // Adjust the speed of loading here
    }
  
    simulateLoading();
  });
  