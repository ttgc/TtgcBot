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
('Relance','une fois par combet l''hote ou le gardien peut relancer n''importe quel jet (hors critiques)','Gardien','guardian'),
('Disparition','peut disparaitre n''importe quand mais ne peut plus agir','Gardien','guardian'),
('Connexion telepathique','Permet de communique avec son hote','Gardien','guardian'),
('Creature harmonieuse','Karma compris entre -10 et -5 ou +5 et +10','Ningemono','ningemono'),
('Animalisation','Permet de faire apparaitre des caracteristiques propres de son animal (ailes, queue, crocs, etc.)','Ningemono','ningemono'),
('Instinct animal','Permet en cas de test sur 1d6 reussi d''agir par instinct (remplace intuition)','Ningemono','ningemono'),
('Forme animale','Bonus de transformation complete en animal :\n+2 instinct\nAjoute des bonus/malus a chaque stat en fonction de l''animal','Ningemono','ningemono'),
('Langage animal','Permet de parler la langue de l''animal complementaire','Ningemono','ningemono'),
('Nyctalope','Permet de voir dans le noir (naturel)','Ningemono Nekonya','ningemono nekonya'),
('Acrobate','+5% pour realiser des acrobaties','Ningemono Nekonya','ningemono nekonya'),
('Patte de velours','ne fait pas de bruit en se deplacant (+20% en discretion)','Ningemono Nekonya','ningemono nekonya'),
('Flair','permet de detecter et de suivre des odeurs particulieres','Ningemono Inuwan','ningemono inuwan'),
('Enrage','octroie un bonus de 5% en cas de jet d''instinct animal reussi face a une cible menacante pendant toute la duree du combat','Ningemono Inuwan','ningemono inuwan'),
('Chien de garde','peut faire peur aux cibles s''aprochant trop pres de ce qu''il protege ou de lui avec un jet de charisme +10% (une seule fois en debut de combat)','Ningemono Inuwan','ningemono inuwan'),
('Nyctalope','Permet de voir dans le noir (naturel)','Ningemono Okamiuooon','ningemono okamiuoon'),
('Flair','permet de detecter et de suivre des odeurs particulieres','Ningemono Okamiuooon','ningemono okamiuoon'),
('Meute','pousse un hurlement en debut de combat en cas de jet d''instinct reussi qui octroie +5% en force a tout ses allies et +10% aux allies okamiuoon','Ningemono Okamiuooon','ningemono okamiuoon'),
('Predateur','+10% pour chasser dans la nature','Ningemono Okamiuooon','ningemono okamiuoon'),
('Creature seduisante','+10% en charme et seduction','Ningemono Kitsunekon','ningemono kitsunekon'),
('Ruse','+10% pour induire quelqu''un en erreur','Ningemono Kitsunekon','ningemono kitsunekon'),
('Esprit detache','ne peut se faire controler mentalement','Ningemono Kitsunekon','ningemono kitsunekon'),
('Renard 9 queues','Octroie les avantages suivants :\n+5% a tout bonus / malus total affectant esprit/charisme\nUne cible charmee aura plus de mal a retrouver ses esprits (-20%)\nPeut visualiser les flux energetiques','Ningemono Kitsunekon','ningemono kitsunekon'),
('Vol','Peut voler dans les airs (naturel)','Ningemono Toripi','ningemono toripi'),
('Plumes tranchantes','les plumes sont en parties melangees avec de l''acier et peuvent etre lancees pour attaquer','Ningemono Toripi','ningemono toripi'),
('Vision lointaine','peut voir largement plus loin que la normale','Ningemono Toripi','ningemono toripi'),
('Portage','peut transporter de grosses proies dans ses serres','Ningemono Toripi','ningemono toripi'),
('Cri terrifiant','en debut de combat pousse un hurlement sur un jet de charisme pour terrifier les cibles proches','Ningemono Toripi','ningemono toripi'),
('Amphibie','peut respirer aussi bien sur terre que dans l''eau (naturel)','Ningemono Sakanakari','ningemono sakanakari'),
('Affinite aquatique','ne peut pas user de magie elementairement contradictoire avec l''eau (naturel)','Ningemono Sakanakari','ningemono sakanakari'),
('Nage olympique','nage beaucoup plus rapidement','Ningemono Sakanakari','ningemono sakanakari'),
('Chant melodieux','en chantant, permet de charmer certaines cibles en cas de jet de charisme +10% reussi','Ningemono Sakanakari','ningemono sakanakari'),
('Peau urticante','en cas de danger proche (jet d''instinct reussi) la peau devient urticante pendant toute la duree du cobmat','Ningemono Sakanakari','ningemono sakanakari'),
('Galop','deplacement augmente et plus rapide (x2 avec les regles de deplacement)','Ningemono Umahin','ningemono umahin'),
('Bus magique','permet de transporter maximum 2 personnes','Ningemono Umahin','ningemono umahin'),
('Fleches abondantes','permet de generer automatiquement des fleches classiques','Ningemono Umahin','ningemono umahin'),
('Morsure empoisonnee','les cibles mordues sont empoisonnees','Ningemono Hebishuru','ningemono hebishuru'),
('Poison violent','tout poison issue de competence est amplifie et provoque de violentes douleurs','Ningemono Hebishuru','ningemono hebishuru'),
('Antidote','insensible au poison','Ningemono Hebishuru','ningemono hebishuru'),
('Super saut','peut sauter deux fois plus haut','Ningemono Usagipyon','ningemono usagipyon'),
('Sonar','peut reperer des bruits sur de longues distances','Ningemono Usagipyon','ningemono usagipyon'),
('Patte de lapin','en cas d''echec (hors super-critique) le jet est relance (1 fois par combat)','Ningemono Usagipyon','ningemono usagipyon'),
('Peau epaisse','resistance aux blessures physiques et saignements accrue (-20 points de degats)','Ningemono Doragondraa','ningemono doragondraa'),
('Vision etendue','peut voir beaucoup plus loin et dispose aussi d''une vision thermique supplementaire','Ningemono Doragondraa','ningemono doragondraa'),
('Avidite','Obtient +10% d''or dans les loot qu''il ne vous pretera guere','Ningemono Doragondraa','ningemono doragondraa'),
('Consumation','Malediction qui rend incontrolable et engendre de lourdes consequences pouvant aller jusqu''a la mort definitive lorsque la sante mentale tombe en dessoud de 0','Ningemono Doragondraa','ningemono doragondraa'),
('Intelligence artificielle','les machina sont incapable de faire appel a l''intuition en contrepartie, leur esprit est bien plus developpe','Machina','machina'),
('Corps metallique','ne possede pas de sang et est insensible a la douleur','Machina','machina'),
('Psyche inexistante','les PM ne se rechargent pas naturellement, les capacites magiques sont limites et possede une insensibilite a certaines magies','Machina','machina'),
('Batterie','Consomme des PM pour fonctionner, a 0 PM le Machina ne peut plus agir','Machina','machina'),
('Mise en veille','Permet de se mettre en veille qui simule l''etat d''extinction de la machine','Machina','machina'),
('Runable','peut etre rune (1d4 slots)','Machina','machina'),
('Apparence alterable','peut changer son apparence a volonte mais consomme plus d''energie','Machina','machina'),
('Cloud','permet de stocker sur un serveur externe ses donnes completes pouvant etre restaures en cas de destruction du Machina','Machina','machina'),
('Communication sans fil','permet de communiquer avec d''autres machina peu importe la distance','Machina','machina'),
('Couteau suisse','peut transformer ses bras en diverses armes et outils','Machina Host','machina host'),
('Jetpack','peut voler grace a son jetpack (consomme plus d''energie)','Machina Host','machina host'),
('Bouclier deflecteur','peut faire apparaitre un bouclier a tout moment qui consomme des PM. Les degats se repercutent alors sur les PM au lieu des PV','Machina Host','machina host'),
('Multi coeur','peut transferer ses donnes dans un machina host a proximite','Machina Server','machina server'),
('Trucage','une fois par combat, un jet rate (hors super-critique) peut etre altere en retranchant 10 au score obtenu','Machina Server','machina server'),
('Base virale VPS','Bloque la plupart des malwares. Gare a l''annonce reguliere de sa mise a jour','Machina Server','machina server'),
('Sudo','permet d''emprunter un droit de ROOT parmi : Overclock, Multi-shell, apt-get, chown, rm -rf /*, loop','Machina Server','machina server'),
('Polymorphisme','peut changer a volonte d''apparence','Polymorphe','polymorphe'),
('Conservateur de pouvoir','des lors qu''il adopte l''apparence d''une race, il obtient certains pouvoirs fixes lies a cette race','Polymorphe','polymorphe');

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
	SELECT skills.id_skill,nom,description,origine,webclass FROM skills
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
	WHERE (lower(nom) = lower(name));
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

CREATE OR REPLACE FUNCTION charcreate
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	cl Classe.id_classe%TYPE
) RETURNS void AS $$
DECLARE
	inv inventaire.id_inventory%TYPE;
BEGIN
	INSERT INTO inventaire (charkey)
	VALUES (dbkey);
	SELECT MAX(id_inventory) INTO inv FROM inventaire
	WHERE charkey = dbkey;
	--update here
	INSERT INTO Characterr
	VALUES (dbkey, dbkey, '', 1, 1, 1, 1, 1, 50, 50, 50, 50, 0, 0, 0, 1, 1, 3, 100, 0, 0, 0, 0, 0, 0, 0, idserv, idchan, 'O', 'O', inv, 'NULL',false,cl);
	--end of update
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
