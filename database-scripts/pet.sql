CREATE TABLE public.Pet(
	petkey           	 VARCHAR (25) CONSTRAINT pet_petkey_null NOT NULL ,
	nom                  VARCHAR (25)  ,
	espece				 VARCHAR (25)  ,
	lvl		             INT   CONSTRAINT pet_lvl_check CHECK (lvl > 0),
	PV                   INT   ,
	PVmax                INT   CONSTRAINT pet_pvmax_check CHECK (PVmax > 0),
	PM                   INT   CONSTRAINT pet_pm_check CHECK (PM >= 0),
	PMmax                INT   CONSTRAINT pet_pmmax_check CHECK (PMmax >= 0),
	strength             INT   CONSTRAINT pet_str_check CHECK (strength > 0 AND strength <= 100),
	spirit               INT   CONSTRAINT pet_spr_check CHECK (spirit > 0 AND spirit <= 100),
	charisma             INT   CONSTRAINT pet_cha_check CHECK (charisma > 0 AND charisma <= 100),
	agility              INT   CONSTRAINT pet_agi_check CHECK (agility > 0 AND agility <= 100),
	karma                INT   CONSTRAINT pet_kar_check CHECK (karma >= -10 AND karma <= 10),
	instinct             INT   CONSTRAINT pet_int_check CHECK (instinct > 0 AND instinct <= 6),
	rolled_dice          INT   ,
	succes               INT   ,
	fail                 INT   ,
	critic_success       INT   ,
	critic_fail          INT   ,
	super_critic_success INT   ,
	super_critic_fail    INT   ,
	id_server            VARCHAR (25)  ,
	id_channel           VARCHAR (25)  ,
	charkey				 VARCHAR (25)  ,
	gm                   CHAR (1)   ,
	gm_default		     CHAR (1)   ,
	CONSTRAINT prk_constraint_pet PRIMARY KEY (petkey,id_server,id_channel,charkey) ,
	CONSTRAINT pet_pvpvmax_check CHECK (PV <= PVmax) ,
	CONSTRAINT pet_pmpmmax_check CHECK (PM <= PMmax)
)WITHOUT OIDS;

ALTER TABLE public.Pet ADD CONSTRAINT FK_Pet_gm FOREIGN KEY (gm) REFERENCES public.Gamemods(gm_code);
ALTER TABLE public.Pet ADD CONSTRAINT FK_Pet_gm_default FOREIGN KEY (gm_default) REFERENCES public.Gamemods(gm_code);
ALTER TABLE public.Pet ADD CONSTRAINT FK_Pet_character FOREIGN KEY (id_server,id_channel,charkey) REFERENCES public.Characterr(id_server,id_channel,charkey);

--Trigger
CREATE OR REPLACE FUNCTION rolledPet () RETURNS TRIGGER AS $rolledPet$
BEGIN
	new.rolled_dice := new.critic_success + new.critic_fail + new.super_critic_success + new.super_critic_fail + new.succes + new.fail;
	RETURN new;
END;
$rolledPet$ LANGUAGE plpgsql;

CREATE TRIGGER rolledPet
BEFORE INSERT OR UPDATE ON Pet
FOR EACH ROW
EXECUTE PROCEDURE rolledPet();

--Updated existing functions
CREATE OR REPLACE FUNCTION chardelete
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS void AS $$
BEGIN
	--update here
	DELETE FROM Pet
	WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan;
	--end of update
	DELETE FROM Characterr
	WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION resetchar
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS void AS $$
BEGIN
	UPDATE Characterr
	SET PV = PVmax,
	PM = PMmax,
	karma = defaultkarma,
	gm = gm_default
	WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan;
	--update here
	UPDATE Pet
	SET PV = PVmax,
	PM = PMmax,
	karma = 0,
	gm = gm_default
	WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan;
	--end of update
END;
$$ LANGUAGE plpgsql;

