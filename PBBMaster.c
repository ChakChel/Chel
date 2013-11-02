/***************************************************************************//**
 * @file    PBBMaster.c
 * @author  PERROCHAUD Clément
 * @version 0.2
 * @date    2013-11-02
 *
 * Superviseur du bus CAN
 ******************************************************************************/

/*** INCLUDES *****************************************************************/

    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <string.h>
    #include <fcntl.h>
     
    #include <net/if.h>
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <sys/socket.h>
    #include <sys/ioctl.h>
     
    #include <linux/can.h>
    #include <linux/can/raw.h>

/*** MACROS *******************************************************************/

    //! Nombre maximal de modules boost
    #define MAX_BOOST   256

    //! Interval entre chaque salve de requêtes
    #define POLL_PERIOD 500000

/*** FONCTIONS ****************************************************************/

struct can_frame mkFrame(int nBoost, char requ, char* data, size_t count) {

    struct can_frame frame;
    int i;

    if (count > 8)
        count = 8;

    frame.can_id  = nBoost << 3;
    frame.can_dlc = count;
    for (i=0; i<count; i++)
        frame.data[i] = data[i];

    return frame;
}

int sendConsigne(int fd, int nBoost, char consigne) {

    struct can_frame frame;

    frame = mkFrame(nBoost, 0, &consigne, sizeof(char));

    printf("C%i/%i\n", nBoost, consigne);

    if (write(fd, &frame, sizeof(struct can_frame)) != sizeof(char)) {
        perror("Failed to send consigne");
        return -1;
    }

    

    return 1;
    //## return write(fd, &frame, sizeof(struct can_frame));
}

/*** MAIN *********************************************************************/
 
int main(void) {

    int s = 1;
    struct sockaddr_can addr;
    struct ifreq ifr;
    int flags;
    char strConsigne[7];
    ssize_t nRead;

    //## // Ouverture du socket
    //## if((s = socket(PF_CAN, SOCK_RAW, CAN_RAW)) < 0) {
        //## perror("Error while opening socket");
        //## return -1;
    //## }
//## 
    //## // Assignation du socket à l'interface can0
    //## strcpy(ifr.ifr_name, "can0");
    //## ioctl(s, SIOCGIFINDEX, &ifr);
//## 
    //## // Configuration du socket
    //## addr.can_family  = AF_CAN;
    //## addr.can_ifindex = ifr.ifr_ifindex;
//## 
    //## // Début de l'écoute
    //## if(bind(s, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        //## perror("Error in socket bind");
        //## return -2;
    //## }

    // Configuration de stdin en mode non-bloquant
    flags = fcntl(fileno(stdin), F_GETFL, 0);
    if (flags != -1)
        fcntl(fileno(stdin), F_SETFL, flags | O_NONBLOCK);

    // Boucle principale
    while (1) {

        // Traitement des consignes
        while (1) {

            // Lecture de la consigne éventuelle
            nRead = read(fileno(stdin), strConsigne, 7*sizeof(char));

            if (nRead == 0) {
                break;
            } else if (nRead == 7) {

                strConsigne[3] = '\0';
                strConsigne[6] = '\0';

                // Envoi de la consigne
                sendConsigne(s,                                 \
                             atoi(strConsigne),                 \
                             (char) (atoi(strConsigne+4) & 0xFF));
            }
        }

        //## nbytes = read(s, &frame, sizeof(struct can_frame));

        // Attente
        usleep(POLL_PERIOD);
    }

    return EXIT_SUCCESS;
}
