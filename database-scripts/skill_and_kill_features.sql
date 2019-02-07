--TABLES
-- CREATE TABLE public.Deadcharacterr(
-- 	charkey              VARCHAR (25) CONSTRAINT character_charkey_null NOT NULL ,
-- 	nom                  VARCHAR (25)  ,
-- 	lore                 VARCHAR (2000)  ,
-- 	lvl		             INT   CONSTRAINT character_lvl_check CHECK (lvl > 0),
-- 	argent               INT   CONSTRAINT character_argent_check CHECK (argent >= 0),
-- 	rolled_dice          INT   ,
-- 	succes               INT   ,
-- 	fail                 INT   ,
-- 	critic_success       INT   ,
-- 	critic_fail          INT   ,
-- 	super_critic_success INT   ,
-- 	super_critic_fail    INT   ,
-- 	id_server            VARCHAR (25)  ,
-- 	id_channel           VARCHAR (25)  ,
-- 	id_inventory         INT   ,
-- 	classe 							 INT	 ,
-- 	CONSTRAINT prk_constraint_deadchar PRIMARY KEY (charkey, id_server, id_channel)
-- )WITHOUT OIDS;
--
-- ALTER TABLE public.Deadcharacterr ADD CONSTRAINT FK_deadchar_id_serverchan FOREIGN KEY (id_server,id_channel) REFERENCES public.JDR(id_server,id_channel);
-- ALTER TABLE public.Deadcharacterr ADD CONSTRAINT FK_deadchar_id_inventory FOREIGN KEY (id_inventory) REFERENCES public.Inventaire(id_inventory);

CREATE TABLE public.Skills(
	id_skill							SERIAL	,
	nom 									VARCHAR (30) CONSTRAINT skills_nom_null NOT NULL	,
	description						VARCHAR (200) CONSTRAINT skills_descr_null NOT NULL	,
	origine								VARCHAR (50) CONSTRAINT skills_origin_null NOT NULL	,
	webclass							VARCHAR (50)	,
	CONSTRAINT prk_constraint_skills PRIMARY KEY (id_skill)
)WITHOUT OIDS;

CREATE TABLE public.Race(
	id_race								SERIAL	,
	nom 									VARCHAR (25) CONSTRAINT race_nom_null NOT NULL	,
	CONSTRAINT prk_constraint_race PRIMARY KEY (id_race)
)WITHOUT OIDS;

CREATE TABLE public.Classe(
	id_classe							SERIAL	,
	id_race								INT CONSTRAINT classe_race_null NOT NULL	,
	nom 									VARCHAR (25) CONSTRAINT classe_nom_null NOT NULL	,
	CONSTRAINT prk_constraint_classe PRIMARY KEY (id_classe)
)WITHOUT OIDS;

CREATE TABLE public.havingskill(
	charkey              VARCHAR (25) CONSTRAINT character_charkey_null NOT NULL ,
	id_server            VARCHAR (25)  ,
	id_channel           VARCHAR (25)  ,
	id_skill						 INT	,
	CONSTRAINT prk_constraint_havingskill PRIMARY KEY (charkey,id_server,id_channel,id_skill)
)WITHOUT OIDS;

ALTER TABLE public.Classe ADD CONSTRAINT FK_classe_id_race FOREIGN KEY (id_race) REFERENCES public.Race(id_race);
ALTER TABLE public.Characterr ADD COLUMN dead BOOL;
ALTER TABLE public.Characterr ADD COLUMN classe INT;
ALTER TABLE public.Characterr ADD CONSTRAINT FK_Character_classe FOREIGN KEY (classe) REFERENCES public.Classe(id_classe);
ALTER TABLE public.havingskill ADD CONSTRAINT FK_havingskill_char FOREIGN KEY (charkey,id_server,id_channel) REFERENCES public.Characterr(charkey,id_server,id_channel);
ALTER TABLE public.havingskill ADD CONSTRAINT FK_havingskill_skill FOREIGN KEY (id_skill) REFERENCES public.Skills(id_skill);

