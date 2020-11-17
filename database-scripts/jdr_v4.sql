-- Add and rename some class
UPDATE Classe SET nom = 'Enchanteur' WHERE id_race = 6;
INSERT INTO Classe(id_race,nom) VALUES (6,'Protecteur');
UPDATE Classe SET nom = 'Ensorceleuse' WHERE id_race = 4 AND nom = 'Succube libre';

-- Add stats
ALTER TABLE public.Characterr ADD COLUMN prec INT;
ALTER TABLE public.Characterr ADD COLUMN luck INT;
UPDATE Characterr SET prec = 50, luck = 50;
ALTER TABLE public.Characterr ADD CONSTRAINT character_prec_check CHECK (prec > 0 AND prec <= 100);
ALTER TABLE public.Characterr ADD CONSTRAINT character_luck_check CHECK (luck > 0 AND luck <= 100);
ALTER TABLE public.Pet ADD COLUMN prec INT;
ALTER TABLE public.Pet ADD COLUMN luck INT;
UPDATE Pet SET prec = 50, luck = 50;
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

-- Expand skill columns
ALTER TABLE public.Skills ALTER COLUMN nom TYPE VARCHAR(50);
ALTER TABLE public.Skills ALTER COLUMN description TYPE VARCHAR(300);

-- Add organizations and their skills, and links in skil linking tables for org and race
UPDATE skills
SET origine = 'Gardien Enchanteur',
webclass = 'guardian enchanteur'
WHERE nom IN ('Relance', 'Disparition', 'Force alliee');

UPDATE skills
SET origine = 'Succube Ensorceleuse',
webclass = 'succube ensorceleuse'
WHERE webclass = 'succube slibre';

