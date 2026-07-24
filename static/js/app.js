// Prediction form handler
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('predictForm');
    const result = document.getElementById('predictionResult');

    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData(form);
            const data = {};
            formData.forEach((v, k) => data[k] = parseFloat(v));

            // Handle Machine_Type separately (it's a string, not a number)
            const typeSelect = form.querySelector('select[name="Machine_Type"]');
            data['Machine_Type'] = typeSelect ? typeSelect.value : 'Conveyor';

            // Validate machine type is selected
            if (!data['Machine_Type'] || data['Machine_Type'] === '') {
                result.className = 'prediction-result show';
                result.style.background = '#fee2e2';
                result.style.color = '#991b1b';
                result.innerHTML = '<strong>⚠️ Please select a Machine Type</strong>';
                return;
            }

            try {
                const res = await fetch('/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const json = await res.json();

                result.className = 'prediction-result show ' + json.risk_level.toLowerCase();
                result.innerHTML = `
                    <strong>Machine Type: ${json.machine_type}</strong><br>
                    <strong>Prediction: ${json.prediction === 1 ? 'FAILURE LIKELY' : 'NORMAL'}</strong><br>
                    Failure Probability: <b>${json.probability}%</b> | Risk Level: <b>${json.risk_level}</b>
                `;
            } catch(err) {
                result.className = 'prediction-result show';
                result.style.background = '#fee2e2';
                result.style.color = '#991b1b';
                result.innerHTML = '<strong>Error:</strong> ' + err.message;
            }
        });
    }
});
