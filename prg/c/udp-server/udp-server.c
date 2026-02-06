// Server side implementation of UDP client-server model 
#include <stdio.h> 
#include <stdlib.h> 
#include <unistd.h> 
#include <string.h> 
#include <sys/types.h> 
#include <sys/socket.h> 
#include <arpa/inet.h> 
#include <netinet/in.h> 
#include <linux/ip.h>

#define PORT	 8080 
#define MAXLINE 1024 

// Driver code 
int main(int argc, char *argv[])
{
	int c;
	int sockfd; 
	char buffer[MAXLINE]; 
	char *hello = "Hello from server\0"; 
	struct sockaddr_in servaddr, cliaddr; 
	unsigned char  service_type = 0xe0 | IPTOS_LOWDELAY | IPTOS_RELIABILITY;
	int bidirectional = 1;

	while ((c = getopt(argc, argv, "b")) != -1) {
		switch (c) {
			case 'b':
				bidirectional = 1;
				break;
		}
	}

	// Creating socket file descriptor 
	if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) { 
		perror("socket creation failed"); 
		exit(EXIT_FAILURE); 
	} 

	if (setsockopt(sockfd, SOL_IP/*IPPROTO_IP*/, IP_TOS,
		       (void *)&service_type, sizeof(service_type)) < 0)
		perror("setsockopt(IP_TOS) failed:");

	memset(&servaddr, 0, sizeof(servaddr)); 
	memset(&cliaddr, 0, sizeof(cliaddr)); 

	// Filling server information 
	servaddr.sin_family = AF_INET; // IPv4 
	servaddr.sin_addr.s_addr = INADDR_ANY; 
	servaddr.sin_port = htons(PORT); 

	// Bind the socket with the server address 
	if ( bind(sockfd, (const struct sockaddr *)&servaddr, 
			sizeof(servaddr)) < 0 ) 
	{ 
		perror("bind failed"); 
		exit(EXIT_FAILURE); 
	} 

	int len, n; 
	while (1) {
		printf("ready receive\n");
		n = recvfrom(sockfd, (char *)buffer, MAXLINE, 
					MSG_WAITALL, ( struct sockaddr *) &cliaddr, 
					&len); 
		buffer[n] = '\0'; 
		printf("Client : %s\n", buffer); 
		sleep(1);
		if (bidirectional) {
			n = sendto(sockfd, (const char *)hello, strlen(hello) + 1,
				MSG_CONFIRM, (const struct sockaddr *) &cliaddr,
					len);
			printf("Hello message sent: %d\n", n);
		}
	}

	return 0; 
} 
