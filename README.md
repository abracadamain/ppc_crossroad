# ppc_crossroad
## TAF :
* dans lights enlever multiprocessing.value si pas utilisé dans d'autres thread/process et les lock associés DONE V
* lock pour les accès écriture et lecture a shm (pas auto-bloquant). il faut le même lock pour tous -> obligé manager ?
* tests
* rapport
* régler leaks
* coord reçoit pas les véhicules et 'the queue no longer exist' DONE V
* modif traffic_prio_gen accordé sur traffic gen DONEV
* mettre des couleurs sur les prints des lights
* light n'attend pas que prio passe avant de changer de state
* lights process enfant ?
* coordinator ne fait pas passer prio d'abord