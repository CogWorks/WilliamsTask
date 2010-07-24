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

XPoint ** get_cell_origins(xres, yres, n) {
	XPoint **points = malloc(n*sizeof(XPoint*));
	int min_res = -1;
	int res_diff = -1;
	int i, j;
	if (yres<xres) {
		min_res = yres / n;
		res_diff = ( xres - yres ) / 2;
		for (i=0;i<n;i++) {
			points[i] = malloc(n*sizeof(XPoint*));
			for (j=0;j<n;j++) {
				points[i][j].y = i * min_res + (min_res / 2);
				points[i][j].x = j * min_res + res_diff + (min_res / 2);
				//printf("x: %d, y: %d\n", points[i][j].x, points[i][j].y);
			}
		}
	} else {
		min_res = xres / n;
		res_diff = ( yres - xres ) / 2;
		for (i=0;i<n;i++) {
			points[i] = malloc(n*sizeof(XPoint*));
			for (j=0;j<n;j++) {
				points[i][j].y = i * min_res + res_diff + (min_res / 2);
				points[i][j].x = j * min_res + (min_res / 2);
				//printf("x: %d, y: %d\n", points[i][j].x, points[i][j].y);
			}
		}
	}
	return points;
}

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

	XPoint **points = get_cell_origins(XDisplayWidth(d, s), XDisplayHeight(d, s), 13);
	int i, j;

	/* event loop */
	while (1) {
		XNextEvent(d, &e);
		/* draw or redraw the window */
		if (e.type == Expose) {
			for (i=0;i<13;i++) {
				for (j=0;j<13;j++) {
					XDrawPoint(d, w, DefaultGC(d, s), points[i][j].x, points[i][j].y);
				}
			}
			XFillRectangle(d, w, DefaultGC(d, s), 20, 20, 10, 10);
			XFillRectangle(d, w, DefaultGC(d, s), 550, 50, 10, 10);
			XFillRectangle(d, w, DefaultGC(d, s), 1000, 400, 10, 10);
			XFillRectangle(d, w, DefaultGC(d, s), 40, 500, 10, 10);
			XPoint points[13];
			points[0].x = 100;
			points[0].y = 100;
			points[1].x = 110;
			points[1].y = 100;
			points[2].x = 110;
			points[2].y = 110;
			points[3].x = 120;
			points[3].y = 110;
			points[4].x = 120;
			points[4].y = 100;
			points[5].x = 130;
			points[5].y = 100;
			points[6].x = 130;
			points[6].y = 90;
			points[7].x = 120;
			points[7].y = 90;
			points[8].x = 120;
			points[8].y = 80;
			points[9].x = 110;
			points[9].y = 80;
			points[10].x = 110;
			points[10].y = 90;
			points[11].x = 100;
			points[11].y = 90;
			points[12].x = 100;
			points[12].y = 90;
			XFillPolygon(d, w, DefaultGC(d, s), points, 13, Nonconvex, CoordModeOrigin);
			XDrawString(d, w, DefaultGC(d, s), 50, 50, msg, strlen(msg));
			XFillArc(d, w, DefaultGC(d, s), 500, 300, 40, 40, 0, 23040);
		}
		/* exit on key press */
		if (e.type == KeyPress)
			break;
	}

	/* close connection to server */
	XCloseDisplay(d);

	return 0;
}
