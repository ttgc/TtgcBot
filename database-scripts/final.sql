-- Fixit old scripts
INSERT INTO Extensions (universe, world) VALUES ('Cosmorigins', 'Xyord');

DO $$
<<fixit>>
DECLARE
    xyord Extensions.id_extension%TYPE;
	idr Race.id_race%TYPE;
	ido Organizations.id_org%TYPE;
	sk RECORD;
BEGIN
    SELECT id_extension INTO xyord FROM Extensions WHERE universe = 'Cosmorigins' AND world = 'Xyord';
	-- Race
	INSERT INTO Race (nom, id_extension) VALUES ('Xyordien', xyord);
	RAISE NOTICE 'Inserts in Race completed';
	-- Class
	SELECT id_race INTO idr FROM Race WHERE nom = 'Xyordien' AND id_extension = xyord;
	INSERT INTO Classe (id_race, nom) VALUES (idr, 'Backliner'), (idr, 'Invader'), (idr, 'Commander'), (idr, 'Pacifier'), (idr, 'Administrator');
	RAISE NOTICE 'Inserts in Classe completed';
	-- Organizations
	INSERT INTO Organizations(nom, id_extension, hidden) VALUES
	('Seigneur', xyord, false), ('Legionnaire', xyord, false), ('Esclave', xyord, false);
	RAISE NOTICE 'Inserts in Organizations completed';
	RAISE NOTICE 'Skipping xyord skills';
END fixit $$;

-- ADTAF
INSERT INTO Extensions (universe, world) VALUES ('Abyssal Dive', 'The Ancient Fortress');

-- Add new race, class, symbionts, organizations, and skills (v6)
DO $$
<<v6update>>
DECLARE
	terae Extensions.id_extension%TYPE;
	orianis Extensions.id_extension%TYPE;
    xyord Extensions.id_extension%TYPE;
    adtaf Extensions.id_extension%TYPE;
	idr Race.id_race%TYPE;
	ido Organizations.id_org%TYPE;
	ids Symbiont.id_symbiont%TYPE;
	sk RECORD;
