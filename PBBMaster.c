/***************************************************************************//**
 * @file    PBBMaster.c
 * @author  PERROCHAUD Clément
 * @version 1.0
 * @date    2013-11-04
 *
 * Superviseur du bus CAN
 ******************************************************************************/

#include "PBBMaster.h"

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
struct can_frame mkFrame(unsigned int id,       \
                         unsigned char requ,    \
                         char* data,            \
                         size_t count) {

    struct can_frame frame;
    int i;

    frame.can_id  = ((id & 0x07FF) << 3 |   \
                     (requ & 0x01) << 1);
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
int sendConsigne(int fd, unsigned char nBoost, char consigne) {

    struct can_frame frame;

    frame = mkFrame(((IDENTIFIANT << 8) | nBoost), 0, &consigne, sizeof(char));

    if (write(fd, &frame, FRAME_SIZE) != FRAME_SIZE) {
        perror("Failed to send consigne");
        return -1;
    }

    return 0;
}

/***************************************************************************//**
 * Reçoit un acquittement
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
int getAck(int fd, unsigned char nBoost, useconds_t timeout) {

    struct can_frame frame;
    fd_set set;
    struct timeval delay;
    int rv;

    FD_ZERO(&set);
    FD_SET(fd, &set);

    delay.tv_sec = 0;
    delay.tv_usec = timeout;

    rv = select(fd + 1, &set, NULL, NULL, &delay);

    if(rv == -1) {
        perror("Failed to select ACK");
        return -2;
    } else if(rv == 0) {
        return 0;
    }

    if (read(fd, &frame, FRAME_SIZE) != FRAME_SIZE) {
        perror("Failed to read ACK");
        return -1;
    }

    // Vérification de l'ID de l'expéditeur
    if (((frame.can_id >> 3) & 0x7FF) == nBoost)
        return 1;

    // Chaque trame durant plus de 50ms, inutile d'en attendre une seconde
    return 0;
}

int sendRequ(int fd, unsigned char nBoost) {

    struct can_frame frame;

    frame = mkFrame(((IDENTIFIANT << 8) | nBoost), 1, NULL, 0);

    if (write(fd, &frame, FRAME_SIZE) != FRAME_SIZE) {
        perror("Failed to send request");
        return -1;
    }

    return 0;
}
int getMesures(int fd, unsigned char nBoost, useconds_t timeout) {

    struct can_frame frame;
    fd_set set;
    struct timeval delay;
    int rv;

    FD_ZERO(&set);
    FD_SET(fd, &set);

    delay.tv_sec = 0;
    delay.tv_usec = timeout;

    rv = select(fd + 1, &set, NULL, NULL, &delay);

    if(rv == -1) {
        perror("Failed to select answer");
        return -2;
    } else if(rv == 0) {
        return 0;
    }

    if (read(fd, &frame, FRAME_SIZE) != FRAME_SIZE) {
        perror("Failed to read answer");
        return -1;
    }

    // Vérification de l'ID de l'expéditeur
    if (((frame.can_id >> 3) & 0x7FF) == nBoost && frame.can_dlc == 4) {

        fprintf(stdout,             \
                "%i\t%i\t%i\t%i\t%i\n", \
                nBoost,
                frame.data[0],      \
                frame.data[1],      \
                frame.data[2],      \
                frame.data[3]);

        fflush(stdout);

        return 1;
    }

    // Je suis une feignasse
    return 0;
}
int sendInvite(int fd, unsigned char nBoost) {

    struct can_frame frame;
    char data[2];

    data[0] = IDENTIFIANT;
    data[1] = nBoost;

    frame = mkFrame(CODE_INVITE, 1, data, 2*sizeof(char));

    if (write(fd, &frame, FRAME_SIZE) != FRAME_SIZE) {
        perror("Failed to send invite");
        return -1;
    }

    return 0;
}
void popModule(unsigned char nBoost) {
    tabModules[nBoost] = 0;
}

void addModule(unsigned char nBoost) {
    tabModules[nBoost] = 1;
}

/*** MAIN *********************************************************************/
 
int main(void) {

    int s = 1;
    struct sockaddr_can addr;
    struct ifreq ifr;
    int flags;
    char strConsigne[7];
    int nRead;
    unsigned char nBoost;
    unsigned char invite;

    // Initialisation du tableau des modules
    for (nBoost=0; nBoost<MAX_BOOSTS; nBoost++)
        tabModules[nBoost] = 0;

    // Ouverture du socket
    if((s = socket(PF_CAN, SOCK_RAW, CAN_RAW)) < 0) {
        perror("Error while opening socket");
        return -1;
    }

    // Assignation du socket à l'interface can0
    strcpy(ifr.ifr_name, "can0");
    ioctl(s, SIOCGIFINDEX, &ifr);

    // Configuration du socket
    addr.can_family  = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    // Début de l'écoute
    if(bind(s, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("Error in socket bind");
        return -2;
    }

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

                nBoost = (unsigned char)(atoi(strConsigne) & 0xFF);

                // Envoi de la consigne
                sendConsigne(s,         \
                             nBoost,    \
                             (unsigned char) (atoi(strConsigne+4) & 0xFF));

                // Réception de l'acquittement
                if (getAck(s, nBoost, ACK_TIMEOUT) == 0)
                    popModule(nBoost);
            }
        }

        // Envoi des requêtes
        invite = 0;
        for (nBoost=0; nBoost<MAX_BOOSTS; nBoost++) {
            if (tabModules[nBoost] == 1) {  // Relevé des mesures
                sendRequ(s, nBoost);
                if (getAck(s, nBoost, ACK_TIMEOUT) == 0 ||  \
                    getMesures(s, nBoost, ANS_TIMEOUT) == 0)
                    popModule(nBoost);
            } else if (invite == 0) {       // Invite P&P
                sendInvite(s, nBoost);
                if (getAck(s, nBoost, ACK_TIMEOUT) == 1) {
                    addModule(nBoost);
                    invite = 1;
                }
            }
        }

        // Attente
        usleep(POLL_PERIOD);
    }

    return EXIT_SUCCESS;
}
