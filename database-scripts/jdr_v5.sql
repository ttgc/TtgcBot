-- Add new gamemods
INSERT INTO Gamemods VALUES ('I', 'Illumination'), ('S', 'Sepulchral');


-- Add extension table
CREATE TABLE public.Extensions(
	id_extension     			SERIAL ,
	universe	            VARCHAR (25) CONSTRAINT extension_universe_notnull NOT NULL ,
	world									VARCHAR (25) CONSTRAINT extension_world_notnull NOT NULL ,
	CONSTRAINT prk_constraint_extensions PRIMARY KEY (id_extension)
)WITHOUT OIDS;

INSERT INTO Extensions (universe, world) VALUES ('Cosmorigins', 'Terae'), ('Cosmorigins', 'Orianis');

-- Add symbiont tables
CREATE TABLE public.Symbiont(
	id_symbiont     			SERIAL ,
	nom 									VARCHAR (25) CONSTRAINT symbiont_nom_null NOT NULL	,
	id_extension     			INT CONSTRAINT symbiont_extension_null NOT NULL ,
	CONSTRAINT prk_constraint_symbiont PRIMARY KEY (id_symbiont)
)WITHOUT OIDS;

CREATE TABLE public.SymbiontSkills(
	id_symbiont     			INT ,
	id_skill 							INT	,
	CONSTRAINT prk_constraint_symbiontskills PRIMARY KEY (id_symbiont, id_skill)
)WITHOUT OIDS;

ALTER TABLE public.SymbiontSkills ADD CONSTRAINT FK_skills_id_symbiont FOREIGN KEY (id_symbiont) REFERENCES public.Symbiont(id_symbiont);
ALTER TABLE public.SymbiontSkills ADD CONSTRAINT FK_skills_id_skill FOREIGN KEY (id_skill) REFERENCES public.Skills(id_skill);


-- Add columns required by Orianis update
ALTER TABLE public.Skills ADD COLUMN id_extension INT;
ALTER TABLE public.Organizations ADD COLUMN id_extension INT;
ALTER TABLE public.Race ADD COLUMN id_extension INT;
UPDATE Skills SET id_extension = (SELECT id_extension FROM Extensions WHERE universe = 'Cosmorigins' AND world = 'Terae');
UPDATE Organizations SET id_extension = (SELECT id_extension FROM Extensions WHERE universe = 'Cosmorigins' AND world = 'Terae');
UPDATE Race SET id_extension = (SELECT id_extension FROM Extensions WHERE universe = 'Cosmorigins' AND world = 'Terae');
ALTER TABLE public.Skills ADD CONSTRAINT FK_skills_id_ext FOREIGN KEY (id_extension) REFERENCES public.Extensions(id_extension);
ALTER TABLE public.Organizations ADD CONSTRAINT FK_skills_id_ext FOREIGN KEY (id_extension) REFERENCES public.Extensions(id_extension);
ALTER TABLE public.Race ADD CONSTRAINT FK_skills_id_ext FOREIGN KEY (id_extension) REFERENCES public.Extensions(id_extension);


-- Add race, class, symbionts, organizations, and skills for Orianis
DO $$
<<orianisupdate>>
DECLARE
	orianis Extensions.id_extension%TYPE;
	idr Race.id_race%TYPE;
