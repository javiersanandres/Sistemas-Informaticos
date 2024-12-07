MATCH p = shortestPath((d:Director {name: "Reiner, Carl"})-[:ACTED_IN|DIRECTED*]-(a:Actor {name: "Smyth, Lisa (I)"}))
RETURN p;