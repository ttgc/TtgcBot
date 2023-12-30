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
	INSERT INTO Race (nom, id_extension) VALUES ('Humains', adtaf), ('Descendant des anciens', adtaf);
	RAISE NOTICE 'Inserts in Race completed';
	-- Class
	SELECT id_race INTO idr FROM Race WHERE nom = 'Humains' AND id_extension = adtaf;
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
	('Presence', 'Octroie la possibilite de faire usage de l''aura a son hôte mais retire egalement toute possibilite de cumuler et d''user de points d''anti-aura', 'Horya', 'symbiont horya', orianis),
	('Combat deterministe', 'Au debut d''un combat, l''hôte peut realiser un jet d''intimidation (charisme), en fonction du resultat il se voit octroyer plus ou moins de points d''auras utilisables uniquement sur ce combat', 'Horya', 'symbiont horya', orianis),
	('Ambivalence energetique', 'Permet d''utiliser ses PV pour payer un coût en PM. Le coût est alors multiplie par 1,25', 'Manahil', 'symbiont manahil', orianis),
	('Barriere de mana', 'Permet de generer une barriere de mana pour encaisser n''importe quel type de degâts avec un coût en PM equivalent au degâts initiaux multiplie par 1,25 (max : 300 PM / tour)', 'Manahil', 'symbiont manahil', orianis),
	('Perte seche', 'Si l''hôte tombe en dessous de 100 PM restants, il perdra 50 PV / tour tant qu''il ne remontera pas au dessus de 100 PM', 'Manahil', 'symbPerte secheiont manahil', orianis),
	('Combo agressif', 'Pour chaque action offensive reussie, la marge de reussite critique augmente de 1 jusqu''a un maximum de 10 (non cumulable). En cas d''echec sur une action offensive ou si aucune action offensive n''est entreprise pendant deux tours ou plus, ce bonus est reinitialise', 'Shuuchuu', 'symbiont shuuchuu', orianis),
	('Concentration', 'Permet une fois par combat de passer en posture de focalisation pour une duree maximale de 5 tours', 'Shuuchuu', 'symbiont shuuchuu', orianis),
	('Gratuite energetique', 'En posture de focalisation, une fois par tour, le personnage peut lancer une action consommant jusqu''a 30 PM sans en payer le coût', 'Shuuchuu', 'symbiont shuuchuu', orianis),
	('Meditation', 'En posture de focalisation, permet de passer son action pour mediter recuperant 30+1d20 PM et retirant toutes les alterations d''etats negatives', 'Shuuchuu', 'symbiont shuuchuu', orianis),
	('Succes focalise', 'les gains de "Combo agressif" sont doubles en posture de focalisation', 'Shuuchuu', 'symbiont shuuchuu', orianis),
	('Immunite acquise', 'Immunise a toutes les alterations d''etats (hors mort), maledictions et maladies', 'Physiocura', 'symbiont physiocura', orianis),
	('Soumission eternelle', 'L''hôte meurt automatiquement si on tente de lui extraire son symbiote ou si celui-ci est detruit', 'Physiocura', 'symbiont physiocura', orianis),
	('Guerison acceleree', 'Recupere 25 PV / tour automatiquement', 'Physiocura', 'symbiont physiocura', orianis),
	('Renforcement', 'Gagne automatiquement 5 points de force par niveau jusqu''au niveau 5 inclus soit un total de 25 points supplementaires aux niveaux 5 ou superieurs. Le gain de force ne permet en aucun cas de depasser le maximum en force du personnage pour son niveau actuel', 'Physiocura', 'symbiont physiocura', orianis),
	('Dans les dents', 'Multiplie les degâts physiques infliges par 1,5. Ne fonctionne que sur les attaques au corps a corps necessitant un jet de force', 'Physiocura', 'symbiont physiocura', orianis),
	('Intrication', 'Les talents du symbiote sont transferes a l''hôte', 'Shurodingeru', 'symbiont shurodingeru', orianis);
	RAISE NOTICE 'Inserts in Skills completed';
	-- TODO: RaceSkills
	--SELECT id_race INTO idr FROM Race WHERE nom = 'Grits' AND id_extension = orianis;
	--FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Grits' ORDER BY id_skill LIMIT 1) LOOP
	--	INSERT INTO RaceSkills VALUES (idr, sk.id_skill);
	--END LOOP;
	RAISE NOTICE 'Inserts in RaceSkills completed';
	-- TODO: OrgSkills
	--SELECT id_org INTO ido FROM Organizations WHERE nom = 'Espion' AND id_extension = orianis;
	--FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Espion' AND id_extension = orianis ORDER BY id_skill) LOOP
	--	INSERT INTO OrgSkills VALUES (ido, sk.id_skill);
	--END LOOP;
	RAISE NOTICE 'Inserts in OrgSkills completed';
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
	RAISE NOTICE 'Inserts in SymbiontSkills completed';
	RAISE NOTICE 'Updates for v6 completed';
END v6update $$;
