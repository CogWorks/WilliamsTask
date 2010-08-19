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

#ifndef W67TYPES_H_
#define W67TYPES_H_

#include <X11/Xlib.h>

#define W67_MAX_COLORS	7
#define W67_MAX_SHAPES	6
#define W67_MAX_SIZES	4

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
	LARGE
} w67Size_t;

typedef struct {
	int			id;
	w67Color_t	color;
	w67Shape_t	shape;
	w67Size_t	size;
	XPoint		origin;
	XPoint		cell;
	int			width;
	int			height;
} w67Object_t;

typedef struct {
	Display *d;
	Window w;
	Window r;
	GC gc;
	int s;
	Cursor cursor;
	unsigned int screen_width;
	unsigned int screen_height;
	int x;
	int y;
	int center_x;
	int center_y;
	int hcw;
	int cell_width;
	int cell_gap;
	int res_diff;
	XColor w67Colors[7];
	Font font;
} w67Experiment_t;

typedef struct {
	int port;
	char *address;
} addy_t;

extern const char *w67ShapeNames[W67_MAX_SHAPES];
extern const char *w67ColorNames[W67_MAX_COLORS];
extern const char *w67SizeNames[W67_MAX_SIZES];
extern const float w67Sizes[W67_MAX_SIZES];

int random_int(int upper_bound);
void hideMouse();
void unhideMouse();
void moveMouse(int x, int y);
void pressKey(int keycode, int modifiers);
void getMouse(XPoint *mouse);

void connection_send(char *message);

void w67init();
void doTrials(int trials);

void w67DrawProbe(w67Object_t *object);
void w67DrawObject(w67Object_t *object);

void wait_for_actr_connections(unsigned short port);

#define ROWS_AND_COLS	13
#define MAX_OBJECTS		100
#define GAP 0.02

w67Experiment_t *e;
int port;
int state;

w67Object_t objects[MAX_OBJECTS];
int probe_index;
int center_x;
int center_y;

#endif /* W67TYPES_H_ */
