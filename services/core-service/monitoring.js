const Prometheus = require('prom-client');

// Create metrics
const httpRequestDurationMicroseconds = new Prometheus.Histogram({
    name: 'http_request_duration_ms',
    help: 'Duration of HTTP requests in ms',
    labelNames: ['route', 'method', 'status'],
    buckets: [5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000]
});

const ollamaRequestDurationMs = new Prometheus.Histogram({
    name: 'ollama_request_duration_ms',
    help: 'Duration of Ollama API requests in ms',
    labelNames: ['model', 'prompt_size'],
    buckets: [50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000]
});

const memoryOperationCounter = new Prometheus.Counter({
    name: 'memory_operations_total',
    help: 'Count of memory operations',
    labelNames: ['operation', 'status']
});

// Export metrics via HTTP endpoint
app.get('/metrics', async (req, res) => {
    res.set('Content-Type', Prometheus.register.contentType);
    res.end(await Prometheus.register.metrics());
}); 