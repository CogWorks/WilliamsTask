#include <X11/Xlib.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

Display *d;
Window w;
GC gc;

XColor w67Colors[7];
float w67Sizes[] = {0.3, 0.5, 0.7};

int screen_width;
int screen_height;

int cell_width;

typedef enum {
	CROSS,
	SQUARE,
	CIRCLE,
	TRIANGLE,
	STAR,
	SEMICIRCLE,
	DIAMOND
} w67Shape_t;

typedef enum {
	BLUE,
	GREEN,
	ORANGE,
	PINK,
	YELLOW,
	BLACK,
	WHITE
} w67Color_t;

typedef enum {
	SMALL,
	MEDIUM,
	LARGE,
} w67Size_t;

int random_int(int upper_bound) {
	return (int) ( (float)upper_bound * rand() / (RAND_MAX + 1.0) );
}

void rotate(XPoint *points, int npoints, int rx, int ry, float angle) {
    int i;
    for (i=0; i<npoints; i++) {
	float x, y;
	x = points[i].x - rx;
	y = points[i].y - ry;
	points[i].x =  rx + x * cosf(angle) - y * sinf(angle);
	points[i].y =  ry + x * sinf(angle) + y * cosf(angle);
    }
}

void w67DrawTriangle(Display *d, Window w, GC gc, int x, int y, int width, int angle) {
	XPoint points[4];
	int radius = width/2;
	int adj = radius - 3 * radius / sqrt(3) / 2;
	points[0].x = x;
	points[0].y = y - radius + adj;
	points[1].x = x + radius * cos(210);
	points[1].y = y + radius * sin(210) + adj;
	points[2].x = x - radius * cos(330);
	points[2].y = points[1].y  + adj;
	points[3].x = points[0].x;
	points[3].y = points[0].y;
	XFillPolygon(d, w, gc, points, 4, Convex, CoordModeOrigin);
}

void w67DrawStar(Display *d, Window w, GC gc, int x, int y, int arms, int rOuter, int rInner, int angle) {
	XPoint points[2*arms+1];
    double a = 3.141592653589793238462643 / arms;
    int i = 0;
    for (; i < 2 * arms; i++) {
        double r = (i & 1) == 0 ? rOuter : rInner;
        points[i].x = x + cos(i * a) * r;
        points[i].y = y + sin(i * a) * r;
    }
    points[i].x = points[0].x;
    points[i].y = points[0].y;
    XFillPolygon(d, w, gc, points, 2*arms+1, Nonconvex, CoordModeOrigin);
}

void w67DrawCross(Display *d, Window w, GC gc, int x, int y, int width, int angle) {
	XPoint points[13];
	int side = width / 3;
	points[0].x = x - 1.5 * side;
	points[0].y = y - 0.5 * side;
	points[1].x = points[0].x + side;
	points[1].y = points[0].y;
	points[2].x = points[1].x;
	points[2].y = points[1].y - side;
	points[3].x = points[2].x + side;
	points[3].y = points[2].y;
	points[4].x = points[3].x;
	points[4].y = points[3].y + side;
	points[5].x = points[4].x + side;
	points[5].y = points[4].y;
	points[6].x = points[5].x;
	points[6].y = points[5].y + side;
	points[7].x = points[6].x - side;
	points[7].y = points[6].y;
	points[8].x = points[7].x;
	points[8].y = points[7].y + side;
	points[9].x = points[8].x - side;
	points[9].y = points[8].y;
	points[10].x = points[9].x;
	points[10].y = points[9].y - side;
	points[11].x = points[10].x - side;
	points[11].y = points[10].y;
	points[12].x = points[11].x;
	points[12].y = points[11].y;
	XFillPolygon(d, w, gc, points, 13, Nonconvex, CoordModeOrigin);
}

void w67DrawObject(w67Shape_t shape, w67Color_t color, w67Size_t size, int x, int y, int angle) {

	XSetForeground(d, gc, w67Colors[color].pixel);

	int cw = cell_width*w67Sizes[size];

	switch (shape) {
	case CROSS:
		w67DrawCross(d,w,gc,x,y,cw,angle);
		break;
	case SQUARE:
		XFillRectangle(d, w, gc, x-.5*cw, y-.5*cw, cw, cw);
		break;
	case CIRCLE:
		XFillArc(d, w, gc, x-.5*cw, y-.5*cw, cw, cw, 0, 23040);
		break;
	case TRIANGLE:
		w67DrawTriangle(d, w, gc, x, y, cw, 0);
		break;
	case SEMICIRCLE:
		XFillArc(d, w, gc, x-.5*cw, y-.5*cw, cw, cw, 33, 11520);
		break;
	case STAR:
		w67DrawStar(d,w,gc,x,y,5, cw/2, cw/3.5, angle);
		break;
	}

	XSetForeground(d, gc, w67Colors[BLACK].pixel);

}