BEGIN
	SELECT id_extension INTO terae FROM Extensions WHERE universe = 'Cosmorigins' AND world = 'Terae';
	SELECT id_extension INTO orianis FROM Extensions WHERE universe = 'Cosmorigins' AND world = 'Orianis';
    SELECT id_extension INTO xyord FROM Extensions WHERE universe = 'Cosmorigins' AND world = 'Xyord';
    SELECT id_extension INTO adtaf FROM Extensions WHERE universe = 'Abyssal Dive' AND world = 'The Ancient Fortress';
	-- Race
	INSERT INTO Race (nom, id_extension) VALUES ('Humain', adtaf), ('Descendant des anciens', adtaf);
	RAISE NOTICE 'Inserts in Race completed';
	-- Class
	SELECT id_race INTO idr FROM Race WHERE nom = 'Humain' AND id_extension = adtaf;
	INSERT INTO Classe (id_race, nom) VALUES (idr, 'Standard'), (idr, 'Detenteur de mana');
	SELECT id_race INTO idr FROM Race WHERE nom = 'Descendant des anciens' AND id_extension = adtaf;
	INSERT INTO Classe (id_race, nom) VALUES (idr, 'Descendant des anciens');
	RAISE NOTICE 'Inserts in Classe completed';
	-- Symbionts
	INSERT INTO Symbiont (nom, id_extension) VALUES
    ('Horya', orianis), ('Manahil', orianis), ('Shuuchuu', orianis), ('Physiocura', orianis), ('Shurodingeru', orianis),
    ('Omega-1', orianis), ('Omega-2', orianis), ('Omega-3', orianis), ('Omega-4', orianis), ('Omega-5', orianis),
    ('Omega-6', orianis), ('Omega-7', orianis), ('Omega-8', orianis), ('Omega-9', orianis), ('Omega-10', orianis),
    ('Omega-11', orianis), ('Omega-12', orianis), ('Omega-13', orianis), ('Furya', xyord), ('Ignos', xyord);
	RAISE NOTICE 'Inserts in Symbionts completed';
	-- Organizations
	INSERT INTO Organizations(nom, id_extension, hidden) VALUES
	('Marchand', adtaf, false), ('Eclaireur', adtaf, false), ('Chasseur', adtaf, false), ('Informateur', adtaf, false),
    ('Medecin', adtaf, false), ('Cuistot', adtaf, false), ('Mercenaire', adtaf, false), ('Mecanicien', adtaf, false),
    ('Alchimiste', adtaf, false), ('Pretre Elyon', adtaf, false), ('Artificier', adtaf, false),
    ('Politicien', adtaf, false), ('Archimage', adtaf, false), ('Apotre Elyon', adtaf, false);
	RAISE NOTICE 'Inserts in Organizations completed';
	INSERT INTO Skills(nom, description, origine, webclass, id_extension) VALUES
	('Presence', 'Octroie la possibilite de faire usage de l''aura a son hote mais retire egalement toute possibilite de cumuler et d''user de points d''anti-aura', 'Horya', 'symbiont horya', orianis),
	('Combat deterministe', 'Au debut d''un combat, l''hote peut realiser un jet d''intimidation (charisme), en fonction du resultat il se voit octroyer plus ou moins de points d''auras utilisables uniquement sur ce combat', 'Horya', 'symbiont horya', orianis),
	('Ambivalence energetique', 'Permet d''utiliser ses PV pour payer un coût en PM. Le coût est alors multiplie par 1,25', 'Manahil', 'symbiont manahil', orianis),
	('Barriere de mana', 'Permet de generer une barriere de mana pour encaisser n''importe quel type de degâts avec un coût en PM equivalent au degâts initiaux multiplie par 1,25 (max : 300 PM / tour)', 'Manahil', 'symbiont manahil', orianis),
	('Perte seche', 'Si l''hote tombe en dessous de 100 PM restants, il perdra 50 PV / tour tant qu''il ne remontera pas au dessus de 100 PM', 'Manahil', 'symbPerte secheiont manahil', orianis),
	('Combo agressif', 'Pour chaque action offensive reussie, la marge de reussite critique augmente de 1 jusqu''a un maximum de 10 (non cumulable). En cas d''echec sur une action offensive ou si aucune action offensive n''est entreprise pendant deux tours ou plus, ce bonus est reinitialise', 'Shuuchuu', 'symbiont shuuchuu', orianis),
	('Concentration', 'Permet une fois par combat de passer en posture de focalisation pour une duree maximale de 5 tours', 'Shuuchuu', 'symbiont shuuchuu', orianis),
	('Gratuite energetique', 'En posture de focalisation, une fois par tour, le personnage peut lancer une action consommant jusqu''a 30 PM sans en payer le coût', 'Shuuchuu', 'symbiont shuuchuu', orianis),
	('Meditation', 'En posture de focalisation, permet de passer son action pour mediter recuperant 30+1d20 PM et retirant toutes les alterations d''etats negatives', 'Shuuchuu', 'symbiont shuuchuu', orianis),
	('Succes focalise', 'les gains de "Combo agressif" sont doubles en posture de focalisation', 'Shuuchuu', 'symbiont shuuchuu', orianis),
	('Immunite acquise', 'Immunise a toutes les alterations d''etats (hors mort), maledictions et maladies', 'Physiocura', 'symbiont physiocura', orianis),
	('Soumission eternelle', 'L''hote meurt automatiquement si on tente de lui extraire son symbiote ou si celui-ci est detruit', 'Physiocura', 'symbiont physiocura', orianis),
	('Guerison acceleree', 'Recupere 25 PV / tour automatiquement', 'Physiocura', 'symbiont physiocura', orianis),
	('Renforcement', 'Gagne automatiquement 5 points de force par niveau jusqu''au niveau 5 inclus soit un total de 25 points supplementaires aux niveaux 5 ou superieurs. Le gain de force ne permet en aucun cas de depasser le maximum en force du personnage pour son niveau actuel', 'Physiocura', 'symbiont physiocura', orianis),
	('Dans les dents', 'Multiplie les degâts physiques infliges par 1,5. Ne fonctionne que sur les attaques au corps a corps necessitant un jet de force', 'Physiocura', 'symbiont physiocura', orianis),
	('Intrication', 'Les talents du symbiote sont transferes a l''hote', 'Shurodingeru', 'symbiont shurodingeru', orianis),
	('Revitalisation', 'Les PV de l''hote sont quintuples, si l''hote tombe en dessous de 0 PV, il regenere 20% de ses PV max chaque tour pendant 5 tours, cette regeneration speciale doit ensuite se recharger 5 tours de plus', 'Omega-1', 'symbiont omega omega-1', orianis),
	('Monstruosite', 'Decuple toutes les statistiques, empechant ainsi tout echec simple, seul les echecs critiques et super-critiques sont possible. De plus la marge d''echec critique est reduite de 5 tandis que celle des reussites critiques est augmentee de 5', 'Omega-1', 'symbiont omega omega-1', orianis),
	('Omae wa', 'Tous les degâts infliges sont multiplies par 10', 'Omega-1', 'symbiont omega omega-1', orianis),
	('Transformiste', 'Permet d''alterer son apparence a volonte', 'Omega-1', 'symbiont omega omega-1', orianis),
	('Immunite en scenarium', 'Octroie une immunite totale a toutes les alterations d''etat, a la douleur et aux saignements. Tout membre perdu se regenere pratiquement instantanement y compris le cerveau. Le seul moyen de tuer definitivement l''hote est de detruire completement son corps sans laisser le moindre reste', 'Omega-1', 'symbiont omega omega-1', orianis),
	('Depossession', 'Permet de beneficier temporairement des talents d''une cible etant passee dans le champs de vision de l''hote, et de derober temporairement ces derniers en cas de contact direct avec la cible', 'Omega-2', 'symbiont omega omega-2', orianis),
	('Contre-mesure', 'Lorsqu''il subit une attaque, obtient une resistance de 100% contre ce type d''attaque pendant toute la duree du combat', 'Omega-2', 'symbiont omega omega-2', orianis),
	('Motricite', 'Triple la mobilite et octroie +20% en esquive', 'Omega-2', 'symbiont omega omega-2', orianis),
	('Anticipation', 'Permet d''anticiper les mouvements d''un adversaire au prochain tour', 'Omega-2', 'symbiont omega omega-2', orianis),
	('Energisant', 'Permet d''absorber l''energie environnante pour regenerer ses PM ou la relancer sous formes d''eclairs electriques. L''hote est egalement immunise a l''electricite', 'Omega-2', 'symbiont omega omega-2', orianis),
	('Surtension', 'Les regenerations de PM qui font depasser le maximum sont utilises pour generer des arcs electriques defensif autour du corps de l''hote', 'Omega-2', 'symbiont omega omega-2', orianis),
	('Transport eclair', 'Permet de se transformer en electricite et de se deplacer a la vitesse de la foudre instantanement a n''importe quel emplacement dans le champs de vision de l''hote. Se deplacer ainsi inflige des degâts aux autres cibles proche de la zone d''impact', 'Omega-3', 'symbiont omega omega-3', orianis),
	('Induction', 'Permet de ressentir et d''alterer tous les champs electromagnetique a proximite. De plus, l''hote est insensible a l''electricite qui lui restaure meme des PV et des PM (coefficient de -1)', 'Omega-3', 'symbiont omega omega-3', orianis),
	('Duelliste', '+10% pour attaquer une cible lors d''un duel', 'Omega-3', 'symbiont omega omega-3', orianis),
	('Electricite statique', 'Permet d''entourer son corps d''arcs electriques a volonte, infligeant des degâts aux cibles trop proche et electrisant toute arme utilisee', 'Omega-3', 'symbiont omega omega-3', orianis),
	('Liquefaction', 'Permet de se deplacer a la surface de n''importe quelle matiere comme s''il s''agissait d''un liquide. Lorsque ce talent est utilisee, l''hote et le symbiote se fondent parfaitement dans la matiere traversee et ne sont pas visible', 'Omega-4', 'symbiont omega omega-4', orianis),
	('Hydrolyse', 'Permet d''adopter les memes proprietes physiques que l''eau, y compris son etat physique (solide, liquide, gazeux, supercritique) en fonction de la pression et temperature ambiante', 'Omega-4', 'symbiont omega omega-4', orianis),
	('Absorption', 'L''hote peut devorer une cible vulnerable, la dissolvant totalement. Une fois dissoute l''hote acquiert tous les talents de sa cible et peut egalement acquerir certaines capacites et statistiques de celle-ci qui viennent alors remplacer les capacites ou statistiques equivalentes de l''hote', 'Omega-4', 'symbiont omega omega-4', orianis),
	('Immuable Montagne', 'L''hote voit sa peau etre recouverte de granite. Octroie une reduction de 100% contre les degâts physiques', 'Omega-5', 'symbiont omega omega-5', orianis),
	('Taille-mont', 'Chaque attaque physique tranchante ou perçante subit, reduit "Immuable Montagne" de 10% (certaines attaques ou type de degât peuvent retirer davantage). Si l''hote ne subit aucune attaque physique tranchante ou perçante pendant 3 tours, la protection est restauree entierement', 'Omega-5', 'symbiont omega omega-5', orianis),
	('Monts et merveilles', 'Octroie +20% en force, reduit la marge d''echec critique de 5% et augmente celles des reussites critiques de 5% (non cumulable). Les degâts physiques infliges augmentent egalement mais diminue chaque fois que "Immuable Montagne" diminue', 'Omega-5', 'symbiont omega omega-5', orianis),
	('Forge des geants', 'Permet de generer n''importe quelle arme en granite sans coût ni jet et sans consommer d''action', 'Omega-5', 'symbiont omega omega-5', orianis),
	('Corruption', 'Toutes les cibles qui entrent en contact avec l''hote ou qui subissent une attaque de l''hote ont une chance d''etre contamine par le pathogene du symbiote. Les victimes doivent reussir un jet de chance avec un bonus/malus plus ou moins important', 'Omega-6', 'symbiont omega omega-6', orianis),
	('Porteur sain', 'Octroie l''immunite totale contre la pathogene du symbiote', 'Omega-6', 'symbiont omega omega-6', orianis),
	('Reconstitution', 'Permet de reconstituer n''importe quel membre ou partie du corps perdue au bout d''un certains temps qui depend de la taille du morceau a regenerer', 'Omega-7', 'symbiont omega omega-7', orianis),
	('Receveur universel', 'Permet d''absorber le sang de n''importe quel cible en mettant en contact une plaie de celle-ci avec une autre de l''hote. Le transfere sanguin vide alors les PV de la cible pour les restaurer a l''hote avec un ratio de 1', 'Omega-7', 'symbiont omega omega-7', orianis),
	('Immunite naturelle', 'Immunise l''hote contre toutes les maladies sauf celle engendrees par des symbiotes omega superieurs', 'Omega-7', 'symbiont omega omega-7', orianis),
	('Alizees', 'Vitesse de deplacement doublee en tout temps', 'Omega-8', 'symbiont omega omega-8', orianis),
	('Immunite climatique', 'Est immunise aux variations de temperatures et de pressions ainsi qu''aux radiations mortelles', 'Omega-8', 'symbiont omega omega-8', orianis),
	('Envole-moi', 'Permet de voler sans aucune limite d''altitude', 'Omega-8', 'symbiont omega omega-8', orianis),
	('Decompression explosive', 'Les PM peuvent depasser les PM max jusqu''a 100 PM au dessus de la limite, lorsque les PM atteignent cette nouvelle limite, le surplus de PM est libere sous forme d''une onde de choc liee a une decompression explosive autour de l''hote', 'Omega-8', 'symbiont omega omega-8', orianis),
	('L''air de rien', 'Permet de manipuler l''air aux alentours a volonte sans coût ni jet', 'Omega-8', 'symbiont omega omega-8', orianis),
	('Pensee acceleree', 'Altere la perception du temps, donnant l''impression que tout se deroule au ralenti et permettant ainsi de reflechir 10 fois plus vite que la normale', 'Omega-9', 'symbiont omega omega-9', orianis),
	('Retroaction', 'En se concentrant et en meditant suffisamment longtemps, permet de remonter le temps jusqu''a 24h en arriere', 'Omega-9', 'symbiont omega omega-9', orianis),
	('Devoreur de temps', 'Chaque cible tuee augmente l''esperance de vie d''autant que celle qui restait a la cible au moment de sa mort', 'Omega-9', 'symbiont omega omega-9', orianis),
	('Protection immunitaire', 'Immunise contre le vieillissement, toutes les maladies ainsi que tous les poisons et toutes les toxines', 'Omega-9', 'symbiont omega omega-9', orianis),
	('Ascendant mental', 'Permet de posseder et d''utiliser des points d''aura. L''hote possede par defaut 2 points d''aura, et en regenere un chaque fois qu''il parvient a controler mentalement une cible. Si l''hote controle au moins une personne mentalement, il regenere egalement un point d''aura tous les 3 tours', 'Omega-10', 'symbiont omega omega-10', orianis),
	('Subduction', 'Permet de prendre le controle, contre un jet passif d''esprit, de n''importe quel entite sensible au controle mental a proximite', 'Omega-10', 'symbiont omega omega-10', orianis),
	('Reactivite accrue', '+25% en esquive (remplace tous les bonus en esquive precedents)', 'Omega-11', 'symbiont omega omega-11', orianis),
	('Hyper-vitesse', 'Octroie 2 actions par tour (non cumulable sauf avec "Nitro")', 'Omega-11', 'symbiont omega omega-11', orianis),
	('Nitro', 'Permet d''obtenir une 3e action contre 25 PM / tour jusqu''a 3 tours consecutifs. Une fois le boost termine, l''hote perd une action chaque tour pendant autant de temps que la duree du boost initiale', 'Omega-11', 'symbiont omega omega-11', orianis),
	('Rapide et furieux', 'Octroie +3 de deplacement bonus en permanence', 'Omega-11', 'symbiont omega omega-11', orianis),
	('Elastic-man', 'Permet de deformer, durcir, ramollir le corps de l''hote a volonte sans coût de mana supplementaire', 'Omega-12', 'symbiont omega omega-12', orianis),
	('Regeneration moleculaire', 'Supprime les saignements et hemorragies de l''hote, et regenere les membres perdus en 1 tour maximum, seul la tete et le cerveau ne peuvent etre regeneres', 'Omega-12', 'symbiont omega omega-12', orianis),
	('Separation', 'Permet de subdiviser l''hote en plusieurs entites ayant chacune leur action et pouvant utiliser les memes aptitudes et competences que l''originale. PV et PM sont repartis equitablement a la division et les entites peuvent etre reabsorbes pour recuperer les PV/PM restants a cette derniere', 'Omega-12', 'symbiont omega omega-12', orianis),
	('Cameleon', 'Permet d''alterer l''apparence pour se fondre dans n''importe quel decor tel un veritable cameleon ', 'Omega-13', 'symbiont omega omega-13', orianis),
	('Memoire volatile', 'Permet d''effacer tout souvenir de l''hote et du symbiote chez n''importe quelle cible proche de l''hote', 'Omega-13', 'symbiont omega omega-13', orianis),
	('Furie', 'Lorsque l''hote tombe a 0 PV ou moins, ceux-ci sont entierement regeneres et passe en posture "Enrage". Dans cet etat l''hote perd alors 50*2x PV au Xe tour ', 'Furya', 'symbiont furya', xyord),
	('Aura furieuse', 'En posture "Enrage", l''hote gagne 1 point d''aura par tour', 'Furya', 'symbiont furya', xyord),
	('Double action', 'En posture "Enrage", l''hote possede deux actions par tour', 'Furya', 'symbiont furya', xyord),
	('Agressivite', 'En posture "Enrage", les degâts infliges par l''hote sont augmentes. L''hote peut egalement parer mais ne peut pas esquiver ou effectuer d''autres actions defensives', 'Furya', 'symbiont furya', xyord),
	('Retour au calme', 'Si tout les ennemis sont vaincus et que l''hote est en posture "Enrage", celle-ci prend alors fin immediatement', 'Furya', 'symbiont furya', xyord),
	('Ignifuge', 'Octroie une immunite totale aux degâts de feu et de chaleur', 'Ignos', 'symbiont ignos', xyord),
	('Chaud bouillant', 'L''hote peut enflamme son corps a volonte sans coût ni jet', 'Ignos', 'symbiont ignos', xyord),
	('Qui s''y frotte s''y brûle', 'Lorsque le corps de l''hote est entierement enflamme, il emet des faibles deflagrations repoussant les entites (1u) a proximite (≤ 2u)', 'Ignos', 'symbiont ignos', xyord),
	('Sensibilite aquatique', 'L''eau et les degâts d''eau subits sont doubles et appliquent un effet similaire aux brûlures sur une cible normale. Si le corps de l''hote est entierement enflamme, les degâts d''eau eteignent le corps completement et l''empeche de s''enflammer a nouveau pendant 3 tours', 'Ignos', 'symbiont ignos', xyord),
	('Faiblesse organique', 'Divise par deux les PM max et les PV max a la creation du personnage', 'Humain', 'adtaf human', adtaf),
	('Irradie', 'Le personnage commence a 10+1d20 points de mutation a sa creation', 'Humain', 'adtaf human', adtaf),
	('Expose', 'Possede un malus naturel cumulable de -10% sur tous les jets de mutation (chance)', 'Humain', 'adtaf human', adtaf),
	('Sans mana fixe', 'Ne possede pas de PM (PM = 0)', 'Humain Standard', 'adtaf human standard', adtaf),
	('Langue de bois', 'Octroie un bonus de +20% pour manipuler des humains (charisme)', 'Descendant des anciens', 'adtaf ancient', adtaf);
	RAISE NOTICE 'Inserts in Skills completed';
	SELECT id_race INTO idr FROM Race WHERE nom = 'Humain' AND id_extension = adtaf;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Humain' ORDER BY id_skill) LOOP
		INSERT INTO RaceSkills VALUES (idr, sk.id_skill);
	END LOOP;
	SELECT id_race INTO idr FROM Race WHERE nom = 'Descendant des anciens' AND id_extension = adtaf;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Descendant des anciens' ORDER BY id_skill) LOOP
		INSERT INTO RaceSkills VALUES (idr, sk.id_skill);
	END LOOP;
	RAISE NOTICE 'Inserts in RaceSkills completed';
	--SELECT id_org INTO ido FROM Organizations WHERE nom = 'Espion' AND id_extension = orianis;
	--FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Espion' AND id_extension = orianis ORDER BY id_skill) LOOP
	--	INSERT INTO OrgSkills VALUES (ido, sk.id_skill);
	--END LOOP;
	--RAISE NOTICE 'Inserts in OrgSkills completed';
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Horya' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Horya' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Manahil' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Manahil' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Shuuchuu' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Shuuchuu' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Physiocura' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Physiocura' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Shurodingeru' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Shurodingeru' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Omega-1' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Omega-1' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Omega-2' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Omega-2' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Omega-3' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Omega-3' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Omega-4' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Omega-4' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Omega-5' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Omega-5' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Omega-6' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Omega-6' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Omega-7' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Omega-7' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Omega-8' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Omega-8' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Omega-9' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Omega-9' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Omega-10' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Omega-10' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Omega-11' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Omega-11' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Omega-12' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Omega-12' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Omega-13' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Omega-13' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Furya' AND id_extension = xyord;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Furya' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Ignos' AND id_extension = xyord;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Ignos' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	RAISE NOTICE 'Inserts in SymbiontSkills completed';
	RAISE NOTICE 'Updates for v6 completed';