INSERT INTO Organizations(nom) VALUES
('Fidele de la lumiere'),
('Militaire'), ('Ingenieur'), ('Mafieux'), ('Marchand'),
('Umbrinis'), ('Faeliath'), ('Okane'), ('Guilde du savoir'),
('Onilord'), ('Kuroni'), ('Kibou'),
('Disciple de Vitalia'), ('Grand guerrier'), ('Senateur'),
('Sunien'), ('Unien'), ('Rebelle'),
('ROOT'), ('Assassin');
INSERT INTO Skills(nom,description,origine,webclass) VALUES
('Interposition','peut s''interposer lorsque son hote est cible contre un jet d''agilite, en cas de reussite le gardien peut tenter une parade si applicable','Gardien Protecteur','guardian protecteur'),
('Casser la baraque','+5% de critique sur les jets de force','Gardien Protecteur','guardian protecteur'),
('La lumiere guide vos pas','Vous permet d''invoquer la lumiere divine pour vous eclairer. Cette lumiere n''a aucun impact offensif ni defensif','Fidele de la lumiere','general affiliation saisho'),
('Benediction divine','En priant, permet de vous guerir d''une malediction puissante au prix d''un montant proportionnel de PM max perdus definitivement','Fidele de la lumiere','general affiliation saisho'),
('Absolution','La lumiere ne vous blesse plus mais vous soigne (coeff de -1), en contrepartie le coefficient de degats d''ombre est doublé','Fidele de la lumiere','general affiliation saisho'),
('Partage','Vous permet d''avoir une autre affiliation en parallele compatible avec celle-ci. Cependant 3 effets d''affiliation au choix ne seront plus pris en compte','Fidele de la lumiere','general affiliation saisho'),
('Hierarchie','Bonus/Malus pour convaincre (charisme) un autre militaire en fonction de votre (ancien) grade et de celui du PNJ','Militaire','human affiliation militaire'),
('Survivaliste','+10% pour survivre en pleine nature, loin de toute civilisation','Militaire','human affiliation militaire'),
('Macgyver','+10% pour fabriquer en urgence un dispositif quelconque','Ingenieur','human affiliation ingenieur'),
('Expertise','+10% dans l''analyse scientifique','Ingenieur','human affiliation ingenieur'),
('Baron du crime','les non-mafieux avec qui vous traitez se mefient de vous','Mafieux','human affiliation mafieux'),
('Qui peux le moins peux le plus','+10% en negociation unilaterale','Mafieux','human affiliation mafieux'),
('Faire ses preuves','les autres trafiquants perdent facilement confiance en vous en cas d''echec de votre part','Mafieux','human affiliation mafieux'),
('Mafieux un jour mafieux toujours','Si vous quittez le milieu de la mafia, les autres mafieux voudront vous traquer voir vous eliminer','Mafieux','human affiliation mafieux'),
('Benefice naturel','+10% pour vendre legerement plus cher un objet et pour acheter legerement moins cher un objet','Marchand','human affiliation marchand'),
('Commission','Recevez +10% de comission si vous etes impliquez dans une negociation faisant gagner de l''argent','Marchand','human affiliation marchand'),
('L''argent a une odeur','+2 en intuition pour trouver de l''argent','Marchand','human affiliation marchand'),
('Boycott','Si vous arretez d''etre marchand, la communaute marchande vous boycottera','Marchand','human affiliation marchand'),
('Parlementaire','vous pouvez sieger au parlement de Sanctum','Umbrinis','elem affiliation umbrinis'),
('Patriote','+10% pour rallier des elementaire a votre cause lorsque vous defendez les valeurs de votre pays','Umbrinis','elem affiliation umbrinis'),
('Inquisiteur','vous etes legalement autorise par votre pays a chasser les heretiques venerant des divinites paiennes','Faeliath','elem affiliation faeliath'),
('Endurance de Spatia','vos prieres envers Spatia regenerent vos PM proportionnellement','Faeliath','elem affiliation faeliath'),
('Protection divine','vous regenerez lentement vos PV et le bonus d''endurance de Spatia est augmente si vous priez dans une eglise qui lui est dediee','Faeliath','elem affiliation faeliath'),
('Transcendance de Spatia','si la deesse Spatia reconnait votre devouement, elle vous octroiera au hasard un effet suivant (1d4) :\n1. Bielementarisation\n2. Competence divine\n3. Messie\n4. Benediction','Faeliath','elem affiliation faeliath'),
('Transcendance bielementarisation','vous obtenez la capacite de manier un second element sauf si vous en etes deja capable','Faeliath Transcendance','none'),
('Transcendance competence divine','vous obtenez une competence bonus quelque soit votre niveau','Faeliath Transcendance','none'),
('Transcendance messie','vous etes desormais capable de convertir temporairement vos PM en bonus de PV max pour tout les autres fideles de Spatia a proximite. Vous pouvez recuperer vos PM a tout moment, annulant alors le bonus','Faeliath Transcendance','none'),
('Transcendance benediction','Spatia benit un de vos objet fetiche, celui-ci passe ainsi au rang d''Artefact','Faeliath Transcendance','none'),
('Business is business','+10% en negociation en affaire','Okane','elem affiliation okane'),
('Comission','Recevez +15% de comission si vous etes impliquez dans une negociation faisant gagner de l''argent','Okane','elem affiliation okane'),
('Experimentation','+5% en experimentation pour la recherche','Guilde du Savoir','elem affiliation gsavoir'),
('Savoir','+5% en analyse de magie','Guilde du Savoir','elem affiliation gsavoir'),
('Hors la loi','votre affiliation est consideree comme hors la loi partout dans le monde. Si on la decouvre, vous serez traque et arrete','Onilord','onikaosu succube affiliation onilord'),
('La loi du plus fort','vous devez obeissance aux plus fort que vous au sein de l''ordre et inversement aupres des plus faibles que vous','Onilord','onikaosu succube affiliation onilord'),
('Force accrue','+5% en force naturellement','Onilord','onikaosu succube affiliation onilord'),
('Experimentation','+10% en experimentation pour la recherche','Kuroni','onikaosu succube affiliation kuroni'),
('Savoir noir','+10% en analyse de magie noire','Kuroni','onikaosu succube affiliation kuroni'),
('Sagesse','+5% en esprit naturellement','Kuroni','onikaosu succube affiliation kuroni'),
('Asile','les pays controles par l''ordre Kibou vous accueilleront en cas de problement sauf si vous etes considere comme un criminel','Kibou','onikaosu succube affiliation kibou'),
('Courage','la peur ne vous connait pas, meme en danger de mort','Kibou','onikaosu succube affiliation kibou'),
('Influence','+5% en charisme naturellement','Kibou','onikaosu succube affiliation kibou'),
('L''amour pas la guerre','aider les gens avec vos pouvoirs vous permet d''avoir un bonus de 10% en chance et 5% en charisme. si vous tuez deliberement une personne ou contribuez deliberement a sa mort, ces bonus seront perdus definitivement et vous obtiendrez un malus de 10% en chance','Disciple de Vitalia','mgirl affiliation vitalia'),
('Guerison mentale','+5% en charisme pour tenter de liberer une cible d''un controle mental avec un beau discours','Disciple de Vitalia','mgirl affiliation vitalia'),
('Miracle de la vie','soins emis accrus de 10%','Disciple de Vitalia','mgirl affiliation vitalia'),
('Regime de la terreur','inspire la crainte aux autres magical girl non affiliees','Grand guerrier','mgirl affiliation grdguerriere'),
('Victimisation','la violence augmente votre force de 10% tant que vous le restez. Le bonus s''annule egalement si vous prenez une raclee','Grand guerrier','mgirl affiliation grdguerriere'),
('Devoir senatorial','vous avez votre place au senat et devez y sieger regulierement en fonction de l''importance de la convocation de l''assemblee','Senateur','mgirl affiliation senateur'),
('L''union fait le charisme','lors de negociations, pour chaque magical girl dans votre groupe en accord avec vous, elles et vous obtiennent un bonus de 5x% jusqu''a un maximum de 20%','Senateur','mgirl affiliation senateur'),
('Si vis pacem para bellum','+10% pour negocier la paix','Sunien','ningemono affiliation sunien'),
('Heraut de guerre','Les Sunien sont pacifiques. Tout les autres Ningemono leur vouent un respect absolu','Sunien','ningemono affiliation sunien'),
('Tribu','+10% sur toute action d''opportunite pour porter assistance a un autre Ningemono en danger et ayant la meme affiliation que vous','Unien','ningemono affiliation unien'),
('High-tech','connaissances en mecanique Machina accrues, +5% sur les competences et jet en relation avec celle-ci','Unien','ningemono affiliation unien'),
('Embuscade','+10% sur les actions d''opportunites avec effet de surprise','Rebelle','ningemono affiliation rebelle'),
('Camouflage','+5% pour fuir ou se cacher dans la nature (hors zones degagees)','Rebelle','ningemono affiliation rebelle'),
('Ni vu ni connu jt''embrouille','+5% pour tenter d''arnaquer quelqu''un','Rebelle','ningemono affiliation rebelle'),
('Reseau generalise de partage de directives','vous recevez et pouvez transmettre vos evaluations personnelles pour ajouter des directives generales que vous pouvez suivre ou non','ROOT','machina affiliation root'),
('Hardware','+10% en mecanique','ROOT','machina affiliation root'),
('Software','+10% en programmation','ROOT','machina affiliation root'),
('Hacker','+5% pour pirater un systeme technologique','Assassin/Criminel','machina affiliation assassin'),
('Tir chirurgical','+5% sur les tirs a tres longue distance','Assassin/Criminel','machina affiliation assassin'),
('Wanna cry','+5% en conception de virus informatique','Assassin/Criminel','machina affiliation assassin'),
('Ma foi pas de foi sans foie','Impossible de faire partie d''une religion et donc de choisir une affiliation en lien avec la religon','Machina','machina');

