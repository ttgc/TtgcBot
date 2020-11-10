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
ALTER TABLE public.Organizations ADD COLUMN hidden BOOLEAN CONSTRAINT organization_hidden_notnull NOT NULL CONSTRAINT organization_hidden_default DEFAULT false;
ALTER TABLE public.Race ADD COLUMN id_extension INT;
UPDATE Skills SET id_extension = (SELECT id_extension FROM Extensions WHERE universe = 'Cosmorigins' AND world = 'Terae');
UPDATE Organizations SET id_extension = (SELECT id_extension FROM Extensions WHERE universe = 'Cosmorigins' AND world = 'Terae'), hidden = false;
UPDATE Organizations SET hidden = true WHERE nom = 'Onilord';
UPDATE Race SET id_extension = (SELECT id_extension FROM Extensions WHERE universe = 'Cosmorigins' AND world = 'Terae');
ALTER TABLE public.Skills ADD CONSTRAINT FK_skills_id_ext FOREIGN KEY (id_extension) REFERENCES public.Extensions(id_extension);
ALTER TABLE public.Organizations ADD CONSTRAINT FK_organization_id_ext FOREIGN KEY (id_extension) REFERENCES public.Extensions(id_extension);
ALTER TABLE public.Race ADD CONSTRAINT FK_race_id_ext FOREIGN KEY (id_extension) REFERENCES public.Extensions(id_extension);


-- Add race, class, symbionts, organizations, and skills for Orianis
DO $$
<<orianisupdate>>
DECLARE
	terae Extensions.id_extension%TYPE;
	orianis Extensions.id_extension%TYPE;
	idr Race.id_race%TYPE;
	sk RECORD;
