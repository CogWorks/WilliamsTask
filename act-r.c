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

pthread_t connect_thread;
pthread_t run_thread;
int sock;
struct sockaddr_in echoServAddr;

typedef struct {
	int port;
	char *host;
} connectInfo_t;

#define BUFSIZE 4096

void connection_send(char *out) {
	int recvMsgSize;
	int recieved = 0;
	int alloced = BUFSIZE;
	char echoBuffer[BUFSIZE];
	char *message = malloc(BUFSIZE*sizeof(char));
	message[0] = '\0';
	send(sock, out, strlen(out), 0);
	do {
		if ((recvMsgSize = recv(sock, echoBuffer, BUFSIZE, 0)) < 0) {
			printf("recv() failed\n");
			goto error;
		}
		recieved += recvMsgSize;
		if (recieved>alloced)
			message = realloc(message, sizeof(message)+BUFSIZE*sizeof(char));
		if (recvMsgSize<BUFSIZE) {
			if (echoBuffer[recvMsgSize-1]=='\n') {
				strncat(message, echoBuffer, recvMsgSize-2);
				printf("%s\n", message);
				free(message);
				return;
			} else {
				strncat(message, echoBuffer, recvMsgSize);
			}
		}
	} while (1);
	error:
	if (message) free(message);

}

void actr_device_handle_keypress(struct json_object *request, struct json_object *response) {
	printf("Key pressed!\n");
	struct json_object *params = json_object_object_get(request, "params");
	if (json_object_array_length(params)>0) {
		struct json_object *args = json_object_array_get_idx(params, 0);
		const char *key = json_object_get_string(json_object_object_get(args, "key"));
		printf("Key %s pressed!\n", key);
		int keycode = XStringToKeysym(key);
		printf("Key %s, keycode %d pressed!\n", key, keycode);
		pressKey(keycode,0);
		json_object_object_add(response, "error", json_object_new_int(0));
		json_object_object_add(response, "result", json_object_new_int(keycode));
		json_object_object_add(response, "prototype", json_object_new_string("json-rpc-response"));
	}
}

void actr_cursor_to_vis_loc(struct json_object *request, struct json_object *response) {
	json_object_object_add(response, "error", json_object_new_int(0));
	json_object_object_add(response, "result", NULL);
}

void actr_build_vis_locs_for(struct json_object *request, struct json_object *response) {
	struct json_object *result = json_object_new_array();
	int i;
	struct json_object *object;
	object = json_object_new_object();
	if (state>=0) {
		json_object_object_add(object,"isa",json_object_new_string("visual-location-ext"));
		json_object_object_add(object,"index",json_object_new_int(-1));
		json_object_object_add(object,"screen-y",json_object_new_int(objects[probe_index].origin.y));
		json_object_object_add(object,"screen-x",json_object_new_int(objects[probe_index].origin.x));
		json_object_object_add(object,"kind",json_object_new_string("probe"));
		json_object_object_add(object,"prototype",json_object_new_string("hashTable"));
		json_object_array_add(result, object);
	}
	if (state>0) {
		for (i=0;i<MAX_OBJECTS;i++) {
			object = json_object_new_object();
			json_object_object_add(object,"isa",json_object_new_string("visual-location-ext"));
			json_object_object_add(object,"index",json_object_new_int(i));
			json_object_object_add(object,"screen-y",json_object_new_int(objects[i].origin.y));
			json_object_object_add(object,"screen-x",json_object_new_int(objects[i].origin.x));
			json_object_object_add(object,"kind",json_object_new_string("shape"));
			json_object_object_add(object,"color",json_object_new_string(w67ColorNames[objects[i].color]));
			json_object_object_add(object,"prototype",json_object_new_string("hashTable"));
			json_object_array_add(result, object);
		}
	}
	json_object_object_add(response, "error", json_object_new_int(0));
	json_object_object_add(response, "result", result);
	json_object_object_add(response, "prototype", json_object_new_string("json-rpc-response"));
}

void actr_vis_loc_to_obj(struct json_object *request, struct json_object *response) {
	struct json_object *params = json_object_object_get(request, "params");
	if (json_object_array_length(params)>0) {
		struct json_object *args = json_object_array_get_idx(params, 0);
		int index = json_object_get_int(json_object_object_get(args, "index"));
		struct json_object *result = json_object_new_object();
		if (index>0) {
			json_object_object_add(result,"isa",json_object_new_string("shape"));
			json_object_object_add(result,"index",json_object_new_int(index));
			json_object_object_add(result,"screen-y",json_object_new_int(objects[index].origin.y));
			json_object_object_add(result,"screen-x",json_object_new_int(objects[index].origin.x));
			json_object_object_add(result,"width",json_object_new_int(objects[index].width));
			json_object_object_add(result,"height",json_object_new_int(objects[index].height));
			json_object_object_add(result,"id",json_object_new_int(objects[index].id));
			json_object_object_add(result,"color",json_object_new_string(w67ColorNames[objects[index].color]));
			json_object_object_add(result,"shape",json_object_new_string(w67ShapeNames[objects[index].shape]));
			json_object_object_add(result,"size",json_object_new_string(w67SizeNames[objects[index].size]));
		} else if (index==-1) {
			json_object_object_add(result,"isa",json_object_new_string("probe"));
			json_object_object_add(result,"index",json_object_new_int(index));
			json_object_object_add(result,"screen-y",json_object_new_int(center_y));
			json_object_object_add(result,"screen-x",json_object_new_int(center_x));
			json_object_object_add(result,"id",json_object_new_int(objects[probe_index].id));
			json_object_object_add(result,"color",json_object_new_string(w67ColorNames[objects[probe_index].color]));
			json_object_object_add(result,"shape",json_object_new_string(w67ShapeNames[objects[probe_index].shape]));
			json_object_object_add(result,"size",json_object_new_string(w67SizeNames[objects[probe_index].size]));
		}
		json_object_object_add(result, "prototype", json_object_new_string("hashTable"));
		json_object_object_add(response, "error", json_object_new_int(0));
		json_object_object_add(response, "result", result);
		json_object_object_add(response, "prototype", json_object_new_string("json-rpc-response"));
	}
}

