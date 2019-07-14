-- Add and rename some class
UPDATE Classe SET nom = 'Enchanteur' WHERE id_race = 6;
INSERT INTO Classe(id_race,nom) VALUES (6,'Protecteur');
UPDATE Classe SET nom = 'Ensorceleuse' WHERE id_race = 4 AND nom = 'Succube libre';

-- Add stats
ALTER TABLE public.Characterr ADD COLUMN prec INT;
ALTER TABLE public.Characterr ADD COLUMN luck INT;
ALTER TABLE public.Characterr ADD CONSTRAINT character_prec_check CHECK (prec > 0 AND prec <= 100);
ALTER TABLE public.Characterr ADD CONSTRAINT character_luck_check CHECK (luck > 0 AND luck <= 100);
ALTER TABLE public.Pet ADD COLUMN prec INT;
ALTER TABLE public.Pet ADD COLUMN luck INT;
ALTER TABLE public.Pet ADD CONSTRAINT pet_prec_check CHECK (prec > 0 AND prec <= 100);
ALTER TABLE public.Pet ADD CONSTRAINT pet_luck_check CHECK (luck > 0 AND luck <= 100);

-- Add organizations and affiliates for the game
CREATE TABLE public.Organizations(
	id_org		      			SERIAL ,
	nom				            VARCHAR (30) CONSTRAINT org_nom_null NOT NULL ,
	CONSTRAINT prk_constraint_organizations PRIMARY KEY (id_org)
)WITHOUT OIDS;

CREATE TABLE public.OrgSkills(
	id_org		      			 INT ,
	id_skill							 INT ,
	CONSTRAINT prk_constraint_orgskills PRIMARY KEY (id_org, id_skill)
)WITHOUT OIDS;

CREATE TABLE public.RaceSkills(
	id_race		      			 INT ,
	id_skill							 INT ,
	CONSTRAINT prk_constraint_raceskills PRIMARY KEY (id_race, id_skill)
)WITHOUT OIDS;

ALTER TABLE public.OrgSkills ADD CONSTRAINT FK_orgskills_id_org FOREIGN KEY (id_org) REFERENCES public.Organizations(id_org);
ALTER TABLE public.RaceSkills ADD CONSTRAINT FK_orgskills_id_race FOREIGN KEY (id_race) REFERENCES public.Race(id_race);
ALTER TABLE public.Characterr ADD COLUMN affiliated_with INT;
ALTER TABLE public.Characterr ADD CONSTRAINT FK_char_id_org FOREIGN KEY (affiliated_with) REFERENCES public.Organizations(id_org);

-- Add organizations and their skills, and links in skil linking tables for org and race
INSERT INTO Organizations(nom) VALUES
('-');
INSERT INTO Skills(nom,description,origine,webclass) VALUES
('-','-','-','-');
INSERT INTO OrgSkills VALUES
(1,1);
INSERT INTO RaceSkills VALUES
(1,1);

-- Perform update of characterr
UPDATE Characterr SET prec = 50, luck = 50;

-- new fonctions
CREATE OR REPLACE FUNCTION affiliate
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	org Organizations.nom%TYPE
) RETURNS void AS $$
DECLARE
	orgid Organizations.id_org%TYPE;
	nbr INT;
BEGIN
	SELECT COUNT(*) INTO nbr FROM Organizations
	WHERE (nom = org);
	IF nbr > 0 THEN
		SELECT id_org INTO orgid FROM Organizations
		WHERE (nom = org);
		UPDATE Characterr
		SET affiliated_with = orgid
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_orgskills
(
	org Organizations.nom%TYPE
) RETURNS SETOF Skills AS $$
DECLARE
	orgid Organizations.id_org%TYPE;
BEGIN
	SELECT id_org INTO orgid FROM Organizations
	WHERE (nom = org);
	RETURN QUERY
	SELECT Skills.id_skill, nom, description, origine, webclass FROM Skills
	INNER JOIN OrgSkills ON (Skills.id_skill = OrgSkills.id_skill)
	WHERE id_org = orgid;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_raceskills
(
	racename Race.nom%TYPE
) RETURNS SETOF Skills AS $$
DECLARE
	raceid Race.id_race%TYPE;
BEGIN
	SELECT id_race INTO raceid FROM Race
	WHERE (nom = racename);
	RETURN QUERY
	SELECT Skills.id_skill, nom, description, origine, webclass FROM Skills
	INNER JOIN RaceSkills ON (Skills.id_skill = RaceSkills.id_skill)
	WHERE id_race = raceid;
END;
$$ LANGUAGE plpgsql;

-- Update old fonctions
CREATE OR REPLACE FUNCTION charcreate
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	cl Classe.id_classe%TYPE
) RETURNS void AS $$
DECLARE
	inv inventaire.id_inventory%TYPE;
	--update here
	racename Race.nom%TYPE;
	sk RECORD;
	--end of update
