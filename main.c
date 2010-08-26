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
 * Original experiment details
 *
 *
 * Visual field is 39 X 39 degrees, divided up into a 13 X 13 grid of 3 degree
 * square. Objects occupy 100 of the squares, chosen at random, except the
 * center is reserved for the target description.
 *
 * stimuli are in four sizes:
 * 2.8, 1.9, 1.3, 0.8 degrees, called very large, large, medium, and small
 *
 * 5 colors:
 * blue, green, yellow, orange, pink
 *
 * 5 shapes:
 * circle, semicircle, triangle, square, cross
 *
 * each stimulus has a two digit number 0-99
 *
 * probe is number, optionally with color, size, shape, verbally presented on
 * first slide, repeated on second.
 *
 * trial start
 * slide 1 probe
 * {button press}
 * slide 2 probe + description
 * {button press - when found}
 *
 * 30 subjects, two sessons, 200 trials per S.
 *
 */

/**
 * TODO: Convert pixel calculations from int to float+round()
 * TODO: Implement a diamond shape
 * TODO: Adjust font based on screen resolution
 * TODO: Add option to set custom number of rows and columns
 * TODO: ACT-R interface
 * TODO: Log to file
 * TODO: Keep track of probe study/rehersal time
 */

#define _GNU_SOURCE

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <sys/time.h>
#include <getopt.h>
#include <X11/keysym.h>
#include <X11/extensions/Xrandr.h>

#include "williams67.h"

void update_mouse() {
	char *msg = 0;
	asprintf(&msg, "{\"method\":\"set-mouse-pos\",\"params\":[%d,%d],\"prototype\":\"json-rpc-notification\"}",cursor_x,cursor_y);
	//printf("%s\n", msg);
	connection_send(msg);
}

void generate_w67_objects(int nrc, w67Object_t *objects, int no) {
	if (nrc % 2 != 1) {
		fprintf(stderr, "Number of rows and columns must be odd.");
		exit(1);
	}
	int max_cells = nrc * nrc;
	int center = (nrc-1)/2;
	int i, j;

	int offset = center * e->cell_width + center * e->cell_gap;
	int start_x = e->center_x - offset;
	int start_y = e->center_y - offset;

	//printf("Offset: %d, StartX: %d, StartY: %d\n", offset, start_x, start_y);

	i = 0;
	while (i<no) {
		pick_cell:
		objects[i].cell.x = random_int(nrc);
		objects[i].cell.y = random_int(nrc);
		if (objects[i].cell.x == center && objects[i].cell.y == center)
			goto pick_cell;
		for (j=0;j<i;j++) {
			if (objects[j].cell.x == objects[i].cell.x &&
					objects[j].cell.y == objects[i].cell.y) {
				goto pick_cell;
			}
		}
		pick_id:
		objects[i].id = random_int(no);
		for (j=0;j<i;j++) {
			if (objects[j].id == objects[i].id)
				goto pick_id;
		}

		pick_obj:
		objects[i].color = random_int(5);
		objects[i].shape = random_int(5);
		objects[i].size = random_int(4);
		for (j=0;j<i;j++) {
			if (objects[i].color == objects[j].color &&
					objects[i].size == objects[j].size &&
					objects[i].shape == objects[j].shape) {
				goto pick_obj;
			}
		}

		objects[i].origin.y = start_y + objects[i].cell.y * e->cell_width + objects[i].cell.y * e->cell_gap;
		objects[i].origin.x = start_x + objects[i].cell.x * e->cell_width + objects[i].cell.x * e->cell_gap;
		objects[i].width = objects[i].height = (int)e->cell_width * w67Sizes[objects[i].size];

		//printf("Loc-%d: (%d,%d)\n", i, objects[i].origin.x, objects[i].origin.y);
		i++;

	}

}

