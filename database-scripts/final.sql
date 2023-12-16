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
    ('Horya', orianis), ('Manahil', orianis), ('Schuuchuu', orianis), ('Physiocura', orianis), ('Shurodingeru', orianis),
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
	-- TODO: Skills
	--INSERT INTO Skills(nom, description, origine, webclass, id_extension) VALUES ('','','','',orianis);
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
	-- TODO: SymbiontSkills
	--SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Azort' AND id_extension = orianis;
	--FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Azort' ORDER BY id_skill) LOOP
	--	INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	--END LOOP;
	RAISE NOTICE 'Inserts in SymbiontSkills completed';
	RAISE NOTICE 'Updates for v6 completed';
END v6update $$;
