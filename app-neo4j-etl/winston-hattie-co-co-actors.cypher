// Obtain the actors that have worked with "Winston, Hattie"
MATCH (h:Actor {name: 'Winston, Hattie'})-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(other:Actor)
WITH COLLECT(other) AS worked_with_winston

// Obtain those who didn't work with "Winston, Hattie"
MATCH (a:Actor)
WHERE NOT a.name = "Winston, Hattie" AND NOT a IN worked_with_winston
WITH COLLECT(a) AS didnt_work_with_winston, worked_with_winston

// Finally, obtain the actors that haven't worked with "Winston, Hattie", but have
// worked with some third actor in common.
MATCH (a:Actor)-[:ACTED_IN]->(n:Movie)<-[:ACTED_IN]-(third:Actor)
WHERE a IN didnt_work_with_winston AND third IN worked_with_winston
RETURN a;