XPoint ** get_cell_origins(int xres, int yres, int n, int *len) {
	XPoint **points = malloc(n*sizeof(XPoint*));
	int res_diff = -1;
	int i, j;
	if (yres<xres) {
		*len = yres / n;
		res_diff = ( xres - yres ) / 2;
		for (i=0;i<n;i++) {
			points[i] = malloc(n*sizeof(XPoint*));
			for (j=0;j<n;j++) {
				points[i][j].y = i * *len + (*len / 2);
				points[i][j].x = j * *len + res_diff + (*len / 2);
				//printf("x: %d, y: %d\n", points[i][j].x, points[i][j].y);
			}
		}
	} else {
		*len = xres / n;
		res_diff = ( yres - xres ) / 2;
		for (i=0;i<n;i++) {
			points[i] = malloc(n*sizeof(XPoint*));
			for (j=0;j<n;j++) {
				points[i][j].y = i * *len + res_diff + (*len / 2);
				points[i][j].x = j * *len + (*len / 2);
				//printf("x: %d, y: %d\n", points[i][j].x, points[i][j].y);
			}
		}
	}
	return points;
}

void w67init() {

	int s;
	Status rc;
	Colormap screen_colormap;
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

	XMapRaised(d,w);

	/* select kind of events we are interested in */
	XSelectInput(d, w, ExposureMask | KeyPressMask);

	XEvent xev;
	memset(&xev, 0, sizeof(xev));
	xev.type = ClientMessage;
	xev.xclient.window = w;
	xev.xclient.message_type = XInternAtom(d, "_NET_WM_STATE", False);
	xev.xclient.format = 32;
	xev.xclient.data.l[0] = 1;
	xev.xclient.data.l[1] = XInternAtom(d, "_NET_WM_STATE_FULLSCREEN", False);
	xev.xclient.data.l[2] = 0;
	XSendEvent(d, DefaultRootWindow(d), False, SubstructureNotifyMask, &xev);
	XMoveResizeWindow(d,w,0,0,XDisplayWidth(d,s),XDisplayHeight(d,s));

	/* map (show) the window */
	XMapWindow(d, w);

	XGrabPointer(d,w,True,0,GrabModeAsync,GrabModeAsync,w,0L,CurrentTime);
	XGrabKeyboard(d,w,False,GrabModeAsync,GrabModeAsync,CurrentTime);

	gc = DefaultGC(d, s);

	screen_colormap = DefaultColormap(d, s);

	rc = XAllocNamedColor(d, screen_colormap, "black", &w67Colors[BLACK], &w67Colors[BLACK]);
	if (rc == 0) {
		fprintf(stderr, "XAllocNamedColor - failed to allocated 'pink' color.\n");
		exit(1);
	}
	rc = XAllocNamedColor(d, screen_colormap, "white", &w67Colors[WHITE], &w67Colors[WHITE]);
	if (rc == 0) {
		fprintf(stderr, "XAllocNamedColor - failed to allocated 'pink' color.\n");
		exit(1);
	}
	rc = XAllocNamedColor(d, screen_colormap, "pink", &w67Colors[PINK], &w67Colors[PINK]);
	if (rc == 0) {
		fprintf(stderr, "XAllocNamedColor - failed to allocated 'pink' color.\n");
		exit(1);
	}
	rc = XAllocNamedColor(d, screen_colormap, "orange", &w67Colors[ORANGE], &w67Colors[ORANGE]);
	if (rc == 0) {
		fprintf(stderr, "XAllocNamedColor - failed to allocated 'orange' color.\n");
		exit(1);
	}
	rc = XAllocNamedColor(d, screen_colormap, "blue", &w67Colors[BLUE], &w67Colors[BLUE]);
	if (rc == 0) {
		fprintf(stderr, "XAllocNamedColor - failed to allocated 'blue' color.\n");
		exit(1);
	}
	rc = XAllocNamedColor(d, screen_colormap, "yellow", &w67Colors[YELLOW], &w67Colors[YELLOW]);
	if (rc == 0) {
		fprintf(stderr, "XAllocNamedColor - failed to allocated 'yellow' color.\n");
		exit(1);
	}
	rc = XAllocNamedColor(d, screen_colormap, "green", &w67Colors[GREEN], &w67Colors[GREEN]);
	if (rc == 0) {
		fprintf(stderr, "XAllocNamedColor - failed to allocated 'green' color.\n");
		exit(1);
	}

	screen_width = XDisplayWidth(d, s);
	screen_height = XDisplayHeight(d, s);

}

int main(int argc, char* argv[] ) {

	srand(time(NULL));

	w67init();

	char *msg = "Hello, World!";

	XPoint **points = get_cell_origins(screen_width, screen_height, 13, &cell_width);
	//printf("Cell side length: %d\n", len);
	int i, j;

	int excluded = 0;
	XEvent e;
	/* event loop */
	while (1) {
		XNextEvent(d, &e);
		/* draw or redraw the window */
		if (e.type == Expose) {
			for (i=0;i<13;i++) {
				for (j=0;j<13;j++) {
					if (i == 6 && j == 6) continue;
					if (excluded >=0 && random_int(169)<69) {
						excluded++;
						continue;
					}
					int color = random_int(5);
					int size = random_int(3);
					int shape = random_int(5);
					printf("Color: %d, Size: %d\n", color, size);
					w67DrawObject(shape, color, size, points[i][j].x, points[i][j].y, 0);
					XDrawPoint(d, w, gc, points[i][j].x, points[i][j].y);
				}
			}
		}
		/* exit on key press */
		if (e.type == KeyPress)
			break;
	}

	/* close connection to server */
	XCloseDisplay(d);

	return 0;
}