INSERT INTO Race(nom) VALUES ('Humain'),('Elementaire'),('Onikaosu'),('Succube'),('Magical Girl'),('Gardien'),('Ningemono'),('Machina'),('Polymorphe');
INSERT INTO Classe(id_race,nom) VALUES
(1,'Soldat'), (1,'Voleur'), (1, 'Mage'),
(2,'Elementaire'), (2,'Haut elementaire'),
(3,'Senshi'),(3,'Mahoutsukai'),
(4,'Mage'),(4,'Executrice'),(4,'Succube libre'),
(5,'Magical enchanteresse'),(5,'Magical guerriere'),
(6,'Gardien'),
(7,'Nekonya'),(7,'Inuwan'),(7,'Okamiuooon'),(7,'Kitsunekon'),(7,'Toripi'),(7,'Umahin'),(7,'Hebishuru'),(7,'Sakanakari'),(7,'Usagipyon'),(7,'Doragondraa'),
(8,'Host'),(8,'Server'),
(9,'Polymorphe');
INSERT INTO Skills(nom,description,origine,webclass) VALUES
('Artisan','Autorise et octroie +10% en artisanat (force)','General','general'),
('Negociateur','+5% en negociation (charisme)','General','general'),
('Charmeur','+5% en seduction (charisme)','General','general'),
('Alchimiste','Autorise et octroie +10% en alchimie (esprit)','General','general'),
('Ambianceur','+10% pour detendre l''atmosphere (augmente egalement l''impact de l''action)','General','general'),
('Fouineur','+10% en fouille (agilite)','General','general'),
('Chanceux','Double le nombre de points de karma gagne / perdu','General','general'),
('Mur de pierre','+10% en parade / -10% en esquive','Humain Soldat','human soldat'),
('Courageux','+20% en attaque d''opportunite','Humain Soldat','human soldat'),
('Protecteur','+10% en action defensive pour proteger un allie','Humain Soldat','human soldat'),
('Guerrier','+5% sur une action offensive','Humain Soldat','human soldat'),
('Persuasif','+10% pour convaincre','Humain Soldat','human soldat'),
('Diversion','+10% pour faire diversion','Humain Soldat','human soldat'),
('Manipulateur','+10% en arnaque','Humain Voleur','human voleur'),
('Fouilleur','+15% en fouille (incompatible fouineur)','Humain Voleur','human voleur'),
('Discretion','+10% pour etre furtif/discret','Humain Voleur','human voleur'),
('Rapide','+10% en mouvement rapide','Humain Voleur','human voleur'),
('Diversion','+10% pour faire diversion','Humain Voleur','human voleur'),
('Concentration','+5% pour detecter les traces de magie','Humain Mage','human mage'),
('Manipulation mentale','+10% en influence ou manipulation','Humain Mage','human mage'),
('Rapidite','+10% en esquive','Humain Mage','human mage'),
('Minimiseur','Inventaire et bourse 50% plus grands','Humain Mage','human mage'),
('Diversion','+10% pour faire diversion','Humain Mage','human mage'),
('Charme naturel','+15% en seduction','Succube','succube'),
('Demon','-4 de base en karma','Succube','succube'),
('Nyctalope','Ah on savait bien que c''etaient des...','Succube','succube'),
('Vol','Les ailes des succubes leur permettent de voler a basse altitude','Succube','succube'),
('Envoutement','Une cible charmee ne peut pas retrouver ses esprits normalement','Succube','succube'),
('Absorption','Absorbe 10% des degats infliges','Succube','succube'),
('Concentration','+15% pour detecter les traces de magie','Succube Mage','succube mage'),
('Manipulation mentale','+15% en influence ou manipulation','Succube Mage','succube mage'),
('Rapidite','+10% en esquive','Succube Mage','succube mage'),
('Minimiseur','Inventaire et bourse deux fois plus grands','Succube Mage','succube mage'),
('Forme demoniaque','Transformation :\nRegen PM\nMode offensif auto\n+5% charisme/esprit\n-5 karma a l''activation\nPerte de PV / tour proportionnelle\nJet d''esprit passif pour arreter la transformation','Succube Mage','succube mage'),
('Force','+15% en action offensive','Succube Executrice','succube executrice'),
('Manipulation mentale','+10% en influence ou manipulation','Succube Executrice','succube executrice'),
('Sadique','+10% en action offensive contre une cible blessee','Succube Executrice','succube executrice'),
('Maitre d''arme','Capable de manier n''importe quelle arme sans entrainement','Succube Executrice','succube executrice'),
('Forme demoniaque','Transformation :\nRegen PM\nMode offensif auto\n+5% charisme/esprit\n-5 karma a l''activation\nPerte de PV / tour proportionnelle\nJet d''esprit passif pour arreter la transformation','Succube Executrice','succube executrice'),
('Influence','+10% pour influencer une decision','Succube libre','succube slibre'),
('Force de groupe','+15% aux jets d''actions combinees','Succube libre','succube slibre'),
('Rapidite','+10% en esquive','Succube','succube slibre'),
('Sens des affaires','+10% en negociation (incompatible negociateur)','Succube','succube slibre'),
('Arnaqueuse','+10% en arnaque (non cumulable avec sens des affaires)','Succube','succube slibre'),
('Demon','-5 de base en karma','Onikaosu','onikaosu'),
('Nyctalope','Permet de voir dans le noir','Onikaosu','onikaosu'),
('Forme demoniaque','Transformation :\nRegen PM\nMode offensif auto\n+5% charisme/esprit\n-5 karma a l''activation\nPerte de PV / tour proportionnelle\nJet d''esprit passif pour arreter la transformation','Onikaosu','onikaosu'),
('Dechainement','Consomme x PV pour augmenter les degats infliges de x points','Onikaosu','onikaosu'),
('Reactivite','+10% en parade','Onikaosu','onikaosu'),
('Afflux psychique','Lorsque les PM sont faibles, les PM se regenerent de 10 pts jusqu''a 150 pts max, non cumulatif','Onikaosu Mahoutsukai','onikaosu mahoutsukai'),
('Afflux mental','Utilise 20x PM supplementaire pour obtenir un bonus de 5x% en jet d''esprit (max 100 PM / jet)','Onikaosu Mahoutsukai','onikaosu mahoutsukai'),
('Minimiseur','Inventaire et bourse 150% plus grands','Onikaosu Mahoutsukai','onikaosu mahoutsukai'),
('Fortification','Consomme 10x PM pour augmenter l''armure de x points pendant le prochain tour (max 50 PM / tour)','Onikaosu Senshi','onikaosu senshi'),
('Afflux physique','Utilise 20x PM supplementaire pour obtenir un bonus de 5x% en jet de force (max 100 PM / jet)','Onikaosu Senshi','onikaosu senshi'),
('Point faible','Frappe la ou ca fait mal en priorite si l''action est possible','Onikaosu Senshi','onikaosu senshi'),
('Opportuniste','Agit en premier en combat s''il/elle est en mode offensif','Onikaosu Senshi','onikaosu senshi'),
('Controle elementaire','Peut deplacer une source elementaire correspondant a l''element associe au personnage sans cout de mana','Elementaire','elem'),
('Force et faiblesse','Les elementaires sont soumis a l''equilibre elementaire','Elementaire','elem'),
('Reactivite','+10% en esquive','Elementaire','elem'),
('Transformation elementaire','Transformation :\n+2 en karma lors de l''activation\n+5% en esprit\nMeme propriete physique que son element\ncout en PM proportionnel par tour\nla transformation prend fin a 0 PM','Elementaire','elem'),
('Transmission','a sa mort, transmet ses pouvoirs a la personne de son choix (obligatoire)','Haut Elementaire','elem hautelem'),
('Connexion elementaire','peut communiquer par telepathie avec un elementaire du meme element ou un haut elementaire','Haut Elementaire','elem hautelem'),
('Connexion elementaire','peut communiquer par telepathie avec un elementaire du meme element','Elementaire Classique','elem clelem'),
('Creature angelique','+4 en karma','Magical Girl','mgirl'),
('Pouvoir de l''amour','+10% sur les jets en lien avec l''amour','Magical Girl','mgirl'),
('Pouvoir scelle','le personnage est lie a sa relique magique','Magical Girl','mgirl'),
('Magical transformation','Transformation :\n+5 karma a l''activation\nLight et Dark points utilisables\n+5% en esprit/charisme\nmode defensif auto','Magical Girl','mgirl'),
('Idole','-30% pour passer inaperçu dans une foule / +30% pour les autres en test de connaissance sur elle (incompatible identite secrete)','Magical Girl','mgirl'),
('Seductrice','+15% en seduction et charme naturel','Magical Girl','mgirl'),
('Identite secrete','+30% pour passer inaperçu dans une foule / -30% pour les autres en test de connaissance sur elle (incompatible idole)','Magical Girl','mgirl'),
('Inebranlable','ne peut pas se faire assomer','Magical Girl Guerriere','mgirl mgguerriere'),
('Berserk','+10% sur les actions offensives lorsqu''un allie est attaque','Magical Girl Guerriere','mgirl mgguerriere'),
('Detachement mental','ne peut pas se faire controler mentalement','Magical Girl Enchanteresse','mgirl mggenchant'),
('Amitie magique','peut transferer ses PM a un allie','Magical Girl Enchanteresse','mgirl mggenchant'),
('Creature angelique','+5 en karma','Gardien','guardian'),
('Lien de force','un gardien est lie a son hote, le gardien ne peut succomber que si son hote est tue','Gardien','guardian'),
('Appel','Peut se teleporter a proximite de son hote pour un cout en PM proportionnel a la distance a parcourir','Gardien','guardian'),
('Mignon','+10% en jet de seduction et de charme','Gardien','guardian'),
('Force alliee','peut transfere des PM a l''hote','Gardien','guardian'),
('Pouvoir combine','en cas d''attaque combinee avec son hote, +10% sur les deux jets','Gardien','guardian'),
('Relance','une fois par combet l''hote ou le gardien peut relancer n''importe quel jet','Gardien','guardian'),
('Disparition','peut disparaitre n''importe quand mais ne peut plus agir','Gardien','guardian'),
('Connexion telepathique','Permet de communique avec son hote','Gardien','guardian');

