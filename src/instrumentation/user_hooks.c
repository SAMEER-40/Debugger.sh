#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <pthread.h>
#include <time.h>
#include <unistd.h>

static int (*real_pthread_mutex_lock)(pthread_mutex_t *mutex) = NULL;
static int (*real_pthread_mutex_unlock)(pthread_mutex_t *mutex) = NULL;
static FILE *log_file = NULL;  // Log file pointer

// Get timestamp with nanosecond precision
void get_timestamp(char* buffer, size_t size) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    snprintf(buffer, size, "%ld.%09ld", ts.tv_sec, ts.tv_nsec);
}

// Initialize hooks
void init_hooks() {
    if (!real_pthread_mutex_lock) {
        real_pthread_mutex_lock = dlsym(RTLD_NEXT, "pthread_mutex_lock");
    }
    if (!real_pthread_mutex_unlock) {
        real_pthread_mutex_unlock = dlsym(RTLD_NEXT, "pthread_mutex_unlock");
    }

    if (!log_file) {
        log_file = fopen("mutex_log.txt", "a");
        if (!log_file) {
            perror("Error opening mutex_log.txt");
            exit(EXIT_FAILURE);
        }
    }
}

// Hook for pthread_mutex_lock
int pthread_mutex_lock(pthread_mutex_t *mutex) {
    init_hooks();

    if (log_file) {
        char timestamp[32];
        get_timestamp(timestamp, sizeof(timestamp));

        flockfile(log_file);  // Lock file for thread-safe logging
        fprintf(log_file, "[%s] THREAD %lu: Locking mutex %p\n", timestamp, pthread_self(), mutex);
        fflush(log_file);
        funlockfile(log_file);  // Unlock file
    }

    return real_pthread_mutex_lock(mutex);
}

// Hook for pthread_mutex_unlock
int pthread_mutex_unlock(pthread_mutex_t *mutex) {
    init_hooks();

    if (log_file) {
        char timestamp[32];
        get_timestamp(timestamp, sizeof(timestamp));

        flockfile(log_file);
        fprintf(log_file, "[%s] THREAD %lu: Unlocking mutex %p\n", timestamp, pthread_self(), mutex);
        fflush(log_file);
        funlockfile(log_file);
    }

    return real_pthread_mutex_unlock(mutex);
}

// Destructor to close log file on exit
__attribute__((destructor))
void cleanup() {
    if (log_file) {
        fclose(log_file);
        log_file = NULL;
    }
}
