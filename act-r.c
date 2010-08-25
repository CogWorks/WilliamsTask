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

#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <pthread.h>

#include "json/src/json.h"
#include "jsonrpc/include/jsonrpc.h"

#include "williams67.h"

#define BUFSIZE 4096

int servSock;
int clntSock;
pthread_t run_thread;
pthread_t mouse_thread;

void connection_send(const char *out) {
	send(clntSock, out, strlen(out), 0);
	send(clntSock, "\n", 1, 0);
}

void actr_device_press_key(struct json_object *request, struct json_object *response) {
	//printf("Key pressed!\n");
	int keycode = json_object_get_int(json_object_object_get(request, "params"));
	//printf("Key %d pressed!\n", keycode);
	pressKey(keycode,0);
}

void actr_device_click_mouse(struct json_object *request, struct json_object *response) {
	//printf("Mouse clicked!\n");
	struct json_object *params = json_object_object_get(request, "params");
	clickMouse(0);
}

void actr_device_move_cursor_to(struct json_object *request, struct json_object *response) {
	struct json_object *params = json_object_object_get(request, "params");
	if (json_object_array_length(params)>0) {
		int x = json_object_get_int(json_object_array_get_idx(params, 0));
		int y = json_object_get_int(json_object_array_get_idx(params, 1));
		//printf("Move mouse to x:%d,y:%d\n", x, y);
		moveMouse(x, y);
	}
}

void send_display_objects() {

	//printf("Send display objects!\n");

	struct json_object *message = json_object_new_object();
	struct json_object *params = json_object_new_object();
	struct json_object *vis_locs = json_object_new_array();
	struct json_object *vis_objs = json_object_new_array();

	int i;
	char *chunk = 0;

	if (state>=0) {
		asprintf(&chunk,
				"(isa visual-location screen-x %d screen-y %d kind probe)",
				objects[probe_index].origin.x,
				objects[probe_index].origin.y);
		json_object_array_add(vis_locs, json_object_new_string(chunk));
		free(chunk);
		asprintf(&chunk,
				"(isa probe color %s shape %s size %s id %d)",
				w67ColorNames[objects[probe_index].color],
				w67ShapeNames[objects[probe_index].shape],
				w67SizeNames[objects[probe_index].size],
				objects[probe_index].id);
		json_object_array_add(vis_objs, json_object_new_string(chunk));
		free(chunk);
	}

	if (state>0) {
			for (i=0;i<MAX_OBJECTS;i++) {
				asprintf(&chunk,
						"(isa visual-location screen-x %d screen-y %d color %s kind shape)",
						objects[i].origin.y,
						objects[i].origin.x,
						w67ColorNames[objects[i].color]);
				json_object_array_add(vis_locs, json_object_new_string(chunk));
				free(chunk);
				asprintf(&chunk,
						"(isa shape color %s shape %s size %s id %d width %d height %d)",
						w67ColorNames[objects[i].color],
						w67ShapeNames[objects[i].shape],
						w67SizeNames[objects[i].size],
						objects[i].id,
						objects[i].width,
						objects[i].height);
				json_object_array_add(vis_objs, json_object_new_string(chunk));
				free(chunk);
			}
	}
	json_object_object_add(message, "method", json_object_new_string("update-display"));
	json_object_object_add(params, "vis-locs", vis_locs);
	json_object_object_add(params, "vis-objs", vis_objs);
	json_object_object_add(params, "prototype", json_object_new_string("display-objects"));
	json_object_object_add(message, "params", params);
	json_object_object_add(message, "prototype", json_object_new_string("json-rpc-notification"));
	connection_send(json_object_to_json_string(message));
	//printf("Display objects sent!\n");
}

void *runTrials(void *ptr) {
	int trials = (int)ptr;
	//printf("Trials: %d\n", trials);
	doTrials(trials);
}