--TRIGGER
-- CREATE OR REPLACE FUNCTION blockdeadchar () RETURNS TRIGGER AS $blockdeadchar$
-- BEGIN
-- 	new.lvl := old.lvl;
-- 	new.rolled_dice := old.rolled_dice;
-- 	new.succes := old.succes;
-- 	new.fail := old.fail;
-- 	new.critic_success := old.critic_success;
-- 	new.critic_fail := old.critic_fail;
-- 	new.super_critic_success := old.super_critic_success;
-- 	new.super_critic_fail := old.super_critic_fail;
-- 	RETURN new;
-- END;
-- $blockdeadchar$ LANGUAGE plpgsql;
--
-- CREATE TRIGGER blockdeadchar
-- BEFORE UPDATE ON Deadcharacterr
-- FOR EACH ROW
-- EXECUTE PROCEDURE blockdeadchar();

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
	UPDATE characterr
	SET dead = (true)
	WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan;
	-- FOR line IN (SELECT nom,lore,lvl,argent,rolled_dice,succes,fail,critic_success,critic_fail,super_critic_success,super_critic_fail,id_inventory,classe FROM Characterr
	-- 		WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan) LOOP
	-- 	INSERT INTO Deadcharacterr
	-- 	VALUES (dbkey,line.nom,line.lore,line.lvl,line.argent,line.rolled_dice,line.succes,line.fail,line.critic_success,line.critic_fail,line.super_critic_success,line.super_critic_fail,idserv,idchan,line.id_inventory,line.classe);
	-- 	UPDATE Characterr
	-- 	SET id_inventory = NULL
	-- 	WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan;
	-- 	DELETE FROM Characterr
	-- 	WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan;
	-- END LOOP;
