// Buscar todas las relaciones de trabajo entre personas (actores y directores)
MATCH (p1:Person)-[:ACTED_IN|DIRECTED]->(m:Movie)<-[:ACTED_IN|DIRECTED]-(p2:Person)
WITH p1, p2, COUNT(m) AS movies_in_common
WHERE movies_in_common > 1 AND p1 <> p2  // Excluir pares iguales
RETURN p1.name AS person1, p2.name AS person2, movies_in_common
ORDER BY movies_in_common DESC;