DO $$
<<rulesupdate>>
DECLARE
  sk RECORD;
	idsk Skills.id_skill%TYPE;
BEGIN
	-- Elementaire
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Elementaire' ORDER BY id_skill LIMIT 2) LOOP
		INSERT INTO RaceSkills
		VALUES (2, sk.id_skill);
	END LOOP;
	-- Onikaosu
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Onikaosu' ORDER BY id_skill LIMIT 3) LOOP
		INSERT INTO RaceSkills
		VALUES (3, sk.id_skill);
	END LOOP;
	-- Succube
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Succube' ORDER BY id_skill LIMIT 4) LOOP
		INSERT INTO RaceSkills
		VALUES (4, sk.id_skill);
	END LOOP;
	-- Magical Girl
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Magical Girl' ORDER BY id_skill LIMIT 4) LOOP
		INSERT INTO RaceSkills
		VALUES (5, sk.id_skill);
	END LOOP;
	-- Gardien
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Gardien' ORDER BY id_skill LIMIT 3) LOOP
		INSERT INTO RaceSkills
		VALUES (6, sk.id_skill);
	END LOOP;
	-- Ningemono
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Ningemono' ORDER BY id_skill LIMIT 3) LOOP
		INSERT INTO RaceSkills
		VALUES (7, sk.id_skill);
	END LOOP;
	-- Machina
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Machina' ORDER BY id_skill LIMIT 5) LOOP
		INSERT INTO RaceSkills
		VALUES (8, sk.id_skill);
	END LOOP;
	SELECT id_skill INTO idsk FROM Skills WHERE nom = 'Ma foi pas de foi sans foie';
	INSERT INTO RaceSkills VALUES (8, idsk);
	-- Polymorphe
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Polymorphe') LOOP
		INSERT INTO RaceSkills
		VALUES (9, sk.id_skill);
	END LOOP;
  RAISE NOTICE 'RaceSkills table updated';
	-- Fidele de la lumiere
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Fidele de la lumiere') LOOP
		INSERT INTO OrgSkills
		VALUES (1, sk.id_skill);
	END LOOP;
	-- Militaire
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Militaire') LOOP
		INSERT INTO OrgSkills
		VALUES (2, sk.id_skill);
	END LOOP;
	-- Ingenieur
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Ingenieur') LOOP
		INSERT INTO OrgSkills
		VALUES (3, sk.id_skill);
	END LOOP;
	-- Mafieux
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Mafieux') LOOP
		INSERT INTO OrgSkills
		VALUES (4, sk.id_skill);
	END LOOP;
	-- Marchand
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Marchand') LOOP
		INSERT INTO OrgSkills
		VALUES (5, sk.id_skill);
	END LOOP;
	-- Umbrinis
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Umbrinis') LOOP
		INSERT INTO OrgSkills
		VALUES (6, sk.id_skill);
	END LOOP;
	-- Faeliath
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Faeliath') LOOP
		INSERT INTO OrgSkills
		VALUES (7, sk.id_skill);
	END LOOP;
	-- Okane
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Okane') LOOP
		INSERT INTO OrgSkills
		VALUES (8, sk.id_skill);
	END LOOP;
	-- Guilde du savoir
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Guilde du Savoir') LOOP
		INSERT INTO OrgSkills
		VALUES (9, sk.id_skill);
	END LOOP;
	-- Onilord
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Onilord') LOOP
		INSERT INTO OrgSkills
		VALUES (10, sk.id_skill);
	END LOOP;
	-- Kuroni
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Kuroni') LOOP
		INSERT INTO OrgSkills
		VALUES (11, sk.id_skill);
	END LOOP;
	-- Kibou
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Kibou') LOOP
		INSERT INTO OrgSkills
		VALUES (12, sk.id_skill);
	END LOOP;
	-- Disciple de Vitalia
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Disciple de Vitalia') LOOP
		INSERT INTO OrgSkills
		VALUES (13, sk.id_skill);
	END LOOP;
	-- Grand guerrier
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Grand guerrier') LOOP
		INSERT INTO OrgSkills
		VALUES (14, sk.id_skill);
	END LOOP;
	-- Senateur
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Senateur') LOOP
		INSERT INTO OrgSkills
		VALUES (15, sk.id_skill);
	END LOOP;
	-- Sunien
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Sunien') LOOP
		INSERT INTO OrgSkills
		VALUES (16, sk.id_skill);
	END LOOP;
	-- Unien
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Unien') LOOP
		INSERT INTO OrgSkills
		VALUES (17, sk.id_skill);
	END LOOP;
	-- Rebelle
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Rebelle') LOOP
		INSERT INTO OrgSkills
		VALUES (18, sk.id_skill);
	END LOOP;
	-- ROOT
	FOR sk IN (SELECT id_skill FROM Skills WHERE nom = 'Reseau generalise de partage de directives') LOOP
		INSERT INTO OrgSkills
		VALUES (19, sk.id_skill);
	END LOOP;
	-- Assassin/Criminel
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Assassin/Criminel') LOOP
		INSERT INTO OrgSkills
		VALUES (20, sk.id_skill);
	END LOOP;
	RAISE NOTICE 'OrgSkills table updated';
