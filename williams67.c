/*=============================================================================
 Copyright (C) 2010 Ryan Hope <rmh3093@gmail.com>

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU General Public License
 as published by the Free Software Foundation; either version 2
 of the License, or (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 =============================================================================*/

/**
 * TODO: Convert pixel calculations from int to float+round()
 * TODO: Randomize ids
 * TODO: Implement a diamond shape
 * TODO: Display probe
 * TODO: Collect mouse events
 */

#include <X11/Xlib.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

Display *d;
Window w;
GC gc;

XColor w67Colors[7];
float w67Sizes[] = {0.3, 0.4625, 0.625, 0.95};

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
	TINY,
	SMALL,
	MEDIUM,
	LARGE,
} w67Size_t;

typedef struct {
	int			id;
	w67Color_t	color;
	w67Shape_t	shape;
	w67Size_t	size;
	XPoint		origin;
} w67Object_t;

int random_int(int upper_bound) {
	return (int) ( (float)upper_bound * rand() / (RAND_MAX + 1.0) );
}

void shuffle(int *array, size_t n) {
	if (n > 1) {
		size_t i;
		for (i = 0; i < n - 1; i++) {
			size_t j = i + rand() / (RAND_MAX / (n - i) + 1);
			int t = array[j];
			array[j] = array[i];
			array[i] = t;
		}
	}
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

void w67DrawTriangle(Display *d, Window w, GC gc, int x, int y, int width) {
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

void w67DrawStar(Display *d, Window w, GC gc, int x, int y, int arms, int rOuter, int rInner) {
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

void w67DrawCross(Display *d, Window w, GC gc, int x, int y, int width) {
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

void w67DrawObject(w67Object_t object) {

	XSetForeground(d, gc, w67Colors[object.color].pixel);

	int cw = (int)cell_width*w67Sizes[object.size];

	switch (object.shape) {
	case CROSS:
		w67DrawCross(d,w,gc,object.origin.x,object.origin.y,cw);
		break;
	case SQUARE:
		XFillRectangle(d, w, gc, object.origin.x-.5*cw, object.origin.y-.5*cw, cw, cw);
		break;
	case CIRCLE:
		XFillArc(d, w, gc, object.origin.x-.5*cw, object.origin.y-.5*cw, cw, cw, 0, 23040);
		break;
	case TRIANGLE:
		w67DrawTriangle(d, w, gc, object.origin.x, object.origin.y, cw);
		break;
	case SEMICIRCLE:
		XFillArc(d, w, gc, object.origin.x-.5*cw, object.origin.y-.5*cw, cw, cw, 33, 11520);
		break;
	case STAR:
		w67DrawStar(d,w,gc,object.origin.x,object.origin.y,5, cw/2, cw/3.5);
		break;
	}

	XSetForeground(d, gc, w67Colors[BLACK].pixel);

}

void generate_w67_objects(int xres, int yres, int nrc, w67Object_t *objects, int no, int *len) {
	if (nrc % 2 != 1) {
		fprintf(stderr, "Number of rows and columns must be odd.");
		exit(1);
	}
	int max_cells = nrc * nrc;
	int center = (nrc-1)/2;
	int res_diff = -1;
	int excluded = 0;
	int i, j, k;
	int ci;

	*len = yres / nrc;
	res_diff = ( xres - yres ) / 2;
generate:
	ci = 0;
	for (i=0;i<nrc;i++) {
		for (j=0;j<nrc;j++) {
			if (i == center && j == center) continue;
			if (excluded >=0 && random_int(max_cells)<(max_cells-no)) {
				excluded++;
				continue;
			}
			objects[ci].origin.y = i * *len + (*len / 2);
			objects[ci].origin.x = j * *len + res_diff + (*len / 2);
			int unique = True;
			while (True) {
				objects[ci].color = random_int(5);
				objects[ci].shape = random_int(5);
				objects[ci].size = random_int(4);
				for (k=0;k<ci;k++) {
					if (objects[ci].color == objects[k].color &&
							objects[ci].size == objects[k].size &&
							objects[ci].shape == objects[k].shape) {
						unique = False;
						break;
					}
				}
				if (unique) {
					break;
				} else {
					unique = True;
				}
			}
			objects[ci].id = ci;
			ci++;
			if (ci==no) goto verify;
		}
	}
verify:
	if (i!=(nrc-1)) goto generate;
	else if (j<center) goto generate;
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

	w67Object_t objects[100];
	memset(&objects, 0, sizeof(objects));
	generate_w67_objects(screen_width, screen_height, 13, objects, 100, &cell_width);

	int i;

	int excluded = 0;
	XEvent e;
	char *id;

	Font font;
	font = XLoadFont(d, "-adobe-courier-medium-r-normal--8-80-75-75-m-50-iso8859-1");
	XSetFont(d, gc, font);

	int angle;
	/* event loop */
	while (1) {
		XNextEvent(d, &e);
		/* draw or redraw the window */
		if (e.type == Expose) {
			for (i=0;i<100;i++) {
				angle = random_int(360);
				w67DrawObject(objects[i]);
				asprintf(&id, "%.2d", objects[i].id);
				XDrawString(d, w, gc, objects[i].origin.x, objects[i].origin.y, id, 2);
				free(id);
				//XDrawPoint(d, w, gc, objects[i].origin.x, objects[i].origin.y);
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
