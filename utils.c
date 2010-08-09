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

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>

#include "williams67.h"

int random_int(int upper_bound) {
	return (int) ( (float)upper_bound * rand() / (RAND_MAX + 1.0) );
}

double distance(int x1, int y1, int x2, int y2) {
	return sqrt((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1));
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

void hideMouse(w67Experiment_t *e) {
	XDefineCursor(e->d, e->w, e->cursor);
}

void unhideMouse(w67Experiment_t *e) {
	XUndefineCursor(e->d, e->w);
}

void moveMouse(w67Experiment_t *e, int x, int y) {
	XWarpPointer(e->d, None, e->w, 0,0,0,0, e->screen_width/2, e->screen_height/2);
}

void clickMouse(w67Experiment_t *e, int button) {

	XEvent event;
	memset(&event, 0x00, sizeof(event));
	event.type = ButtonPress;
	event.xbutton.button = button;
	event.xbutton.same_screen = True;

	XQueryPointer(e->d, e->r,
			&event.xbutton.root,
			&event.xbutton.window,
			&event.xbutton.x_root,
			&event.xbutton.y_root,
			&event.xbutton.x,
			&event.xbutton.y,
			&event.xbutton.state);

	event.xbutton.subwindow = event.xbutton.window;

	while(event.xbutton.subwindow) {

		event.xbutton.window = event.xbutton.subwindow;

		XQueryPointer(e->d, event.xbutton.window,
				&event.xbutton.root,
				&event.xbutton.subwindow,
				&event.xbutton.x_root,
				&event.xbutton.y_root,
				&event.xbutton.x,
				&event.xbutton.y,
				&event.xbutton.state);
	}

	if(XSendEvent(e->d, PointerWindow, True, 0xfff, &event) == 0)
		fprintf(stderr, "Error event !!!\n");

	XFlush(e->d);

	event.type = ButtonRelease;
	event.xbutton.state = 0x100;

	if(XSendEvent(e->d, PointerWindow, True, 0xfff, &event) == 0)
		fprintf(stderr, "Error event !!!\n");

	XFlush(e->d);

}
