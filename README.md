# ppc_crossroad
## TAF :
* dans lights enlever multiprocessing.value si pas utilisé dans d'autres thread/process et les lock associés
* lock pour les accès écriture et lecture a shm (pas auto-bloquant). il faut le même lock pour tous -> obligé manager ?
* finir de modifier la fct gestion_priorite