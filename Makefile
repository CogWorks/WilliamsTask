CFLAGS		:=	-g -pedantic -std=c99
LDFLAGS		:=	-L/usr/X11/lib -lX11 -lXxf86vm -lm -lpthread
SOURCES		:=	act-r.c experiment.c utils.c draw.c main.c 
ARCHIVES	:=	jsonrpc/lib/libjsonrpc.a json/lib/libjson.a
OBJECTS		:=	$(SOURCES:.c=.o)
EXECUTABLE	:=	williams67

.PHONY		:=	json jsonrpc clean

all: $(ARCHIVES) $(SOURCES) $(EXECUTABLE)

$(EXECUTABLE): $(ARCHIVES) $(THIRDPARTY) $(OBJECTS) 
	$(CC) $(OBJECTS) $(ARCHIVES) $(LDFLAGS) -o $@

.c.o:
	$(CC) $(CFLAGS) $(LDFLAGS) -c $<

json/lib/libjson.a: jsonrpc/lib/libjsonrpc.a
	cd json; $(MAKE)

jsonrpc/lib/libjsonrpc.a:
	cd jsonrpc; $(MAKE)

clean:
	rm -f *.o; rm -f $(EXECUTABLE)
	cd json; $(MAKE) clean
	cd jsonrpc; $(MAKE) clean
