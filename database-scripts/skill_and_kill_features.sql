--TABLES
CREATE TABLE public.Deadcharacterr(
	charkey              VARCHAR (25) CONSTRAINT character_charkey_null NOT NULL ,
	nom                  VARCHAR (25)  ,
	lore                 VARCHAR (2000)  ,
	lvl		             INT   CONSTRAINT character_lvl_check CHECK (lvl > 0),
	argent               INT   CONSTRAINT character_argent_check CHECK (argent >= 0),
	rolled_dice          INT   ,
	succes               INT   ,
	fail                 INT   ,
	critic_success       INT   ,
	critic_fail          INT   ,
	super_critic_success INT   ,
	super_critic_fail    INT   ,
	id_server            VARCHAR (25)  ,
	id_channel           VARCHAR (25)  ,
	id_inventory         INT   ,
	classe 							 INT	 ,
	CONSTRAINT prk_constraint_deadchar PRIMARY KEY (charkey, id_server, id_channel)
)WITHOUT OIDS;

ALTER TABLE public.Deadcharacterr ADD CONSTRAINT FK_deadchar_id_serverchan FOREIGN KEY (id_server,id_channel) REFERENCES public.JDR(id_server,id_channel);
ALTER TABLE public.Deadcharacterr ADD CONSTRAINT FK_deadchar_id_inventory FOREIGN KEY (id_inventory) REFERENCES public.Inventaire(id_inventory);

CREATE TABLE public.Skills(
	id_skill							SERIAL	,
	nom 									VARCHAR (25) CONSTRAINT skills_nom_null NOT NULL	,
	description						VARCHAR (100) CONSTRAINT skills_descr_null NOT NULL	,
	origine								VARCHAR (25) CONSTRAINT skills_origin_null NOT NULL	,
	webclass							VARCHAR (50)	,
	CONSTRAINT prk_constraint_skills PRIMARY KEY (id_skill)
)WITHOUT OIDS;

CREATE TABLE public.Race(
	id_race								SERIAL	,
	nom 									VARCHAR (25) CONSTRAINT race_nom_null NOT NULL	,
	CONSTRAINT prk_constraint_race PRIMARY KEY (id_race);
)WITHOUT OIDS;

CREATE TABLE public.Classe(
	id_classe							SERIAL	,
	id_race								INT CONSTRAINT classe_race_null NOT NULL	,
	nom 									VARCHAR (25) CONSTRAINT classe_nom_null NOT NULL	,
	CONSTRAINT prk_constraint_classe PRIMARY KEY (id_classe);
)WITHOUT OIDS;

CREATE TABLE public.havingskill(
	charkey              VARCHAR (25) CONSTRAINT character_charkey_null NOT NULL ,
	id_server            VARCHAR (25)  ,
	id_channel           VARCHAR (25)  ,
	id_skill						 INT	,
	CONSTRAINT prk_constraint_havingskill PRIMARY KEY (charkey,id_server,id_channel,id_skill);
)WITHOUT OIDS;

ALTER TABLE public.Classe ADD CONSTRAINT FK_classe_id_race FOREIGN KEY (id_race) REFERENCES public.Race(id_race);
ALTER TABLE public.Characterr ADD COLUMN classe VARCHAR(25);
ALTER TABLE public.Characterr ADD CONSTRAINT FK_Character_classe FOREIGN KEY (classe) REFERENCES public.Classe(id_classe);
ALTER TABLE public.havingskill ADD CONSTRAINT FK_havingskill_char FOREIGN KEY (charkey,id_server,id_channel) REFERENCES public.Characterr(charkey,id_server,id_channel);
ALTER TABLE public.havingskill ADD CONSTRAINT FK_havingskill_skill FOREIGN KEY (id_skill) REFERENCES public.Skills(id_skill);

INSERT INTO Race(nom) VALUES ('Humain'),('Elementaire'),('Onikaosu'),('Succube'),('Magical Girl'),('Gardien'),('Ningemono'),('Machina'),('Polymorphe');
INSERT INTO Classe(id_race,nom) VALUES
(0,'Soldat'), (0,'Voleur'), (0, 'Mage'),
(1,'Elementaire'), (1,'Haut elementaire'),
(2,'Senshi'),(2,'Mahoutsukai'),
(3,'Mage'),(3,'Executrice'),(3,'Succube libre'),
(4,'Magical enchanteresse'),(4,'Magical guerriere'),
(5,'Gardien'),
(6,'Nekonya'),(6,'Inuwan'),(6,'Okamiuooon'),(6,'Kitsunekon'),(6,'Toripi'),(6,'Umahin'),(6,'Hebishuru'),(6,'Sakanakari'),(6,'Usagipyon'),(6,'Doragondraa'),
(7,'Host'),(7,'Server'),
(8,'Polymorphe');
INSERT INTO Skills(nom,description,origine,webclass) VALUES
('Artisan','Autorise et octroie +10% en artisanat (force)','General','general'),
('Negociateur','+5% en negociation (charisme)','General','general'),
('Charmeur','+5% en seduction (charisme)','General','general'),
('Alchimiste','Autorise et octroie +10% en alchimie (esprit)'),
('Ambianceur','+10% pour detendre l\'atmosphere (augmente egalement l\'impact de l\'action)','General','general'),
('Fouineur','+10% en fouille (agilite)','General','general'),
('Chanceux','Double le nombre de points de karma gagne / perdu','General','general');

