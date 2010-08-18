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

#include <X11/Xlib.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <sys/time.h>
#include <unistd.h>

#include "williams67.h"

void w67DrawTriangle(w67Experiment_t *e, int x, int y, int width) {
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
	XFillPolygon(e->d, e->w, e->gc, points, 4, Convex, CoordModeOrigin);
}

void w67DrawStar(w67Experiment_t *e, int x, int y, int arms, int rOuter, int rInner) {
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
	XFillPolygon(e->d, e->w, e->gc, points, 2*arms+1, Nonconvex, CoordModeOrigin);
}

void w67DrawCross(w67Experiment_t *e, int x, int y, int width) {
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
	XFillPolygon(e->d, e->w, e->gc, points, 13, Nonconvex, CoordModeOrigin);
}

void w67DrawObject(w67Object_t *object) {

	XSetForeground(e->d, e->gc, e->w67Colors[object->color].pixel);

	int cw = (int)e->cell_width * w67Sizes[object->size];

	switch (object->shape) {
	case CROSS:
		w67DrawCross(e, object->origin.x, object->origin.y, cw);
		break;
	case SQUARE:
		XFillRectangle(e->d, e->w, e->gc, object->origin.x-.5*cw, object->origin.y-.5*cw, cw, cw);
		break;
	case CIRCLE:
		XFillArc(e->d, e->w, e->gc, object->origin.x-.5*cw, object->origin.y-.5*cw, cw, cw, 0, 23040);
		break;
	case TRIANGLE:
		w67DrawTriangle(e, object->origin.x, object->origin.y, cw);
		break;
	case SEMICIRCLE:
		XFillArc(e->d, e->w, e->gc, object->origin.x-.5*cw, object->origin.y-.5*cw, cw, cw, 33, 11520);
		break;
	case STAR:
		w67DrawStar(e, object->origin.x,object->origin.y,5, cw/2, cw/3.5);
		break;
	}

	XSetForeground(e->d, e->gc, e->w67Colors[BLACK].pixel);

	char id[2];
	sprintf(id, "%.2d", object->id);
	XDrawString(e->d, e->w, e->gc, object->origin.x, object->origin.y, id, 2);
}

void w67DrawProbe(w67Object_t *object) {
	char id[8];
	sprintf(id, "%.2d", object->id);
	int x = 0.1 * e->cell_width + e->screen_width / 2 - e->cell_width / 2;
	int y = 0.2 * e->cell_width + e->screen_height / 2 - e->cell_width / 2;
	XDrawString(e->d, e->w, e->gc, x, y, w67ShapeNames[object->shape],
			strlen(w67ShapeNames[object->shape]));
	XDrawString(e->d, e->w, e->gc, x, y+9, w67ColorNames[object->color],
			strlen(w67ColorNames[object->color]));
	XDrawString(e->d, e->w, e->gc, x, y+18, w67SizeNames[object->size],
			strlen(w67SizeNames[object->size]));
	XDrawString(e->d, e->w, e->gc, x, y+27, id, 2);
}
