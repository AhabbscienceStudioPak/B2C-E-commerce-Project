// JavaScript file for the Plotly Dash app

// Embed the Dash app in the HTML page
var myDashApp = document.getElementById('sales-graph');
var url = 'http://127.0.0.1:5000'; // Replace with the URL of your Dash app

// Fetch the layout and data from the Dash app
Promise.all([
  fetch(url + '/_dash-layout').then(response => response.json()),
  fetch(url + '/_dash-dependencies').then(response => response.json()),
]).then(([layout, data]) => {
  // Create the Plotly chart with the layout and data
  Plotly.newPlot(myDashApp, data, layout);

  // Resize the chart when the window is resized
  window.addEventListener('resize', () => {
    Plotly.Plots.resize(myDashApp);
  });
});