/*
void *update_mouse(void *ptr) {
	int us = (int)ptr * 1000;
	int x = 0;
	int y = 0;
	char *msg = 0;
	while (clntSock) {
		if (x!=cursor_x || y!=cursor_y) {
			asprintf(&msg, "{\"method\":\"set-mouse-pos\",\"params\":[%d,%d],\"prototype\":\"json-rpc-notification\"}",cursor_x,cursor_y);
			printf("%s\n", msg);
			connection_send(msg);
			free(msg);
			x = cursor_x;
			y = cursor_y;
		}
		usleep(us);
	}
}
*/

void actr_device_run(struct json_object *request, struct json_object *response) {

	//printf("Got start signal!\n");

	struct json_object *params = json_object_object_get(request, "params");
	int trials = json_object_get_int(params);
	w67init();
	//pthread_create(&mouse_thread, NULL, update_mouse, (void*)10);
	if (trials<0) trials = 1;
	int ret = pthread_create(&run_thread, NULL, runTrials, (void*)trials);

}

void handle_act_r_connection(int clntSocket) {

	while (1) {

		char echoBuffer[BUFSIZE];
		int recvMsgSize;
		int recieved = 0;
		int alloced = BUFSIZE;
		char *message = malloc(BUFSIZE*sizeof(char));
		message[0] = '\0';

		do {
			if ((recvMsgSize = recv(clntSocket, echoBuffer, BUFSIZE, 0)) < 0) {
				printf("recv() failed\n");
				goto error;
			}
			recieved += recvMsgSize;
			if (recieved>alloced)
				message = realloc(message, sizeof(message)+BUFSIZE*sizeof(char));
			if (recvMsgSize<BUFSIZE) {
				if (echoBuffer[recvMsgSize-1]=='\n') {
					strncat(message, echoBuffer, recvMsgSize-2);
					struct json_object *request = json_tokener_parse(message);
					if (is_error(request)) {
						printf("Malformed json: %s\n", message);
					} else {
						char *r = (char*)json_object_to_json_string(request);
						struct json_object *method = 0;
						method = json_object_object_get(request, "method");
						if (method==0) {
							printf("No method specified: %s\n", message);
						} else {
							jsonrpc_process(r);
						}
					}
					free(message);
					message = malloc(BUFSIZE*sizeof(char));
					message[0] = '\0';
					alloced = BUFSIZE;
					recieved = 0;
				} else {
					strncat(message, echoBuffer, recvMsgSize);
				}
			}
		} while (1);
		error:
		if (message) free(message);
	}
}

void wait_for_actr_connections(unsigned short port) {

	struct sockaddr_in echoServAddr; /* Local address */
	struct sockaddr_in echoClntAddr; /* Client address */
	unsigned int clntLen;            /* Length of client address data structure */

	jsonrpc_add_method("run", actr_device_run);
	jsonrpc_add_method("move-cursor-to", actr_device_move_cursor_to);
	jsonrpc_add_method("click-mouse", actr_device_click_mouse);
	jsonrpc_add_method("press-key", actr_device_press_key);

	/* Create socket for incoming connections */
	if ((servSock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP)) < 0) {
		printf("socket() failed\n");
		return;
	}

	/* Construct local address structure */
	memset(&echoServAddr, 0, sizeof(echoServAddr));   /* Zero out structure */
	echoServAddr.sin_family = AF_INET;                /* Internet address family */
	echoServAddr.sin_addr.s_addr = htonl(INADDR_ANY); /* Any incoming interface */
	echoServAddr.sin_port = htons(port);      		   /* Local port */

	/* Bind to the local address */
	if (bind(servSock, (struct sockaddr *) &echoServAddr, sizeof(echoServAddr)) < 0) {
		printf("bind() failed\n");
		return;
	}
	/* Mark the socket so it will listen for incoming connections */
	if (listen(servSock, 1) < 0)
		printf("listen() failed\n");

	//while (1) {
	/* Set the size of the in-out parameter */
	clntLen = sizeof(echoClntAddr);

	/* Wait for a client to connect */
	if ((clntSock = accept(servSock, (struct sockaddr *) &echoClntAddr,
			&clntLen)) < 0)
		printf("accept() failed\n");

	/* clntSock is connected to a client! */

	printf("Handling client %s\n", inet_ntoa(echoClntAddr.sin_addr));

	handle_act_r_connection(clntSock);
	//}

}