BEGIN
	INSERT INTO inventaire (charkey)
	VALUES (dbkey);
	SELECT MAX(id_inventory) INTO inv FROM inventaire
	WHERE charkey = dbkey;
	--update here
	INSERT INTO Characterr
	VALUES (dbkey, dbkey, '', 1, 1, 1, 1, 1, 50, 50, 50, 50, 0, 0, 0, 1, 1, 3, 100, 0, 0, 0, 0, 0, 0, 0, idserv, idchan, 'O', 'O', inv, 'NULL',false,cl,false,0,50,50);
	SELECT race.nom INTO racename FROM race
	INNER JOIN classe ON (race.id_race = classe.id_race)
	WHERE id_classe = cl;
	FOR sk IN (SELECT * FROM get_raceskills(racename)) LOOP
		PERFORM assign_skill(dbkey,idserv,idchan,sk.id_skill);
	END LOOP;
	--end of update
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION charset
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	stat VARCHAR(5),
	val INT
) RETURNS void AS $$
DECLARE
	curp INT;
	idinv INT;
	cpymoney INT;
BEGIN
	IF LOWER(stat) = 'str' THEN
		UPDATE Characterr
		SET strength = val
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'spr' THEN
		UPDATE Characterr
		SET spirit = val
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'cha' THEN
		UPDATE Characterr
		SET charisma = val
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'agi' THEN
		UPDATE Characterr
		SET agility = val
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
	-- update here
	IF LOWER(stat) = 'prec' THEN
		UPDATE Characterr
		SET prec = val
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'luck' THEN
		UPDATE Characterr
		SET luck = val
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
	-- end of update
	IF LOWER(stat) = 'kar' THEN
		UPDATE Characterr
		SET karma = karma + val
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'dkar' THEN
		UPDATE Characterr
		SET defaultkarma = val
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'pvmax' THEN
		SELECT PV INTO curp FROM Characterr
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
		IF (curp > val) THEN
			UPDATE Characterr
			SET PV = val
			WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
		END IF;
		UPDATE Characterr
		SET PVmax = val
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'pmmax' THEN
		SELECT PM INTO curp FROM Characterr
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
		IF (curp > val) THEN
			UPDATE Characterr
			SET PM = val
			WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
		END IF;
		UPDATE Characterr
		SET PMmax = val
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'pv' THEN
		UPDATE Characterr
		SET PV = PV + val
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'pm' THEN
		UPDATE Characterr
		SET PM = PM + val
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'lp' THEN
		UPDATE Characterr
		SET light_points = val
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'dp' THEN
		UPDATE Characterr
		SET dark_points = val
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'po' THEN
		SELECT id_inventory INTO idinv FROM Characterr
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
		SELECT argent INTO curp FROM Characterr
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
		cpymoney := curp;
		curp := curp / 5000;
		IF cpymoney > 0 THEN
			curp := curp + 1;
		END IF;
		UPDATE inventaire
		SET size_ = size_ - curp
		WHERE id_inventory = idinv;
		UPDATE Characterr
		SET argent = argent + val
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
		SELECT argent INTO curp FROM Characterr
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
		cpymoney := curp;
		curp := curp / 5000;
		IF cpymoney > 0 THEN
			curp := curp + 1;
		END IF;
		UPDATE inventaire
		SET size_ = size_ + curp
		WHERE id_inventory = idinv;
	END IF;
	IF LOWER(stat) = 'int' THEN
		UPDATE Characterr
		SET intuition = val
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'ment' THEN
		UPDATE Characterr
		SET mental = val
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION petset
(
	dbkey Pet.petkey%TYPE,
	charact Characterr.charkey%TYPE,
	idserv Characterr.id_server%TYPE,
	idchan Characterr.id_channel%TYPE,
	stat VARCHAR(5),
	val INT
) RETURNS void AS $$
DECLARE
	curp INT;
BEGIN
	IF LOWER(stat) = 'str' THEN
		UPDATE Pet
		SET strength = val
		WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'spr' THEN
		UPDATE Pet
		SET spirit = val
		WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'cha' THEN
		UPDATE Pet
		SET charisma = val
		WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'agi' THEN
		UPDATE Pet
		SET agility = val
		WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
	END IF;
	-- update here
	IF LOWER(stat) = 'prec' THEN
		UPDATE Pet
		SET prec = val
		WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'luck' THEN
		UPDATE Pet
		SET luck = val
		WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
	END IF;
	-- end of update
	IF LOWER(stat) = 'kar' THEN
		UPDATE Pet
		SET karma = karma + val
		WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'pvmax' THEN
		SELECT PV INTO curp FROM Pet
		WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
		IF (curp > val) THEN
			UPDATE Pet
			SET PV = val
			WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
		END IF;
		UPDATE Pet
		SET PVmax = val
		WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'pmmax' THEN
		SELECT PM INTO curp FROM Pet
		WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
		IF (curp > val) THEN
			UPDATE Pet
			SET PM = val
			WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
		END IF;
		UPDATE Pet
		SET PMmax = val
		WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'pv' THEN
		UPDATE Pet
		SET PV = PV + val
		WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'pm' THEN
		UPDATE Pet
		SET PM = PM + val
		WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'int' THEN
		UPDATE Pet
		SET instinct = val
		WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
	END IF;
END;
$$ LANGUAGE plpgsql;