void w67init() {

	XInitThreads();

	Pixmap blank;
	XColor dummy;
	int i;
	Status rc;
	Colormap screen_colormap;
	XEvent xev;

	char data[1] = {0};
	char *display_name = getenv("DISPLAY");
	//printf("-> Display name: %s\n", display_name);

	srand(time(NULL));

	if (e) (free(e));
	e = malloc(sizeof(w67Experiment_t));

	e->d = XOpenDisplay(display_name);
	if (e->d == NULL) {
		printf("-> Cannot open display\n");
		exit(1);
	}

	e->s = DefaultScreen(e->d);
	e->r = RootWindow(e->d, e->s);

	e->w = XCreateSimpleWindow(e->d, e->r, 0, 0, XDisplayWidth(e->d, e->s),
			XDisplayHeight(e->d, e->s), 0, BlackPixel(e->d, e->s), WhitePixel(e->d, e->s));

	XMapRaised(e->d, e->w);

	XSelectInput(e->d, e->w, ExposureMask | KeyPressMask | ButtonPressMask | ButtonReleaseMask | PointerMotionMask);

	Window r;
	unsigned int d, b;
	XGetGeometry(e->d, e->w, &r, &e->x, &e->y, &e->screen_width, &e->screen_height, &b, &d);
	//printf("-> Screen Resolution (%d,%d) %d %d\n", e->screen_width, e->screen_height, e->x, e->y);

	memset(&xev, 0, sizeof(xev));
	xev.type = ClientMessage;
	xev.xclient.window = e->w;
	xev.xclient.message_type = XInternAtom(e->d, "_NET_WM_STATE", False);
	xev.xclient.format = 32;
	xev.xclient.data.l[0] = 1;
	xev.xclient.data.l[1] = XInternAtom(e->d, "_NET_WM_STATE_FULLSCREEN", False);
	xev.xclient.data.l[2] = 0;
	XSendEvent(e->d, e->r, False, SubstructureNotifyMask, &xev);
	XMoveResizeWindow(e->d, e->w, 0, 0, e->screen_width, e->screen_height);

	XMapWindow(e->d, e->w);

	XGrabPointer(e->d, e->w, True, 0, GrabModeAsync, GrabModeAsync, e->w, 0L, CurrentTime);
	XGrabKeyboard(e->d, e->w, False, GrabModeAsync, GrabModeAsync, CurrentTime);

	e->gc = DefaultGC(e->d, e->s);

	screen_colormap = DefaultColormap(e->d, e->s);

	for (i=0;i<W67_MAX_COLORS;i++) {
		rc = XAllocNamedColor(e->d, screen_colormap, w67ColorNames[i], &e->w67Colors[i], &e->w67Colors[i]);
		if (rc == 0) {
			printf("XAllocNamedColor - failed to allocated '%s' color.\n", w67ColorNames[i]);
			exit(1);
		}
	}

	XFreeColormap(e->d, screen_colormap);

	e->font = XLoadFont(e->d, "-adobe-courier-medium-r-normal--8-80-75-75-m-50-iso8859-1");
	XSetFont(e->d, e->gc, e->font);

	blank = XCreateBitmapFromData(e->d, e->w, data, 1, 1);
	if (blank == None) fprintf(stderr, "error: out of memory.\n");
	e->cursor = XCreatePixmapCursor(e->d, blank, blank, &dummy, &dummy, 0, 0);
	XFreePixmap(e->d, blank);
	//XDestroyWindow(e->d, e->w);
}

void do_set_cursor_loc() {
	char *s = 0;
	asprintf(&s, "{\"method\":\"setCursorLoc\",\"params\":[%d,%d],\"id\":666}\n", cursor_x, cursor_y);
	connection_send(s);
	free(s);
}

