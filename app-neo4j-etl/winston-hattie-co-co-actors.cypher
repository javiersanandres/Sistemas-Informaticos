// Obtain the actors that haven't worked with "Winston, Hattie"
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

//----------------------------------------------------------------------------------
// Películas en las que trabaja 'Winston, Hattie' sacadas de la base de datos SQL:
// 43044	"Beverly Hills Cop III (1994)"
// 78222	"Clara's Heart (1988)"
// 199231	"Jackie Brown (1997)"
// 233000	"Living Out Loud (1998)"
// 253250	"Meet the Deedles (1998)"
// 341318	"Rugrats Movie, The (1998)"
// 384913	"Sunset Park (1996)"
// 410911	"True Crime (1999)"
//----------------------------------------------------------------------------------
// Películas que más productos han vendido:
// SELECT m.movieid, m.movietitle, m.year, SUM(i.sales) AS total_sales
// FROM imdb_movies m
// JOIN imdb_moviecountries mc ON m.movieid = mc.movieid
// JOIN products p ON m.movieid = p.movieid
// JOIN inventory i ON p.prod_id = i.prod_id
// WHERE mc.country = 'USA'
// GROUP BY m.movieid, m.movietitle, m.year
// ORDER BY total_sales DESC
// LIMIT 20;
//
// 229764	"Life Less Ordinary, A (1997)"	        600
// 291835	"Only You (1994)"	                    577
// 156403	"Glimmer Man, The (1996)"	            568
// 189256	"Illtown (1996)"	                    564
// 425473	"Very Thought of You, The (1945)"	    556
// 49493	"Blob, The (1958)"	                    554
// 189363	"Ilsa, She Wolf of the SS (1975)"	    548
// 20335	"Angel Heart (1987)"	                544
// 201944	"Jerk, The (1979)"	                    544
// 107209	"Doctor Zhivago (1965)"	                544
// 145256	"Friends & Lovers (1999)"	            543
// 171259	"Heavy (1995)"	                        543
// 233000	"Living Out Loud (1998)"	            542     ----> Única en la que actúa 'Winston, Hattie'
// 54396	"Bound for Glory (1976)"	            541
// 293247	"Ordinary People (1980)"	            540
// 381390	"Stranger, The (1994)"	                540
// 323235	"Pyromaniac's Love Story, A (1995)"	    540
// 187575	"I.Q. (1994)"	                        538
// 335444	"Right Stuff, The (1983)"	            538
// 138165	"Fisher King, The (1991)"	            537
//----------------------------------------------------------------------------------
// Películas que más dinero han recaudado:
// SELECT m.movieid, m.movietitle, m.year, SUM(i.sales * p.price) AS total_revenue
// FROM imdb_movies m
// JOIN imdb_moviecountries mc ON m.movieid = mc.movieid
// JOIN products p ON m.movieid = p.movieid
// JOIN inventory i ON p.prod_id = i.prod_id
// WHERE mc.country = 'USA'
// GROUP BY m.movieid, m.movietitle, m.year
// ORDER BY total_revenue DESC
// LIMIT 20;
//
// 229764	"Life Less Ordinary, A (1997)"	                    13911.8
// 171259	"Heavy (1995)"	                                    12815.5
// 293247	"Ordinary People (1980)"	                        12735.7
// 107209	"Doctor Zhivago (1965)"	                            12701.5
// 201944	"Jerk, The (1979)"	                                12619.8
// 335444	"Right Stuff, The (1983)"	                        12513.4
// 149475	"Gang Related (1997)"	                            12397.5
// 197145	"Island of Dr. Moreau, The (1996)"	                12255.0
// 100887	"Desert Winds (1995)"	                            12245.5
// 77792	"City Hall (1996)"	                                12218.9
// 437023	"What Lies Beneath (2000)"	                        12217.0
// 323235	"Pyromaniac's Love Story, A (1995)"	                12204.0
// 202529	"JFK (1991)"	                                    12177.1
// 104320	"Digimon: The Movie (2000)"	                        12131.5
// 398430	"Things to Do in Denver When You're Dead (1995)"	12059.3
// 206249	"Julien Donkey-Boy (1999)"	                        11994.7
// 138165	"Fisher King, The (1991)"	                        11984.4
// 78355	"Class Reunion (1982)"	                            11920.6
// 228636	"Liar Liar (1997)"	                                11863.6
// 280104	"Night Tide (1961)"	                                11848.4
//----------------------------------------------------------------------------------
// Intersección de ambos criterios:
// 229764	"Life Less Ordinary, A (1997)"
// 171259	"Heavy (1995)"
// 293247	"Ordinary People (1980)"
// 107209	"Doctor Zhivago (1965)"
// 201944	"Jerk, The (1979)"
// 335444	"Right Stuff, The (1983)"
// 323235	"Pyromaniac's Love Story, A (1995)"
// 138165	"Fisher King, The (1991)"
//----------------------------------------------------------------------------------
// Actores que han trabajado con 'Winston, Hattie' en la base de datos Neo4j:
// SELECT a.actorid, a.actorname
// FROM imdb_actors a
// JOIN imdb_actormovies am ON a.actorid = am.actorid
// WHERE am.movieid = 233000; -- Movie_id de 'Living Out Loud (1998)'
//
// Da 73 resultados (72 si se excluye a la propia 'Winston, Hattie').
//----------------------------------------------------------------------------------