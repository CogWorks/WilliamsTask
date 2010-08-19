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

void hideMouse() {
	XDefineCursor(e->d, e->w, e->cursor);
}

void unhideMouse() {
	XUndefineCursor(e->d, e->w);
}

void moveMouse(int x, int y) {
	XWarpPointer(e->d, None, e->w, 0,0,0,0, e->screen_width/2, e->screen_height/2);
}

void getMouse(XPoint *mouse) {
	if (e && e->d && e->r) {
		XEvent event;
		memset(&event, 0x00, sizeof(event));
		Window inwin;
		Window inchildwin;
		XQueryPointer(e->d, e->r,
				&event.xbutton.root,
				&event.xbutton.window,
				&event.xbutton.x_root,
				&event.xbutton.y_root,
				&event.xbutton.x,
				&event.xbutton.y,
				&event.xbutton.state);
		mouse->x = event.xbutton.x;
		mouse->y = event.xbutton.y;
		XSync(e->d, False);
	} else {
		mouse->x = 0;
		mouse->y = 0;
	}
}

void clickMouse(int button) {

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

void pressKey(int keycode, int modifiers) {

	//XLockDisplay(e->d);
	printf("Executing keypress 1\n");

	XKeyEvent event;
	event.display = e->d;
	event.window = e->w;
	event.root = e->r;
	event.subwindow = None;
	event.time = CurrentTime;
	event.x = 1;
	event.y = 1;
	event.x_root = 1;
	event.y_root = 1;
	event.same_screen = True;
	event.keycode = keycode;
	event.state = modifiers;

	printf("Executing keypress 2\n");

	event.type = KeyPress;

	printf("Executing keypress 3\n");

	if(XSendEvent(event.display, event.window, True, KeyPressMask, (XEvent *)&event) == 0)
		fprintf(stderr, "Error event !!!\n");
	XFlush(e->d);
	//XSync(e->d, True);

	event.type = KeyRelease;

	printf("Executing keypress 4\n");

	if(XSendEvent(event.display, event.window, True, KeyReleaseMask, (XEvent *)&event) == 0)
		fprintf(stderr, "Error event !!!\n");
	XFlush(e->d);
	//XSync(e->d, True);

	printf("Executing keypress 5\n");
	//XUnlockDisplay(e->d);

}