END;
$$ LANGUAGE plpgsql;

-- CREATE OR REPLACE FUNCTION get_deadcharacter
-- (
-- 	dbkey Characterr.charkey%TYPE,
-- 	idserv JDR.id_server%TYPE,
-- 	idchan JDR.id_channel%TYPE
-- ) RETURNS SETOF Deadcharacterr AS $$
-- DECLARE
-- 	nbr INT;
-- 	src JDR.id_channel%TYPE;
-- BEGIN
-- 	SELECT COUNT(*) INTO nbr FROM JDRextension
-- 	WHERE (id_server = idserv AND id_target = idchan);
-- 	IF nbr = 0 THEN
-- 		RETURN QUERY
-- 		SELECT * FROM Deadcharacterr
-- 		WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan;
-- 	ELSE
-- 		SELECT id_src INTO src FROM JDRextension
-- 		WHERE (id_server = idserv AND id_target = idchan);
-- 		RETURN QUERY
-- 		SELECT * FROM Deadcharacterr
-- 		WHERE charkey = dbkey AND id_server = idserv AND id_channel = src;
-- 	END IF;
-- END;
-- $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION is_dead
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS BOOL AS $$
DECLARE
	isdead BOOL;
BEGIN
	SELECT dead INTO isdead FROM Characterr
	WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan;
	RETURN isdead;
	-- SELECT COUNT(*) INTO nbr FROM Deadcharacterr
	-- WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	-- RETURN (nbr <> 0);
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
	--update here
	DELETE FROM havingskill
	WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan;
	--end of update
	DELETE FROM Pet
	WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan;
	DELETE FROM Characterr
	WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan;
