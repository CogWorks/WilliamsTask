LIB_JSON        = ../json/src/.libs/libjson.a
INCLUDE_JSON    = ../json/src

CFLAGS		    += -g -Wall -std=gnu99 -D_GNU_SOURCE -D_REENTRANT \
					-I${INCLUDE_JSON}
LDFLAGS		    +=
LDLIBS		    +=
ARCH	        = lib/libjsonrpc.a

LIB_OBJS 	    = src/jsonrpc.o src/hashmap.o src/circular_buffer.o
LIB_HDRS	    = src/jsonrpc.h src/hashmap.h src/circular_buffer.h


all: ${ARCH}

.c.o:
	cc -c -o $@ $(DEBUG) $(CFLAGS) $(IFLAGS) $<

$(ARCH): $(LIB_OBJS) ${LIB_HDRS} 
	$(AR) $(ARFLAGS) $(ARCH) $?
	cp src/*.h include/


clean:
	rm -f src/*.o *~ lib/*.a lib/*.exe

src/circular_buffer.o: src/circular_buffer.c src/circular_buffer.h
src/hashmap.o: src/hashmap.c src/hashmap.h
src/jsonrpc.o: src/jsonrpc.c src/jsonrpc.h src/hashmap.h

src/circular_buffer: src/circular_buffer.o src/circular_buffer.o 
