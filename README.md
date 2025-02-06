# ppc_crossroad
Simulation d’un carrefour à feux tricolores
## Comment lancer la simulation :
* pré-requis : installer sysv_ipc
* ouvrir 5 terminaux
* se déplacer dans le répertoire ppc_crossroad
* lancer le processus lights avec la commande python3 lights.py 666
* dans l'ordre, dans des terminaux différents, lancer le processus traffic_gen, traffic_prio_gen, coordiantor puis display de la même manière
* la simulation est lancée, vous pouvez l'observer dans display

## Comment arreter la simulation :
* Faire un arret clavier avec Ctr + C pour chaque processus dans l'ordre : display, coordinator, traffic_prio_gen, traffic_gen puis lights