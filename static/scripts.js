document.addEventListener("DOMContentLoaded", function() {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const symbolSelect = document.getElementById('symbol');
    const currentPriceDiv = document.getElementById('currentPrice');

    // Fetch the current market price for the selected symbol
    async function fetchPrice(symbol) {
        const response = await fetch(`/get_price/${symbol}`);
        const data = await response.json();
        currentPriceDiv.innerHTML = `Price: ${data.price} ${data.symbol}`;
    }

    // Start trading
    startBtn.addEventListener('click', async function() {
        startBtn.disabled = true;
        stopBtn.disabled = false;

        const response = await fetch('/start_trading', { method: 'POST' });
        const data = await response.json();
        alert(data.message);
    });

    // Stop trading (optional, implement stop logic as needed)
    stopBtn.addEventListener('click', function() {
        stopBtn.disabled = true;
        startBtn.disabled = false;
        alert("Stop trading functionality not implemented yet.");
    });

    // Fetch price every 2 seconds
    setInterval(() => {
        fetchPrice(symbolSelect.value);
    }, 2000);
});