END v6update $$;

-- Functions
CREATE OR REPLACE FUNCTION affiliate
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	org Organizations.nom%TYPE,
	ext Extensions.id_extension%TYPE
) RETURNS void AS $$
DECLARE
	orgid Organizations.id_org%TYPE;
	nbr INT;
	sk RECORD;
BEGIN
	SELECT COUNT(*) INTO nbr FROM Organizations
	WHERE (nom = org);
	IF nbr > 0 OR org = NULL THEN
		IF ext = NULL THEN
			SELECT id_org INTO orgid FROM Organizations
			WHERE (nom = org);
		ELSE
			SELECT id_org INTO orgid FROM Organizations
			WHERE (nom = org AND id_extension = ext);
		END IF;
		UPDATE Characterr
		SET affiliated_with = orgid
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
		IF org IS NOT NULL THEN
			IF ext = NULL THEN
				FOR sk IN (SELECT * FROM get_orgskills(org)) LOOP
					PERFORM assign_skill(dbkey,idserv,idchan,sk.id_skill);
				END LOOP;
			ELSE
				FOR sk IN (SELECT * FROM get_orgskills(org) WHERE id_extension = ext) LOOP
					PERFORM assign_skill(dbkey,idserv,idchan,sk.id_skill);
				END LOOP;
			END IF;
		END IF;
	END IF;
END;
$$ LANGUAGE plpgsql;