void *runTrials(void *ptr) {
	int *trials = (int *)ptr;
	doTrials(*trials);
}

void start(struct json_object *request, struct json_object *response) {

	printf("Got start signal!\n");

	struct json_object *params = json_object_object_get(request, "params");
	if (json_object_array_length(params)>0) {
		struct json_object *args = json_object_array_get_idx(params, 0);
		int trials = json_object_get_int(json_object_object_get(args, "trials"));
		w67init();
		printf("Trials: %d\n", trials);
		if (trials<0) trials = 1;
		int ret = pthread_create(&run_thread, NULL, runTrials, &trials);
		json_object_object_add(response, "result", json_object_new_int(ret));
	}

}

void *connection(void *ptr) {

	connectInfo_t *ci = (connectInfo_t *)ptr;

	if ((sock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP)) < 0) {
		printf("socket() failed\n");
		return NULL;
	}

	memset(&echoServAddr, 0, sizeof(echoServAddr));
	echoServAddr.sin_family      = AF_INET;
	echoServAddr.sin_addr.s_addr = inet_addr(ci->host);
	echoServAddr.sin_port        = htons(ci->port);

	printf("Handling server %s %d\n", ci->host, ci->port);

	free(ci->host);
	free(ci);

	if (connect(sock, (struct sockaddr *) &echoServAddr, sizeof(echoServAddr)) < 0) {
		printf("connect() failed\n");
		return NULL;
	}

}

void ipc_connect(struct json_object *request, struct json_object *response) {

	struct json_object *params = json_object_object_get(request, "params");
	if (json_object_array_length(params)>0) {
		struct json_object *args = json_object_array_get_idx(params, 0);
		connectInfo_t *ci = malloc(sizeof(connectInfo_t));
		ci->port = json_object_get_int(json_object_object_get(args, "port"));
		ci->host = strdup(json_object_get_string(json_object_object_get(args, "host")));
		int result = pthread_create(&connect_thread, NULL, connection, (void*)ci);
		json_object_object_add(response, "error", json_object_new_int(0));
		json_object_object_add(response, "result", json_object_new_int(result));
		json_object_object_add(response, "prototype", json_object_new_string("json-rpc-response"));
	}

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
						send(clntSocket, "{\"error\":1,\"result\":\"Malformed json\"}\n", 38, 0);
						printf("Malformed json: %s\n", message);
					} else {
						char *r = (char*)json_object_to_json_string(request);
						struct json_object *method = 0;
						method = json_object_object_get(request, "method");
						if (method==0) {
							send(clntSocket, "{\"error\":2,\"result\":\"No method specified\"}\n", 43, 0);
							printf("No method specified: %s\n", message);
						} else {
							char *reply = jsonrpc_process(r);
							if (strcmp(reply, "{ }")==0) {
								send(clntSocket, "{\"error\":3,\"result\":\"Unknown method\"}\n", 38, 0);
								printf("Unknown method: %s\n", message);
							} else {
								int l = strlen(reply);
								if (send(clntSocket, reply, l, 0) != l)
									printf("send() failed\n");
								if (send(clntSocket, "\n", 1, 0) != 1)
									printf("send() failed\n");
							}
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
//close(clntSocket);


void wait_for_actr_connections(unsigned short port) {

	int servSock;                    /* Socket descriptor for server */
	int clntSock;                    /* Socket descriptor for client */
	struct sockaddr_in echoServAddr; /* Local address */
	struct sockaddr_in echoClntAddr; /* Client address */
	unsigned int clntLen;            /* Length of client address data structure */

	jsonrpc_add_method("actr.cursor-to-vis-loc", actr_cursor_to_vis_loc);
	jsonrpc_add_method("actr.build-vis-locs-for", actr_build_vis_locs_for);
	jsonrpc_add_method("actr.vis-loc-to-obj", actr_vis_loc_to_obj);
	jsonrpc_add_method("actr.device-handle-keypress", actr_device_handle_keypress);
	jsonrpc_add_method("ipc.connect", ipc_connect);
	jsonrpc_add_method("start", start);

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

	while (1) {
		/* Set the size of the in-out parameter */
		clntLen = sizeof(echoClntAddr);

		/* Wait for a client to connect */
		if ((clntSock = accept(servSock, (struct sockaddr *) &echoClntAddr,
				&clntLen)) < 0)
			printf("accept() failed\n");

		/* clntSock is connected to a client! */

		printf("Handling client %s\n", inet_ntoa(echoClntAddr.sin_addr));

		handle_act_r_connection(clntSock);
	}

}
