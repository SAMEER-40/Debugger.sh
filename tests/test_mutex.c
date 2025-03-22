#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

#define NUM_THREADS 5  // Total 5 threads, but 3 will get stuck in a deadlock
pthread_mutex_t mutexes[NUM_THREADS];

void log_event(const char *action, int thread_id, int mutex_id) {
    FILE *log_file = fopen("mutex_log.txt", "a");
    if (log_file != NULL) {
        fprintf(log_file, "%s mutex %d by thread %d\n", action, mutex_id, thread_id);
        fclose(log_file);
    }
}

void *thread_func(void *arg) {
    int thread_id = *(int *)arg;
    int first_mutex, second_mutex;

    if (thread_id < 3) {
        // **Threads 0, 1, 2 will form a deadlock cycle**
        first_mutex = thread_id;
        second_mutex = (thread_id + 1) % 3;
    } else {
        // **Threads 3 and 4 will work normally**
        first_mutex = thread_id;
        second_mutex = (thread_id + 1) % NUM_THREADS;
    }

    // Lock First Mutex
    printf("Thread %d: Trying to acquire Mutex %d...\n", thread_id, first_mutex);
    log_event("Locking", thread_id, first_mutex);
    pthread_mutex_lock(&mutexes[first_mutex]);

    printf("Thread %d: Acquired Mutex %d\n", thread_id, first_mutex);
    sleep(1);

    // Lock Second Mutex (Potential Deadlock for Threads 0, 1, 2)
    printf("Thread %d: Trying to acquire Mutex %d...\n", thread_id, second_mutex);
    log_event("Locking", thread_id, second_mutex);
    pthread_mutex_lock(&mutexes[second_mutex]);

    printf("Thread %d: Acquired Mutex %d\n", thread_id, second_mutex);
    sleep(1);

    // Unlock in reverse order
    pthread_mutex_unlock(&mutexes[second_mutex]);
    log_event("Unlocking", thread_id, second_mutex);
    printf("Thread %d: Released Mutex %d\n", thread_id, second_mutex);

    pthread_mutex_unlock(&mutexes[first_mutex]);
    log_event("Unlocking", thread_id, first_mutex);
    printf("Thread %d: Released Mutex %d\n", thread_id, first_mutex);

    return NULL;
}

int main() {
    pthread_t threads[NUM_THREADS];
    int thread_ids[NUM_THREADS];

    // Initialize Mutexes
    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_mutex_init(&mutexes[i], NULL);
    }

    // Create Threads
    for (int i = 0; i < NUM_THREADS; i++) {
        thread_ids[i] = i;
        pthread_create(&threads[i], NULL, thread_func, &thread_ids[i]);
    }

    // Join Threads
    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    // Destroy Mutexes
    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_mutex_destroy(&mutexes[i]);
    }

    return 0;
}
