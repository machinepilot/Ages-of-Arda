#include <pthread.h>

typedef struct {
    char* event_data;
    event_type_t event_type;
    int priority;
} mcp_event_t;

// Thread-safe event queue
typedef struct {
    mcp_event_t* events;
    int capacity;
    int size;
    int head;
    int tail;
    pthread_mutex_t mutex;
    pthread_cond_t not_empty;
    pthread_cond_t not_full;
} event_queue_t;

// Worker thread function to process events
void* event_worker(void* arg) {
    event_queue_t* queue = (event_queue_t*)arg;
    
    while (1) {
        pthread_mutex_lock(&queue->mutex);
        
        // Wait if queue is empty
        while (queue->size == 0) {
            pthread_cond_wait(&queue->not_empty, &queue->mutex);
        }
        
        // Get next event
        mcp_event_t event = queue->events[queue->head];
        queue->head = (queue->head + 1) % queue->capacity;
        queue->size--;
        
        // Signal that queue is not full
        pthread_cond_signal(&queue->not_full);
        pthread_mutex_unlock(&queue->mutex);
        
        // Process event without holding lock
        process_mcp_event(&event);
        
        // Free event data
        free(event.event_data);
    }
    
    return NULL;
} 