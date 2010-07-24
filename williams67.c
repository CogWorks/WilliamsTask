#include <X11/Xlib.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
	unsigned long   flags;
	unsigned long   functions;
	unsigned long   decorations;
	long            inputMode;
	unsigned long   status;
} Hints;

int main(void) {
	Display *d;
	Window w;
	XEvent e;
	char *msg = "Hello, World!";
	int s;

	char *display_name = getenv("DISPLAY");

	/* open connection with the server */
	d = XOpenDisplay(display_name);
	if (d == NULL) {
		fprintf(stderr, "Cannot open display\n");
		exit(1);
	}

	s = DefaultScreen(d);

	/* create window */
	w = XCreateSimpleWindow(d, RootWindow(d, s), 0, 0, XDisplayWidth(d, s), XDisplayHeight(d, s), 0,
			BlackPixel(d, s), WhitePixel(d, s));

	Hints hints;
	Atom property;

	hints.flags = 2;
	hints.decorations = 0;

	property = XInternAtom(d, "_MOTIF_WM_HINTS",True);

	XChangeProperty(d,w,property,property,32,PropModeReplace,(unsigned char *)&hints,5);

	/* select kind of events we are interested in */
	XSelectInput(d, w, ExposureMask | KeyPressMask);

	/* map (show) the window */
	XMapWindow(d, w);

	/* event loop */
	while (1) {
		XNextEvent(d, &e);
		/* draw or redraw the window */
		if (e.type == Expose) {
			XFillRectangle(d, w, DefaultGC(d, s), 20, 20, 10, 10);
			XDrawString(d, w, DefaultGC(d, s), 50, 50, msg, strlen(msg));
		}
		/* exit on key press */
		if (e.type == KeyPress)
			break;
	}

	/* close connection to server */
	XCloseDisplay(d);

	return 0;
}
