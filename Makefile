CC = gcc
CFLAGS = -Wall -g -fPIC -D_GNU_SOURCE
LDFLAGS = -ldl -pthread
TARGET = mutex_hook.so

# Source files
SRCS = src/instrumentation/user_hooks.c
OBJS = $(SRCS:.c=.o)

# Default target
all: $(TARGET)

# Build shared library
$(TARGET): $(OBJS)
	$(CC) -shared -o $@ $^ $(LDFLAGS)

# Compile .c files to .o
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Clean build files
clean:
	rm -f src/instrumentation/*.o $(TARGET)
	rm -f mutex_log.txt lock_graph.png

# Run tests
run-test: $(TARGET)
	LD_PRELOAD=./$(TARGET) ./tests/test_mutex
