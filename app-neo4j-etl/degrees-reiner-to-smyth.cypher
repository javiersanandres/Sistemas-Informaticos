// Buscar el camino más corto desde "Reiner, Carl" hasta "Smyth, Lisa (I)"
MATCH p = shortestPath((d:Director {name: "Reiner, Carl"})-[:ACTED_IN|DIRECTED*]-(a:Actor {name: "Smyth, Lisa (I)"}))
RETURN p;