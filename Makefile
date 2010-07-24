all: clean williams67

clean:
	rm -f williams67

williams67:
	$(CC) williams67.c -o williams67 -lX11 -lXxf86vm