--TRIGGER
CREATE OR REPLACE FUNCTION blockdeadchar () RETURNS TRIGGER AS $blockdeadchar$
BEGIN
	new.lvl := old.lvl;
	new.rolled_dice := old.rolled_dice;
	new.succes := old.succes;
	new.fail := old.fail;
	new.critic_success := old.critic_success;
	new.critic_fail := old.critic_fail;
	new.super_critic_success := old.super_critic_success;
	new.super_critic_fail := old.super_critic_fail;
	RETURN new;
END;
$blockdeadchar$ LANGUAGE plpgsql;

CREATE TRIGGER blockdeadchar
BEFORE UPDATE ON Deadcharacterr
FOR EACH ROW
EXECUTE PROCEDURE blockdeadchar();

--FUNCTIONS
CREATE OR REPLACE FUNCTION kill
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS void AS $$
DECLARE
	line RECORD;
BEGIN
		FOR line IN (SELECT nom,lore,lvl,argent,rolled_dice,succes,fail,critic_success,critic_fail,super_critic_success,super_critic_fail,id_inventory,classe FROM Characterr
			WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan) LOOP
		INSERT INTO Deadcharacterr
		VALUES (dbkey,line.nom,line.lore,line.lvl,line.argent,line.rolled_dice,line.succes,line.fail,line.critic_success,line.critic_fail,line.super_critic_success,line.super_critic_fail,idserv,idchan,line.id_inventory,line.classe);
		UPDATE Characterr
		SET id_inventory = NULL
		WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan;
		DELETE FROM Characterr
		WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan;
	END LOOP;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_deadcharacter
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS SETOF Deadcharacterr AS $$
DECLARE
	nbr INT;
	src JDR.id_channel%TYPE;
BEGIN
	SELECT COUNT(*) INTO nbr FROM JDRextension
	WHERE (id_server = idserv AND id_target = idchan);
	IF nbr = 0 THEN
		RETURN QUERY
		SELECT * FROM Deadcharacterr
		WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan;
	ELSE
		SELECT id_src INTO src FROM JDRextension
		WHERE (id_server = idserv AND id_target = idchan);
		RETURN QUERY
		SELECT * FROM Deadcharacterr
		WHERE charkey = dbkey AND id_server = idserv AND id_channel = src;
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION is_dead
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS BOOL AS $$
DECLARE
	nbr INT;
BEGIN
	SELECT COUNT(*) INTO nbr FROM Deadcharacterr
	WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	RETURN (nbr <> 0);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION assign_skill
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	idskill Skills.id_skill%TYPE
) RETURNS VOID AS $$
BEGIN
	INSERT INTO havingskill
	VALUES (dbkey,idserv,idchan,idskill);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_skill
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS SETOF skills AS $$
BEGIN
	RETURN QUERY
	SELECT id_skill,nom,description,origine,webclass FROM skills
	INNER JOIN havingskill ON (skills.id_skill = havingskill.id_skill)
	WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION skillinfo
(
	idskill Skills.id_skill%TYPE
) RETURNS SETOF skills AS $$
BEGIN
	RETURN QUERY
	SELECT * FROM skills
	WHERE (id_skill = idskill);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION skillsearch
(
	name Skills.nom%TYPE
) RETURNS SETOF skills AS $$
BEGIN
	RETURN QUERY
	SELECT * FROM skills
	WHERE (nom = name);
END;
$$ LANGUAGE plpgsql;

--REWRITTEN FUNCTIONS
CREATE OR REPLACE FUNCTION chardelete
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS void AS $$
BEGIN
	DELETE FROM Characterr
	WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan;
	--update
	DELETE FROM Deadcharacterr
	WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan;
	--end of update
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION jdrdelete
(
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS void AS $$
DECLARE
	line RECORD;
BEGIN
	PERFORM JDRstopallextend(idserv,idchan);
	FOR line IN (SELECT charkey FROM Characterr WHERE id_server = idserv AND id_channel = idchan) LOOP
		PERFORM chardelete(line.charkey, idserv, idchan);
	END LOOP;
	--update
	FOR line IN (SELECT charkey FROM Deadcharacterr WHERE id_server = idserv AND id_channel = idchan) LOOP
		PERFORM chardelete(line.charkey, idserv, idchan);
	END LOOP;
	--end of update
	DELETE FROM finalize
	WHERE id_server = idserv AND id_channel = idchan;
	DELETE FROM JDR
	WHERE id_server = idserv AND id_channel = idchan;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION initCharacter () RETURNS TRIGGER AS $initCharacter$
BEGIN
	IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
		UPDATE JDR
		SET PJs = PJs + 1
		WHERE id_server = new.id_server AND id_channel = new.id_channel;
		new.rolled_dice := new.critic_success + new.critic_fail + new.super_critic_success + new.super_critic_fail + new.succes + new.fail;
		UPDATE inventaire
		SET size_max = 40*FLOOR(new.strength/10)/10
		WHERE charkey = new.charkey;
	END IF;
	IF TG_OP = 'DELETE' OR TG_OP = 'UPDATE' THEN
		UPDATE JDR
		SET PJs = PJs - 1
		WHERE id_server = old.id_server AND id_channel = old.id_channel;
		IF TG_OP = 'UPDATE' THEN
			UPDATE inventaire
			SET size_max = 40*FLOOR(new.strength/10)/10
			WHERE charkey = old.charkey;
		ELSE
			DELETE FROM havingskill
			WHERE (charkey = old.charkey AND id_server = old.id_server AND id_channel = old.id_channel);
		END IF;
	END IF;
	IF TG_OP = 'DELETE' THEN
		RETURN old;
	ELSE
		RETURN new;
	END IF;
END;
$initCharacter$ LANGUAGE plpgsql;
