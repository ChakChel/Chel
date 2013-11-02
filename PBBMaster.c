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

    //! Identifiant unique commun à tous les modules
    #define IDENTIFIANT 0b110

    //! Taille d'une trame
    #define FRAME_SIZE  sizeof(struct can_frame)

/*** FONCTIONS ****************************************************************/

/***************************************************************************//**
 * Formatte une trame CAN.
 *
 * @param nBoost    Le numéro du boost concerné
 * @param requ      1 Pour une trame requête, 0 sinon
 * @param data      Données à envoyer
 * @param count     Taille des données, en octets
 *
 * @return          Trame formée
 ******************************************************************************/
struct can_frame mkFrame(int nBoost, char requ, char* data, size_t count) {

    struct can_frame frame;
    int i;

    frame.can_id  = IDENTIFIANT << 11 | (nBoost & 0xFF) << 3 | requ & 0x01 << 1;
    frame.can_dlc = (count > 8)?8:count;
    for (i=0; i<count; i++)
        frame.data[i] = data[i];

    return frame;
}

/***************************************************************************//**
 * Envoie une consigne
 *
 * @param fd        Le socket d'envoi
 * @param nBoost    Le numéro du boost concerné
 * @param consigne  Consigne à envoyer
 *
 * @return          0 en cas de réussite
 *                  -1 en cas d'erreur à l'envoi
 ******************************************************************************/
int sendConsigne(int fd, int nBoost, char consigne) {

    struct can_frame frame;

    frame = mkFrame(nBoost, 0, &consigne, sizeof(char));

    printf("C%i/%i\n", nBoost, consigne);

    if (write(fd, &frame, FRAME_SIZE) != FRAME_SIZE) {
        perror("Failed to send consigne");
        return -1;
    }

    return 0;
}

/***************************************************************************//**
 * Reçois un acquittement
 *
 * @param fd        Le socket d'envoi
 * @param nBoost    Le numéro du boost concerné
 * @param timeout   Temps maximal d'attente
 *
 * @return          1 en cas de réussite
 *                  0 en cas de timeout
 *                  -1 en cas d'erreur de lecture
 *                  -2 en cas d'erreur de sélection
 ******************************************************************************/
int getAck(int fd, int nBoost, useconds_t timeout) {

    struct can_frame frame;
    fd_set set;
    struct timeval delay;

    FD_ZERO(&set);
    FD_SET(fd, &set);

    timeout.tv_sec = 0;
    timeout.tv_usec = timeout;

    rv = select(fd + 1, &set, NULL, NULL, &timeout);

    if(rv == -1) {
        perror("Failed to select ACK");
        return -2;
    } else if(rv == 0) {
        return 0;
    }

    if (read(s, &frame, FRAME_SIZE) != FRAME_SIZE) {
        perror("Failed to read ACK");
        return -1;
    }

    // if (frame.can_id //TODO
}

/*** MAIN *********************************************************************/
 
int main(void) {

    int s = 1;
    struct sockaddr_can addr;
    struct ifreq ifr;
    int flags;
    char strConsigne[7];
    int nBoost;

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

                nBoost = atoi(strConsigne);

                // Envoi de la consigne
                sendConsigne(s, nBoost, (char) (atoi(strConsigne+4) & 0xFF));

                // Réception de l'acquittement
                if (getAck(s, nBoost, 50000) == 0) {
                    ; //TODO: Retirer module de la liste
                }
            }
        }

        // Attente
        usleep(POLL_PERIOD);
    }

    return EXIT_SUCCESS;
}
