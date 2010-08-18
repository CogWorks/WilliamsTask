CFLAGS		+= -g -Wall -std=gnu99 -D_GNU_SOURCE -D_REENTRANT
LDFLAGS		+=
LDLIBS		+=
ARCH	    = lib/libjson.a

LIB_OBJS 	= src/debug.o \
		  src/linkhash.o \
		  src/printbuf.o \
		  src/arraylist.o \
		  src/json_object.o \
		  src/json_tokener.o

LIB_HDRS	= src/debug.h \
		  src/linkhash.h \
		  src/printbuf.h \
		  src/arraylist.h \
		  src/json_object.h \
		  src/json_tokener.h

TESTS		= src/test1 src/test2

all: ${ARCH}
$(ARCH): $(LIB_OBJS) ${LIB_HDRS} src/json.h
	mkdir -p lib
	$(AR) $(ARFLAGS) $(ARCH) $?
	cp src/*.h include/
tests: $(TESTS)
src/test1: src/test1.o $(LIB_OBJS)
src/test2: src/test2.o $(LIB_OBJS)

clean:
	rm -f src/*.o *~ $(TESTS) lib/*.a lib/*.exe

src/printbuf.o: src/printbuf.c src/printbuf.h
src/cex.o: src/cex.c src/cex.h
src/debug.o: src/debug.c src/debug.h
src/linkhash.o: src/linkhash.c src/linkhash.h
src/arraylist.o: src/arraylist.c src/arraylist.h
src/json_object.o: src/json_object.c $(LIB_HDRS)
src/json_tokener.o: src/json_tokener.c $(LIB_HDRS)
src/test1.o: src/test1.c $(LIB_HDRS)
src/test2.o: src/test2.c $(LIB_HDRS)