BEGIN
	SELECT id_extension INTO terae FROM Extensions WHERE universe = 'Cosmorigins' AND world = 'Terae';
	SELECT id_extension INTO orianis FROM Extensions WHERE universe = 'Cosmorigins' AND world = 'Orianis';
	-- Race
	INSERT INTO Race (nom, id_extension) VALUES
	('Grits', orianis), ('Alfys', orianis), ('Nyfis', orianis), ('Darfys', orianis), ('Zyrfis', orianis),
	('Idylis', orianis), ('Lythis', orianis), ('Itys', orianis), ('Alwenys', orianis), ('Vampyris', orianis),
	('Undefined', NULL);
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
	INSERT INTO Organizations(nom, id_extension) VALUES
	('Espion', orianis), ('Religieux', orianis), ('Federation du commerce', orianis), ('Scientifique', orianis),
	('Contrebandier', orianis), ('Militaire', orianis), ('Bureaucrate', orianis);
	RAISE NOTICE 'Inserts in Organizations completed';
	-- Skills
	INSERT INTO Skills(nom, description, origine, webclass, id_extension) VALUES
	('Sniper','Si le personnage passe son tour a viser sans se deplacer, il obtient un bonus de 10% en precision','Nigemono Umahin','ningemono umahin',terae);
	('Mecano','Autorise et octroie +10% en mecanique (force)','General','general',orianis),
	('Negociateur','+5% en negociation (charisme)','General','general',orianis),
	('Charmeur','+5% en seduction (charisme)','General','general',orianis),
	('Astropilote','Autorise le pilotage astral (pilotage)','General','general',orianis),
	('Ambianceur','+10% pour detendre l''atmosphere (augmente egalement l''impact de l''action)','General','general',orianis),
	('Scientifique','+5% sur les jets impactant la science (esprit)','General','general',orianis),
	('Chanceux','Double le nombre de points de karma gagne / perdu','General','general',orianis),
	('Interstellaire','Le pilote sait utiliser la technologie du WarpDrive (requiert Astropilote)','General','general',orianis),
	('Ingenieux','+5% en conception et analyse de technologie','Grits','grits',orianis),
	('Techno-specialite','specialisation dans une technologie au choix. +10% dans l''utilisation, l''analyse et la conception dans ce domaine','Grits','grits',orianis),
	('Science infuse','+20% dans les jets de connaissance scientifiques','Grits','grits',orianis),
	('Armement adaptatif','Capable de manier n''importe quelle arme avancee sans entrainement','Grits Techno-guerrier','grits technoguerrier',orianis),
	('Impenetrable','Reduit les degats physiques de 10 points','Grits Techno-guerrier','grits technoguerrier',orianis),
	('Electronicien','+10% en electronique','Grits Technomancien','grits technomancien',orianis),
	('Ingenieur numerique','+10% en informatique','Grits Technomancien','grits technomancien',orianis),
	('Post-mortem','Permet de transferer l''esprit a la mort du personnage dans un Itys','Grits Transhumain','grits transhumain',orianis),
	('Retrocompatibilite','Permet d''augmenter la force ou l''agilite de 10% contre un malus de 20% dans l''autre pendant une courte periode','Grits Transhumain','grits transhumain',orianis),
	('Nyctalope','Encore une fois, cela permet de voir dans le noir','Alfys','alfys',orianis),
	('Diplomate','Mode de combat par defaut en defensif','Alfys','alfys',orianis),
	('Dexterite','+10% en esquive (agilite)','Alfys','alfys',orianis),
	('Orateur','+5% pour convaincre d''autres personnes (charisme)','Alfys','alfys',orianis),
	('Telepathie','Permet de communiquer par telepathie avec n''importe quelle cible consentante a proximite','Alfys','alfys',orianis),
	('Influence','+10% pour influencer une decision (charisme)','Alfys Imperialfys','alfys imperialfys',orianis),
	('Leader','Octroie +5% de reussite a un allie qui obeit a une de vos directives','Alfys Imperialfys','alfys imperialfys',orianis),
	('Sniper','+10% sur les tirs a longue distance','Alfys Sacralfys','alfys sacralfys',orianis),
	('Energie stellaire','Permet de se concentrer un tour par combat avec vue sur le ciel directe pour recuperer 5d20 PM','Alfys Sacralfys','alfys sacralfys',orianis),
	('Archer d''elite','+5% en tir a l''arc (precision)','Alfys Sacralfys','alfys sacralfys',orianis),
	('Petite taille','Ne depasse pas les 1m20','Nyfis','nyfis',orianis),
	('La Bibine','Ne resiste pas a boire un petit coup de n''importe quelle biere. Octroie 20% de resistance a l''alcool supplementaire','Nyfis','nyfis',orianis),
	('Marchand de tapis','+10% pour negocier des rabais sur un achat (charisme)','Nyfis','nyfis',orianis),
	('Avarice','Obtient +10% sur les loot monetaires','Nyfis','nyfis',orianis),
	('Artisan','Autorise et octroie +10% en artisanat (force)','Nyfis','nyfis',orianis),
	('Expertise','+20% pour expertiser un objet (esprit)','Nyfis Negociateur','nyfis negociateur',orianis),
	('Marchandage','+5% pour negocier (charisme)','Nyfis Negociateur','nyfis negociateur',orianis),
	('Equite unidirectionnelle','Obtient une prime monetaire de 10% sur les recompenses de quetes','Nyfis Negociateur','nyfis negociateur',orianis),
	('Intimidation','+10% pour intimider (charisme)','Nyfis Bagarreur','nyfis bagarreur',orianis),
	('Provocation','+10% sur la premiere attaque pour declencher une rixe (force)','Nyfis Bagarreur','nyfis bagarreur',orianis),
	('Teigneux','Permet de riposter aux attaques physiques au corps a corps avec une autre attaque de base (hors competences) en mode offensif','Nyfis Bagarreur','nyfis bagarreur',orianis),
	('Sens de l''orientation','Permet de retrouver son chemin facilement via un jet d''intuition reussi','Nyfis Explorateur','nyfis explorateur',orianis),
	('Pilote aguerri','+2 en score de pilotage planetaire et astral','Nyfis Explorateur','nyfis explorateur',orianis),
	('Gardien de l''ombre','Lorsque expose a la lumiere, diminue les chances de reussite de 10%','Darfys','darfys',orianis),
	('Nyctalope','Encore une fois, cela permet de voir dans le noir','Darfys','darfys',orianis),
	('Reactivite','+10% en esquive (agilite)','Darfys','darfys',orianis),
	('Opportuniste','+10% sur les attaques d''opportunites','Darfys','darfys',orianis),
	('Obscurite totale','L''ombre n''inflige plus aucun degats, contrairement aux degats de la lumiere qui sont doubles. La lumiere du jour brule egalement la chaire exposee','Darfys','darfys',orianis),
	('Armement adaptatif','Permet de produire une lame a partir de nanites contre un certain cout en PM. La lame se desintegre lorsqu''elle est lachee','Darfys Assassin','darfys assassin',orianis),
	('Infiltre','+10% en infiltration','Darfys Assassin','darfys assassin',orianis),
	('Joueur de pipeau','+10% pour duper ou arnaquer son interlocuteur (charisme)','Darfys Roublard','darfys roublard',orianis),
	('Improvisation','+10% pour improviser une action en situation de stress','Darfys Roublard','darfys roublard',orianis),
	('Nyctalope','Encore une fois, cela permet de voir dans le noir','Zyrfis','zyrfis',orianis),
	('Dissuasion','+10% pour dissuader une cible d''attaquer le groupe (charisme)','Zyrfis','zyrfis',orianis),
	('Rayonnement toxique','Les attaques de lumiere inflige deux fois plus de degats mais les degats d''ombres sont reduits de moitie','Zyrfis','zyrfis',orianis),
	('Maitre d''arme','Capable de manier n''importe quelle arme sans entrainement','Zyrfis','zyrfis',orianis),
	('Blindage corporel','Reduit les degats subits de 10 points','Zyrfis','zyrfis',orianis),
	('Reactivite','+10% en parade (force)','Zyrfis','zyrfis',orianis),
	('Berserker','En dessous de 100 PV, permet de declencher la posture de combat Berserker :\nEsquive impossible\nDegats superieur au mode offensif\n+10 pts de degats subits\n1 parade par tour\nRiposte simple (pas de competence) en cas de parade reussie','Zyrfis','zyrfis',orianis),
	('Force superieure','Augmente les degats infliges contre les cibles technologiques ou equipees d''armures technologiques','Zyrfis Guerrier Ancestral','zyrfis ancestral',orianis),
	('Blocage magique','Permet de parer certaines attaques magiques (mode defensif ou berserker uniquement)','Zyrfis Guerrier Ancestral','zyrfis ancestral',orianis),
	('Technologie superieure','Augmente les degats infliges contre les cibles biologiques et non equipes d''armures technologiques','Zyrfis Neo-guerrier','zyrfis neoguerrier',orianis),
	('Ambidextrie','Permet d''utiliser deux armes a une main lors d''une seule attaque de base','Zyrfis Neo-guerrier','zyrfis neoguerrier',orianis),
	('Sang froid','Reduit le stress lors du pilotage. Le niveau d''augmentation de difficulte max passe de +2 a +1','Zyrfis Guerrier Armageddon','zyrfis armageddon',orianis),
	('Dernier souffle','Permet de rester conscient a 0 PV. Entre -100 et 0 PV, vous restez egalement conscient pendant 1 tour supplementaire avant de vous effondrer','Zyrfis Guerrier Armageddon','zyrfis armageddon',orianis),
	('Amphibie','Permet de respirer sous l''eau','Idylis','idylis',orianis),
	('Hydrophile','Beneficie des forces et faiblesses elementaires liees a l''eau','Idylis','idylis',orianis),
	('Maladresse','-10% en agilite pour toute action en dehors de l''eau','Idylis','idylis',orianis),
	('Crawl','Ne possede aucun malus lie a une immersion totale dans l''eau','Idylis','idylis',orianis),
	('Beaute de la nature','+10% en seduction (charisme)','Idylis','idylis',orianis),
	('Vision aquatique','Permet de voir sous l''eau meme sans source de lumiere a proximite','Idylis','idylis',orianis),
	('Dos crawle','Obtient un bonus de deplacement de +2 dans l''eau','Idylis','idylis',orianis),
	('Hydro-regen','Regenere des PV regulierement en etant dans l''eau (10 PV / tour)','Idylis','idylis',orianis),
	('Hydro-purge','En etant dans l''eau, reduit de moitie la duree de tous les effets nefastes et entravants qui ne sont pas lies a une faiblesse elementaire de l''eau','Idylis','idylis',orianis),
	('Peau rocheuse','Les degats physiques subits sont reduits de 20 points','Lithys','Lithys',orianis),
	('Exhibitionniste','Porter des vetements (ou armures) est un deshonneur pour vous','Lithys','Lithys',orianis),
	('Erosion','Beneficie des forces et faiblesses elementaires liees a la terre','Lithys','Lithys',orianis),
	('Maboule','Permet de se mettre en boule ou de sortir de cette forme au debut de votre tour. En boule, vous devenez incapable d''agir ou parer','Lythis','lythis',orianis),
	('Technophobe','Ne peut utiliser aucun outil technologique','Lithys','Lithys',orianis),
	('Solide comme un roc','Les degats physique subits sont reduits de 50%','Lithys','Lithys',orianis),
	('Blocage','+10% en parade','Lithys','Lithys',orianis),
	('Bouboule','En boule, octroie une reduction de 25% supplementaire contre les degats physiques subits','Lithys','Lithys',orianis),
	('Roule ma poule','En boule, octroie +2 de deplacement','Lithys','Lithys',orianis),
	('Initiative','Si vous n''avez pas encore agis ce tour-ci, permet d''intervenir pour tenter de parer ou encaisser une attaque contre une cible a proximite. Apres cette intervention, vous agissez immediatement','Lithys','Lithys',orianis),
	('Intelligence artificielle','Les Itys sont incapable de faire appel a l''intuition, en contre-partie leur intelligence est bien plus developpee (esprit)','Itys','Itys',orianis),
	('Corps metallique','Les robots ne possedent pas de sang et son insensible a la douleur','Itys','Itys',orianis),
	('Ma foi pas de foi sans foie','Impossible de faire partie d''une religion ou de choisir une affiliation en lien avec celle-ci','Itys','Itys',orianis),
	('Mental d''acier','Ne possede pas de sante mentale','Itys','Itys',orianis),
	('Non-organique','Interdit la creation de races transgenique et symbiotique a partir des Itys','Itys','Itys',orianis),
	('Relax','Les Itys ne ressentent pas le stress','Itys','Itys',orianis),
	('Interprete','Permet de dechiffrer et de traduire n''importe quel langage alien evolue','Itys','Itys',orianis),
	('Communication sans fil','Permet de communiquer a la vitesse de la lumiere avec d''autres Itys peu importe la distance','Itys','Itys',orianis),
	('Pare-feu','Bloque la plupart des intrusions informatiques et des malwares','Itys','Itys',orianis),
	('Intrusion','+10% pour pirater un systeme informatique ou concevoir un malware','Itys','Itys',orianis),
	('Auto-reparation','Permet de se reparer automatiquement, octroyant la regeneration naturelle de PV','Itys','Itys',orianis),
	('Phytotherapie','Beneficie des forces et faiblesses elementaires liees aux plantes','Alwenys','alwenys',orianis),
	('Contre nature','Limite l''utilisation de technologie au strict necessaire','Alwenys','alwenys',orianis),
	('Xenophobie','-10% pour negocier avec des representants d''autres especes (charisme)','Alwenys','alwenys',orianis),
	('Camouflage','+10% en camouflage dans la nature','Alwenys','alwenys',orianis),
	('Enracinement','Permet de s''enraciner au bout d''un tour sans aucun deplacement effecute. L''enracinement retire la possibilite de se deplacer mais augmente la precision de 5% ainsi que les degats infliges','Alwenys','alwenys',orianis),
	('Herboriste','+10% en jet de connaissance sur la nature (esprit)','Alwenys','alwenys',orianis),
	('Bio-toxine','Le sang du personnage contient une toxine empoisonant tout ceux qui entrent en contact avec','Alwenys','alwenys',orianis),
	('Immunite biologique','Rend insensible aux maladies et aux poisons naturels','Alwenys','alwenys',orianis),
	('Plantes medicinales','Augmente l''efficacite des soins emis de 10%','Alwenys','alwenys',orianis),
	('Surcroissance','Les attaques d''eau recues soignent le personnage (coeff -1), mais les attaques de feu sont doublees (coeff total de 4)','Alwenys','alwenys',orianis),
	('Sanguinaire','Boire du sang est un besoin vital quotidien','Vampyris','vampyris',orianis),
	('Nyctalope','Encore une fois, cela permet de voir dans le noir','Vampyris','vampyris',orianis),
	('Vol','Permet de voler librement a basse altitude','Vampyris','vampyris',orianis),
	('Creature de l''ombre','La lumiere en trop grande quantite brule la chaire et annule l''effet des autres talents. Les degats de lumieres subits sont egalement doubles','Vampyris','vampyris',orianis),
	('Acier brulant','Les degats de metal contre les Vampyris sont doubles et brulent leur cible','Vampyris','vampyris',orianis),
	('Vitalite sanglante','Boire du sang regenere les PV','Vampyris','vampyris',orianis),
	('Energie sanglante','Boire du sang regenere les PM','Vampyris','vampyris',orianis),
	('Vampirisme','Blesser une cible regenere 10% des degats infliges','Vampyris','vampyris',orianis),
	('Appropriation','Boire le sang d''une cible permet de s''approprier temporairement un de ses talents (non cumulable)','Vampyris','vampyris',orianis),
	('Chauve-souris','Permetde se transformer en chauve-souris a volonte. En chauve-souris vous obtenez :\n+30% en agilite\nReussite critique ou super-critique uniquement en force','Vampyris','vampyris',orianis),
	('Poids plume','Augmente le poids max de l''inventaire de 50%','Vampyris','vampyris',orianis);
	RAISE NOTICE 'Inserts in Skills completed';
	-- RaceSkills
	SELECT id_race INTO idr FROM Race WHERE nom = 'Grits' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Grits' ORDER BY id_skill LIMIT 1) LOOP
		INSERT INTO RaceSkills VALUES (idr, sk.id_skill);
	END LOOP;
	SELECT id_race INTO idr FROM Race WHERE nom = 'Alfys' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Alfys' ORDER BY id_skill LIMIT 2) LOOP
		INSERT INTO RaceSkills VALUES (idr, sk.id_skill);
	END LOOP;
	SELECT id_race INTO idr FROM Race WHERE nom = 'Nyfis' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Nyfis' ORDER BY id_skill LIMIT 2) LOOP
		INSERT INTO RaceSkills VALUES (idr, sk.id_skill);
	END LOOP;
	SELECT id_race INTO idr FROM Race WHERE nom = 'Darfys' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Darfys' ORDER BY id_skill LIMIT 2) LOOP
		INSERT INTO RaceSkills VALUES (idr, sk.id_skill);
	END LOOP;
	SELECT id_race INTO idr FROM Race WHERE nom = 'Zyrfis' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Zyrfis' ORDER BY id_skill LIMIT 3) LOOP
		INSERT INTO RaceSkills VALUES (idr, sk.id_skill);
	END LOOP;
	SELECT id_race INTO idr FROM Race WHERE nom = 'Idylis' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Idylis' ORDER BY id_skill LIMIT 4) LOOP
		INSERT INTO RaceSkills VALUES (idr, sk.id_skill);
	END LOOP;
	SELECT id_race INTO idr FROM Race WHERE nom = 'Lithys' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Lithys' ORDER BY id_skill LIMIT 5) LOOP
		INSERT INTO RaceSkills VALUES (idr, sk.id_skill);
	END LOOP;
	SELECT id_race INTO idr FROM Race WHERE nom = 'Itys' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Itys' ORDER BY id_skill LIMIT 6) LOOP
		INSERT INTO RaceSkills VALUES (idr, sk.id_skill);
	END LOOP;
	SELECT id_race INTO idr FROM Race WHERE nom = 'Alwenys' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Alwenys' ORDER BY id_skill LIMIT 3) LOOP
		INSERT INTO RaceSkills VALUES (idr, sk.id_skill);
	END LOOP;
	SELECT id_race INTO idr FROM Race WHERE nom = 'Vampyris' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Vampyris' ORDER BY id_skill LIMIT 5) LOOP
		INSERT INTO RaceSkills VALUES (idr, sk.id_skill);
	END LOOP;
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