--Functions
CREATE OR REPLACE FUNCTION petcreate
(
	dbkey Pet.petkey%TYPE,
	charact Characterr.charkey%TYPE,
	idserv Characterr.id_server%TYPE,
	idchan Characterr.id_channel%TYPE
) RETURNS void AS $$
BEGIN
	INSERT INTO Pet
	VALUES (dbkey, dbkey, 'Unknown', 1, 1, 1, 0, 0, 50, 50, 50, 50, 0, 3, 0, 0, 0, 0, 0, 0, 0, idserv, idchan, charact, 'O', 'O');
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION petdelete
(
	dbkey Pet.petkey%TYPE,
	charact Characterr.charkey%TYPE,
	idserv Characterr.id_server%TYPE,
	idchan Characterr.id_channel%TYPE
) RETURNS void AS $$
BEGIN
	DELETE FROM Pet
	WHERE petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan;
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

CREATE OR REPLACE FUNCTION petsetespece
(
	dbkey Pet.petkey%TYPE,
	charact Characterr.charkey%TYPE,
	idserv Characterr.id_server%TYPE,
	idchan Characterr.id_channel%TYPE,
	esp Pet.espece%TYPE
) RETURNS void AS $$
BEGIN
	UPDATE Pet
	SET espece = esp
	WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION petsetname
(
	dbkey Pet.petkey%TYPE,
	charact Characterr.charkey%TYPE,
	idserv Characterr.id_server%TYPE,
	idchan Characterr.id_channel%TYPE,
	name Pet.nom%TYPE
) RETURNS void AS $$
BEGIN
	UPDATE Pet
	SET nom = name
	WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION pethasroll
(
	dbkey Pet.petkey%TYPE,
	charact Characterr.charkey%TYPE,
	idserv Characterr.id_server%TYPE,
	idchan Characterr.id_channel%TYPE,
	valmax INT,
	val INT
) RETURNS void AS $$
BEGIN
	IF val = 42 THEN
		UPDATE Pet
		SET super_critic_success = super_critic_success + 1
		WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
	ELSE
		IF val = 66 THEN
			UPDATE Pet
			SET super_critic_fail = super_critic_fail + 1
			WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
		ELSE
			IF val <= 10 THEN
				UPDATE Pet
				SET critic_success = critic_success + 1
				WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
			ELSE
				IF val >= 91 THEN
					UPDATE Pet
					SET critic_fail = critic_fail + 1
					WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
				ELSE
					IF val <= valmax THEN
						UPDATE Pet
						SET succes = succes + 1
						WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
					ELSE
						UPDATE Pet
						SET fail = fail + 1
						WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
					END IF;
				END IF;
			END IF;
		END IF;
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION petswitchmod
(
	dbkey Pet.petkey%TYPE,
	charact Characterr.charkey%TYPE,
	idserv Characterr.id_server%TYPE,
	idchan Characterr.id_channel%TYPE,
	def_ BOOLEAN
) RETURNS void AS $$
DECLARE
	curmod Gamemods.gm_code%TYPE;
BEGIN
	IF def_ THEN
		SELECT gm_default INTO curmod FROM Pet
		WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
		IF curmod = 'O' THEN
			curmod := 'D';
		ELSE
			curmod := 'O';
		END IF;
		UPDATE Pet
		SET gm_default = curmod
		WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
	ELSE
		SELECT gm INTO curmod FROM Pet
		WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
		IF curmod = 'O' THEN
			curmod := 'D';
		ELSE
			curmod := 'O';
		END IF;
		UPDATE Pet
		SET gm = curmod
		WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION petlevelup
(
	dbkey Pet.petkey%TYPE,
	charact Characterr.charkey%TYPE,
	idserv Characterr.id_server%TYPE,
	idchan Characterr.id_channel%TYPE
) RETURNS void AS $$
BEGIN
	UPDATE Pet
	SET lvl = lvl + 1
	WHERE (petkey = dbkey AND charkey = charact AND id_server = idserv AND id_channel = idchan);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_pets
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS SETOF Pet AS $$
DECLARE
	line RECORD;
BEGIN
	FOR line IN (SELECT charkey,id_server,id_channel FROM get_character(dbkey,idserv,idchan)) LOOP
		RETURN QUERY
		SELECT * FROM Pet
		WHERE (charkey = line.charkey AND id_server = line.id_server AND id_channel = line.id_channel);
	END LOOP;
END;
$$ LANGUAGE plpgsql;
