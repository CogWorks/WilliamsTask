all: clean williams67

clean:
	rm -f williams67

williams67:
	$(CC) williams67.c -o williams67 -L/usr/X11/lib -lX11 -lXxf86vm -lm
