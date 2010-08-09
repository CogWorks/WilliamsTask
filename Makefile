CFLAGS		:=	-g -pedantic -std=c99
LDFLAGS		:=	-L/usr/X11/lib -lX11 -lXxf86vm -lm
SOURCES		:=	experiment.c utils.c draw.c main.c 
OBJECTS		:=	$(SOURCES:.c=.o)
EXECUTABLE	:=	williams67

.PHONY		:=	clean

all: $(SOURCES) $(EXECUTABLE)

$(EXECUTABLE): $(OBJECTS) 
	$(CC) $(OBJECTS) $(LDFLAGS) -o $@

.c.o:
	$(CC) $(CFLAGS) $(LDFLAGS) -c $<
	
clean:
	rm -f *.o; rm -f $(EXECUTABLE)