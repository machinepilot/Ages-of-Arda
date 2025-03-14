CC = gcc
CFLAGS = -Wall -Wextra -g -I.
LDFLAGS = -lcurl -ljansson -lpthread

all: test-mcp-client test-bard

mcp-client.o: mcp-client.c mcp-client.h
	$(CC) $(CFLAGS) -c mcp-client.c

bard.o: bard.c bard.h mcp-client.h
	$(CC) $(CFLAGS) -c bard.c

test-mcp-client.o: test-mcp-client.c mcp-client.h
	$(CC) $(CFLAGS) -c test-mcp-client.c

test-mcp-client: test-mcp-client.o mcp-client.o
	$(CC) -o test-mcp-client test-mcp-client.o mcp-client.o $(LDFLAGS)

test-bard.o: test-bard.c bard.h
	$(CC) $(CFLAGS) -c test-bard.c

test-bard: test-bard.o bard.o mcp-client.o
	$(CC) -o test-bard test-bard.o bard.o mcp-client.o $(LDFLAGS)

clean:
	rm -f *.o test-mcp-client test-bard

.PHONY: all clean 