END rulesupdate $$;


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
	sk RECORD;
BEGIN
	SELECT COUNT(*) INTO nbr FROM Organizations
	WHERE (nom = org);
	IF nbr > 0 OR org = NULL THEN
		SELECT id_org INTO orgid FROM Organizations
		WHERE (nom = org);
		UPDATE Characterr
		SET affiliated_with = orgid
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
		IF org IS NOT NULL THEN
			FOR sk IN (SELECT * FROM get_orgskills(org)) LOOP
				PERFORM assign_skill(dbkey,idserv,idchan,sk.id_skill);
			END LOOP;
		END IF;
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

CREATE OR REPLACE FUNCTION jdrcopy
(
	idserv JDR.id_server%TYPE,
	src JDR.id_channel%TYPE,
	dest JDR.id_channel%TYPE
) RETURNS void AS $$
DECLARE
	nbr INT;
	mj Membre.id_member%TYPE;
	line RECORD;
	inv inventaire.id_inventory%TYPE;
BEGIN
	SELECT COUNT(*) INTO nbr FROM JDR
	WHERE (id_server = idserv AND id_channel = dest);
	IF nbr <> 0 THEN
		PERFORM jdrdelete(idserv,dest);
	END IF;
	SELECT id_member INTO mj FROM JDR
	WHERE (id_server = idserv AND id_channel = src);
	PERFORM jdrcreate(idserv,dest,mj);
	FOR line IN (SELECT * FROM Characterr WHERE id_server = idserv AND id_channel = src) LOOP
		INSERT INTO inventaire (charkey)
		VALUES (line.charkey);
		SELECT MAX(id_inventory) INTO inv FROM inventaire
		WHERE charkey = line.charkey;
		--update here
		INSERT INTO Characterr
		VALUES (line.charkey, line.nom, line.lore, line.lvl, line.PV, line.PVmax, line.PM, line.PMmax, line.strength, line.spirit, line.charisma, line.agility, line.karma, line.defaultkarma, line.argent, line.light_points, line.dark_points, line.intuition, line.mental, line.rolled_dice, line.succes, line.fail, line.critic_success, line.critic_fail, line.super_critic_success, line.super_critic_fail, idserv, dest, line.gm, line.gm_default, inv, line.id_member, line.dead, line.classe, line.linked, line.xp, line.prec, line.luck, line.affiliated_with);
		--end of update
	END LOOP;
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
