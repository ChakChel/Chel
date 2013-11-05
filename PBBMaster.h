#ifndef PBBMASTER_H
#define PBBMASTER_H

/***************************************************************************//**
 * @file    PBBMaster.h
 * @author  PERROCHAUD Clément
 * @version 0.1
 * @date    2013-11-04
 *
 * Header pour le superviseur du bus CAN
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
    #define MAX_BOOSTS  256

    //! Interval entre chaque salve de requêtes
    #define POLL_PERIOD 500000

    //! Retard maximal de l'acquittement
    #define ACK_TIMEOUT 50000

    //! Retard maximal de l'acquittement
    #define ANS_TIMEOUT 500000

    //! Identifiant unique commun à tous les modules
    #define IDENTIFIANT 0b110

    //! Code d'invite
    #define CODE_INVITE 0x07FF

    //! Taille d'une trame
    #define FRAME_SIZE  sizeof(struct can_frame)

/*** STRUCTURES ***************************************************************/

/*** GLOBALES *****************************************************************/

    //! Tableau des modules
    unsigned char tabModules[MAX_BOOSTS];

#endif
