#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

pthread_mutex_t mutexA, mutexB;

void* thread_func_1(void* arg) {
    printf("Thread 1: Trying to acquire Mutex A...\n");
    pthread_mutex_lock(&mutexA);
    printf("Thread 1: Acquired Mutex A, doing work...\n");
    sleep(1);

    printf("Thread 1: Trying to acquire Mutex B...\n");
    if (pthread_mutex_trylock(&mutexB) == 0) {  // Try lock instead of blocking forever
        printf("Thread 1: Acquired Mutex B, doing work...\n");

        pthread_mutex_unlock(&mutexB);
        printf("Thread 1: Released Mutex B\n");
    } else {
        printf("Thread 1: Could not acquire Mutex B, avoiding deadlock!\n");
    }

    pthread_mutex_unlock(&mutexA);
    printf("Thread 1: Released Mutex A\n");

    return NULL;
}

void* thread_func_2(void* arg) {
    printf("Thread 2: Trying to acquire Mutex B...\n");
    pthread_mutex_lock(&mutexB);
    printf("Thread 2: Acquired Mutex B, doing work...\n");
    sleep(1);

    printf("Thread 2: Trying to acquire Mutex A...\n");
    if (pthread_mutex_trylock(&mutexA) == 0) {  // Try lock instead of blocking forever
        printf("Thread 2: Acquired Mutex A, doing work...\n");

        pthread_mutex_unlock(&mutexA);
        printf("Thread 2: Released Mutex A\n");
    } else {
        printf("Thread 2: Could not acquire Mutex A, avoiding deadlock!\n");
    }

    pthread_mutex_unlock(&mutexB);
    printf("Thread 2: Released Mutex B\n");

    return NULL;
}

int main() {
    pthread_t t1, t2;

    pthread_mutex_init(&mutexA, NULL);
    pthread_mutex_init(&mutexB, NULL);

    pthread_create(&t1, NULL, thread_func_1, NULL);
    pthread_create(&t2, NULL, thread_func_2, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    pthread_mutex_destroy(&mutexA);
    pthread_mutex_destroy(&mutexB);

    return 0;
}
