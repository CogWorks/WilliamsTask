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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <arpa/inet.h>
#include <unistd.h>

#include "json/src/json.h"
#include "jsonrpc/include/jsonrpc.h"

#include "williams67.h"

#define BUFSIZE 4096

void ipc_start(struct json_object *request, struct json_object *response) {

	struct json_object *params = json_object_object_get(request, "params");
	if (json_object_array_length(params)>0) {
		struct json_object *args = json_object_array_get_idx(params, 0);
		int trials = json_object_get_int(json_object_object_get(args, "trials"));
		if (trials<0) trials = 1;
		doTrials(trials);
		json_object_object_add(response, "result", json_object_new_int(trials));
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
						//printf("Malformed json: %s\n", message);
					} else {
						char *r = (char*)json_object_to_json_string(request);
						struct json_object *method = 0;
						method = json_object_object_get(request, "method");
						if (method==0) {
							send(clntSocket, "{\"error\":2,\"result\":\"No method specified\"}\n", 43, 0);
						} else {
							char *reply = jsonrpc_process(r);
							if (strcmp(reply, "{ }")==0) {
								send(clntSocket, "{\"error\":3,\"result\":\"Unknown method\"}\n", 38, 0);
							} else {
								int l = strlen(reply);
								if (send(clntSocket, reply, l, 0) != l)
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

	jsonrpc_add_method("start", ipc_start);

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