CREATE OR REPLACE FUNCTION get_raceskills
(
	racename Race.nom%TYPE
) RETURNS SETOF Skills AS $$
DECLARE
	raceid Race.id_race%TYPE;
BEGIN
	SELECT id_race INTO raceid FROM Race
	WHERE (nom = racename);
	--UPDATE HERE
	RETURN QUERY
	SELECT Skills.id_skill, nom, description, origine, webclass, id_extension FROM Skills
	INNER JOIN RaceSkills ON (Skills.id_skill = RaceSkills.id_skill)
	WHERE id_race = raceid;
	--UPDATE HERE
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
	--UPDATE HERE
	RETURN QUERY
	SELECT Skills.id_skill, nom, description, origine, webclass, id_extension FROM Skills
	INNER JOIN OrgSkills ON (Skills.id_skill = OrgSkills.id_skill)
	WHERE id_org = orgid;
	--UPDATE HERE
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_symbiontskills
(
	sb Symbiont.nom%TYPE
) RETURNS SETOF Skills AS $$
DECLARE
	sbid Symbiont.id_symbiont%TYPE;
BEGIN
	SELECT id_symbiont INTO sbid FROM Symbiont
	WHERE (nom = sb);
	RETURN QUERY
	SELECT Skills.id_skill, nom, description, origine, webclass, id_extension FROM Skills
	INNER JOIN SymbiontSkills ON (Skills.id_skill = SymbiontSkills.id_skill)
	WHERE id_symbiont = sbid;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_skill
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS SETOF skills AS $$
BEGIN
	--UPDATE HERE
	RETURN QUERY
	SELECT skills.id_skill,nom,description,origine,webclass,id_extension FROM skills
	INNER JOIN havingskill ON (skills.id_skill = havingskill.id_skill)
	WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	--END OF UPDATE
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION charhybrid
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	rc Race.id_race%TYPE
) RETURNS void AS $$
DECLARE
	sk RECORD;
BEGIN
	UPDATE characterr
	SET hybrid_race = rc
	WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	FOR sk IN (SELECT id_skill FROM RaceSkills WHERE id_race = rc) LOOP
		PERFORM assign_skill(dbkey, idserv, idchan, sk.id_skill);
	END LOOP;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION charsb
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	sb Symbiont.id_symbiont%TYPE
) RETURNS void AS $$
DECLARE
	prevsb Symbiont.id_symbiont%TYPE;
	sk RECORD;
BEGIN
	SELECT id_symbiont INTO prevsb FROM Characterr
	WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	IF prevsb <> NULL THEN
		DELETE FROM havingskill
		WHERE id_skill IN (SELECT id_skill FROM SymbiontSkills WHERE id_symbiont = prevsb);
	END IF;
	UPDATE characterr
	SET id_symbiont = sb
	WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	IF sb <> NULL THEN
		FOR sk IN (SELECT id_skill FROM SymbiontSkills WHERE id_symbiont = sb) LOOP
			PERFORM assign_skill(dbkey, idserv, idchan, sk.id_skill);
		END LOOP;
	END IF;
END;
$$ LANGUAGE plpgsql;
