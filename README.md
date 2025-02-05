# ppc_crossroad
## TAF :
* dans lights enlever multiprocessing.value si pas utilisé dans d'autres thread/process et les lock associés
* lock pour les accès écriture et lecture a shm (pas auto-bloquant). il faut le même lock pour tous -> obligé manager ?
* tests
* rapport
* régler leaks
* coord reçoit pas les véhicules et 'the queue no longer exist'
* modif traffic_prio_gen accordé sur traffic gen
* mettre des couleurs sur les prints des lights