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

	//XF86VidModeSwitchToMode(d,DefaultScreen(d), 0);
	XF86VidModeSetViewPort(d,DefaultScreen(d),0,0);
	XMoveResizeWindow(d,w,0,0,XDisplayWidth(d,s),XDisplayHeight(d,s));
	XMapRaised(d,w);
	XGrabPointer(d,w,True,0,GrabModeAsync,GrabModeAsync,w,0L,CurrentTime);
	XGrabKeyboard(d,w,False,GrabModeAsync,GrabModeAsync,CurrentTime);

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
			XFillRectangle(d, w, DefaultGC(d, s), 550, 50, 10, 10);
			XFillRectangle(d, w, DefaultGC(d, s), 1000, 400, 10, 10);
			XFillRectangle(d, w, DefaultGC(d, s), 40, 500, 10, 10);
			XPoint points[3];
			points[0].x = 13;
			points[0].y = 53;
			points[1].x = 133;
			points[1].y = 63;
			points[2].x = 83;
			points[2].y = 83;
			points[3].x = 13;
			points[3].y = 53;
			XFillPolygon(d, w, DefaultGC(d, s), points, 4, Nonconvex, CoordModeOrigin);
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