void doTrials(int trials) {

	int i;

	state = -1;
	struct timeval start_time;

	int excluded = 0;
	XEvent xev;
	char *id;

	int wx, wy, rx, ry;
	unsigned m;

	Window root, child;

	hideMouse();
	moveMouse(0,0);

	int trial = 0;

	while (trial<trials) {
		//XFlush(e->d);
		XNextEvent(e->d, &xev);
		if (xev.type == Expose) {
			if (state==-1) {
				Window r;
				unsigned int d, b;
				XGetGeometry(e->d, e->w, &r, &e->x, &e->y, &e->screen_width, &e->screen_height, &b, &d);
				//printf("-> Screen Resolution (%d,%d) %d %d\n", e->screen_width, e->screen_height, e->x, e->y);

				e->center_x = e->screen_width / 2;
				e->center_y = (e->screen_height - e->y) / 2;
				//printf("-> Center: (%d,%d)\n", e->center_x, e->center_y);

				e->cell_width = (e->screen_height - e->y) / (ROWS_AND_COLS+ROWS_AND_COLS*GAP+GAP);
				e->cell_gap = e->cell_width * GAP;
				//printf("-> Cell width: %d Cell gap: %d\n", e->cell_width, e->cell_gap);
				e->hcw = e->cell_width / 2;

				e->res_diff = ( e->screen_width - (e->screen_height - e->y)) / 2;
				//printf("-> Half resolution difference: %d\n", e->res_diff);

				state = 0;
				probe_index = random_int(MAX_OBJECTS);
				generate_w67_objects(ROWS_AND_COLS, objects, MAX_OBJECTS);
			} else if (state==1) {
				for (i=0;i<MAX_OBJECTS;i++)
					w67DrawObject(&objects[i]);
			}
			w67DrawProbe(&objects[probe_index]);
			if (port>0) {
				send_display_objects();
			}
		} else if (xev.type == MotionNotify) {
			cursor_x = xev.xmotion.x;
			cursor_y = xev.xmotion.y;
			update_mouse();
		} else if (xev.type == ButtonPress && state==1) {
			XQueryPointer(e->d, e->r, &root, &child, &rx, &ry, &wx, &wy, &m);
			int found = 0;
			for (i=0;i<MAX_OBJECTS;i++) {
				if (abs(wx-objects[i].origin.x)<e->hcw && abs(wy-objects[i].origin.y)<e->hcw && i==probe_index) {
					found = 1;
					break;
				}
			}
			if (found) {
				struct timeval end_time;
				gettimeofday(&end_time, NULL);
				double t1 = start_time.tv_sec+(start_time.tv_usec/1000000.0);
				double t2 = end_time.tv_sec+(end_time.tv_usec/1000000.0);
				trial++;
				printf("Trial %d: %.2f seconds\n", trial, t2-t1);
				if (trial<trials) {
					XClearWindow(e->d, e->w);
					hideMouse();
					probe_index = random_int(MAX_OBJECTS);
					generate_w67_objects(ROWS_AND_COLS, objects, MAX_OBJECTS);
					w67DrawProbe(&objects[probe_index]);
					state = 0;
					if (port>0) send_display_objects();
				}
			}
		} else if (xev.type == KeyPress && state==0) {
			if ((port>0 && xev.xkey.keycode == XK_f) ||
					(port==0 && xev.xkey.keycode == XKeysymToKeycode(e->d, XK_f))) {
				for (i=0;i<MAX_OBJECTS;i++)
					w67DrawObject(&objects[i]);
				moveMouse(e->center_x, e->center_y);
				unhideMouse(e);
				gettimeofday(&start_time, NULL);
				state = 1;
				if (port>0) send_display_objects();
			}
		}
	}

	done:

	XCloseDisplay(e->d);

}

void showUsage() {
	printf("Usage: williams67 [OPTION]\n");
	printf("\nOptions:\n");
	printf("  -h, --help\t\t\tShow usage\n");
	printf("  -t trials, --trials=trials\tNumber of trials\n");
	printf("  -R port, --act-r=port\t\tAccept ACT-R connection on port\n");
}

void GetScreenSize(int *width, int *height) {

	int num_sizes;
	Rotation original_rotation;

	Display *dpy = XOpenDisplay(NULL);
	Window root = RootWindow(dpy, 0);
	XRRScreenSize *xrrs = XRRSizes(dpy, 0, &num_sizes);

	XRRScreenConfiguration *conf = XRRGetScreenInfo(dpy, root);
	short original_rate = XRRConfigCurrentRate(conf);
	SizeID original_size_id = XRRConfigCurrentConfiguration(conf, &original_rotation);

	*width=xrrs[original_size_id].width;
	*height=xrrs[original_size_id].height;

	XCloseDisplay(dpy);

}

int main(int argc, char* argv[] ) {

	struct option long_options[] = {
			{"help", 	no_argument,       0, 'h'},
			{"trials",  required_argument, 0, 't'},
			{"act-r", 	required_argument, 0, 'R'},
			{0, 0, 0, 0}
	};

	e = 0;
	state = -1;

	int c;
	int option_index = 0;
	int trials = 1;
	port = 0;
	cursor_x = 0;
	cursor_y = 0;

	while (1) {

		c = getopt_long (argc, argv, "ht:R:",
				long_options, &option_index);

		if (c == -1)
			break;

		switch (c) {
		case 0:
			if (long_options[option_index].flag != 0)
				break;
			showUsage();
			exit(1);

		case 'h':
			showUsage();
			exit(0);

		case 'R':
			port = atoi(optarg);
			break;

		case 't':
			trials = atoi(optarg);
			break;

		case '?':
			exit(1);

		default:
			abort();
		}

	}

	w67Experiment_t e;

	if (port>0) {
		wait_for_actr_connections(port);
	} else {
		w67init(&e);
		doTrials(trials);
	}

}