BEGIN
	SELECT id_extension INTO orianis FROM Extensions WHERE universe = 'Cosmorigins' AND world = 'Orianis';
	-- Race
	INSERT INTO Race (nom, id_extension) VALUES
	('Grits', orianis), ('Alfys', orianis), ('Nyfis', orianis), ('Darfys', orianis), ('Zyrfis', orianis),
	('Idylis', orianis), ('Lythis', orianis), ('Itys', orianis), ('Alwenys', orianis), ('Vampyris', orianis);
	RAISE NOTICE 'Inserts in Race completed';
	-- Class
	SELECT id_race INTO idr FROM Race WHERE nom = 'Grits' AND id_extension = orianis;
	INSERT INTO Classe (id_race, nom) VALUES (idr, 'Techno-guerrier'), (idr, 'Technomancien'), (idr, 'Transhumain');
	SELECT id_race INTO idr FROM Race WHERE nom = 'Alfys' AND id_extension = orianis;
	INSERT INTO Classe (id_race, nom) VALUES (idr, 'Imperialfys'), (idr, 'Sacralfys');
	SELECT id_race INTO idr FROM Race WHERE nom = 'Nyfis' AND id_extension = orianis;
	INSERT INTO Classe (id_race, nom) VALUES (idr, 'Negociateur'), (idr, 'Bagarreur'), (idr, 'Explorateur');
	SELECT id_race INTO idr FROM Race WHERE nom = 'Darfys' AND id_extension = orianis;
	INSERT INTO Classe (id_race, nom) VALUES (idr, 'Assassin'), (idr, 'Roublard');
	SELECT id_race INTO idr FROM Race WHERE nom = 'Zyrfis' AND id_extension = orianis;
	INSERT INTO Classe (id_race, nom) VALUES (idr, 'Guerrier ancestral'), (idr, 'Neo-guerrier'), (idr, 'Guerrier Armageddon');
	SELECT id_race INTO idr FROM Race WHERE nom = 'Idylis' AND id_extension = orianis;
	INSERT INTO Classe (id_race, nom) VALUES (idr, 'Idylis');
	SELECT id_race INTO idr FROM Race WHERE nom = 'Lythis' AND id_extension = orianis;
	INSERT INTO Classe (id_race, nom) VALUES (idr, 'Lythis');
	SELECT id_race INTO idr FROM Race WHERE nom = 'Itys' AND id_extension = orianis;
	INSERT INTO Classe (id_race, nom) VALUES (idr, 'Itys');
	SELECT id_race INTO idr FROM Race WHERE nom = 'Alwenys' AND id_extension = orianis;
	INSERT INTO Classe (id_race, nom) VALUES (idr, 'Alwenys');
	SELECT id_race INTO idr FROM Race WHERE nom = 'Vampyris' AND id_extension = orianis;
	INSERT INTO Classe (id_race, nom) VALUES (idr, 'Vampyris');
	RAISE NOTICE 'Inserts in Classe completed';
	-- Symbionts
	INSERT INTO Symbiont (nom, id_extension) VALUES ('Azort', orianis), ('Iridyanis', orianis), ('Enairo', orianis);
	RAISE NOTICE 'Inserts in Symbionts completed';
	-- Organizations
	--INSERT INTO Organizations(nom) VALUES ('');
	RAISE NOTICE 'Inserts in Organizations completed';
	-- Skills
	--INSERT INTO Skills(nom,description,origine,webclass) VALUES ('','','','');
	RAISE NOTICE 'Inserts in Skills completed';
	-- RaceSkills
	RAISE NOTICE 'Inserts in RaceSkills completed';
	-- OrgSkills
	RAISE NOTICE 'Inserts in OrgSkills completed';
	-- SymbiontSkills
	RAISE NOTICE 'Inserts in SymbiontSkills completed';
END orianisupdate $$;


-- Perform update of characterr
ALTER TABLE public.Characterr ADD COLUMN hybrid_race INT CONSTRAINT character_hybrid_default DEFAULT NULL;
ALTER TABLE public.Characterr ADD COLUMN id_symbiont INT CONSTRAINT character_symbiont_default DEFAULT NULL;
ALTER TABLE public.Characterr ADD COLUMN pilot_p INT CONSTRAINT character_pilotp_notnull NOT NULL CONSTRAINT character_pilotp_default DEFAULT -1;
ALTER TABLE public.Characterr ADD COLUMN pilot_a INT CONSTRAINT character_pilota_notnull NOT NULL CONSTRAINT character_pilota_default DEFAULT -1;
UPDATE Characterr SET hybrid_race = NULL, id_symbiont = NULL, pilot_p = -1, pilot_a = -1;
ALTER TABLE public.Characterr ADD CONSTRAINT FK_character_hybrid FOREIGN KEY (hybrid_race) REFERENCES public.Race(id_race);
ALTER TABLE public.Characterr ADD CONSTRAINT FK_character_symbiont FOREIGN KEY (id_symbiont) REFERENCES public.Symbiont(id_symbiont);


-- new fonctions
CREATE OR REPLACE FUNCTION usepoints
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	item VARCHAR
) RETURNS void AS $$
BEGIN
	IF LOWER(item) = 'lightpt' THEN
		UPDATE Characterr
		SET light_points = light_points - 1,
		karma = 10,
		--UPDATE HERE
		gm = 'I'
		--END OF UPDATE
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(item) = 'darkpt' THEN
		UPDATE Characterr
		SET dark_points = dark_points - 1,
		karma = -10,
		--UPDATE HERE
		gm = 'S'
		--END OF UPDATE
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION end_lpdp_gamemod
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS void AS $$
DECLARE
	currentgm Characterr.gm%TYPE;
BEGIN
	SELECT gm INTO currentgm FROM Characterr
	WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	IF currentgm IN ('I', 'S') THEN
		UPDATE Characterr
		SET gm = gm_default
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
END;
$$ LANGUAGE plpgsql;