END;
$$ LANGUAGE plpgsql;

-- CREATE OR REPLACE FUNCTION jdrdelete
-- (
-- 	idserv JDR.id_server%TYPE,
-- 	idchan JDR.id_channel%TYPE
-- ) RETURNS void AS $$
-- DECLARE
-- 	line RECORD;
-- BEGIN
-- 	PERFORM JDRstopallextend(idserv,idchan);
-- 	FOR line IN (SELECT charkey FROM Characterr WHERE id_server = idserv AND id_channel = idchan) LOOP
-- 		PERFORM chardelete(line.charkey, idserv, idchan);
-- 	END LOOP;
-- 	--update
-- 	FOR line IN (SELECT charkey FROM Deadcharacterr WHERE id_server = idserv AND id_channel = idchan) LOOP
-- 		PERFORM chardelete(line.charkey, idserv, idchan);
-- 	END LOOP;
-- 	--end of update
-- 	DELETE FROM finalize
-- 	WHERE id_server = idserv AND id_channel = idchan;
-- 	DELETE FROM JDR
-- 	WHERE id_server = idserv AND id_channel = idchan;
-- END;
-- $$ LANGUAGE plpgsql;

-- CREATE OR REPLACE FUNCTION initCharacter () RETURNS TRIGGER AS $initCharacter$
-- BEGIN
-- 	IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
-- 		UPDATE JDR
-- 		SET PJs = PJs + 1
-- 		WHERE id_server = new.id_server AND id_channel = new.id_channel;
-- 		new.rolled_dice := new.critic_success + new.critic_fail + new.super_critic_success + new.super_critic_fail + new.succes + new.fail;
-- 		UPDATE inventaire
-- 		SET size_max = 40*FLOOR(new.strength/10)/10
-- 		WHERE charkey = new.charkey;
-- 	END IF;
-- 	IF TG_OP = 'DELETE' OR TG_OP = 'UPDATE' THEN
-- 		UPDATE JDR
-- 		SET PJs = PJs - 1
-- 		WHERE id_server = old.id_server AND id_channel = old.id_channel;
-- 		IF TG_OP = 'UPDATE' THEN
-- 			UPDATE inventaire
-- 			SET size_max = 40*FLOOR(new.strength/10)/10
-- 			WHERE charkey = old.charkey;
-- 		ELSE
-- 			DELETE FROM havingskill
-- 			WHERE (charkey = old.charkey AND id_server = old.id_server AND id_channel = old.id_channel);
-- 		END IF;
-- 	END IF;
-- 	IF TG_OP = 'DELETE' THEN
-- 		RETURN old;
-- 	ELSE
-- 		RETURN new;
-- 	END IF;
-- END;
-- $initCharacter$ LANGUAGE plpgsql;
