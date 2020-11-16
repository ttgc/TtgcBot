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
	ido Organizations.id_org%TYPE;
	ids Symbiont.id_symbiont%TYPE;
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
	INSERT INTO Organizations(nom, id_extension, hidden) VALUES
	('Espion', orianis, true), ('Religieux', orianis, false), ('Federation du commerce', orianis, false), ('Scientifique', orianis, false),
	('Contrebandier', orianis, false), ('Militaire', orianis, false), ('Bureaucrate', orianis, false);
	RAISE NOTICE 'Inserts in Organizations completed';
	-- Skills
	INSERT INTO Skills(nom, description, origine, webclass, id_extension) VALUES
	('Mental d''acier','Ne possede pas de sante mentale','Machina','machina',terae),
	('Sniper','Si le personnage passe son tour a viser sans se deplacer, il obtient un bonus de 10% en precision','Nigemono Umahin','ningemono umahin',terae),
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
	('Peau rocheuse','Les degats physiques subits sont reduits de 20 points','Lythis','lythis',orianis),
	('Exhibitionniste','Porter des vetements (ou armures) est un deshonneur pour vous','Lythis','lythis',orianis),
	('Erosion','Beneficie des forces et faiblesses elementaires liees a la terre','Lythis','lythis',orianis),
	('Maboule','Permet de se mettre en boule ou de sortir de cette forme au debut de votre tour. En boule, vous devenez incapable d''agir ou parer','Lythis','lythis',orianis),
	('Technophobe','Ne peut utiliser aucun outil technologique','Lythis','lythis',orianis),
	('Solide comme un roc','Les degats physique subits sont reduits de 50%','Lythis','lythis',orianis),
	('Blocage','+10% en parade','Lythis','lythis',orianis),
	('Bouboule','En boule, octroie une reduction de 25% supplementaire contre les degats physiques subits','Lythis','lythis',orianis),
	('Roule ma poule','En boule, octroie +2 de deplacement','Lythis','lythis',orianis),
	('Initiative','Si vous n''avez pas encore agis ce tour-ci, permet d''intervenir pour tenter de parer ou encaisser une attaque contre une cible a proximite. Apres cette intervention, vous agissez immediatement','Lythis','lythis',orianis),
	('Intelligence artificielle','Les Itys sont incapable de faire appel a l''intuition, en contre-partie leur intelligence est bien plus developpee (esprit)','Itys','Itys',orianis),
	('Corps metallique','Les robots ne possedent pas de sang et son insensible a la douleur','Itys','itys',orianis),
	('Ma foi pas de foi sans foie','Impossible de faire partie d''une religion ou de choisir une affiliation en lien avec celle-ci','Itys','itys',orianis),
	('Mental d''acier','Ne possede pas de sante mentale','Itys','itys',orianis),
	('Non-organique','Interdit la creation de races transgenique et symbiotique a partir des Itys','Itys','itys',orianis),
	('Relax','Les Itys ne ressentent pas le stress','Itys','itys',orianis),
	('Interprete','Permet de dechiffrer et de traduire n''importe quel langage alien evolue','Itys','itys',orianis),
	('Communication sans fil','Permet de communiquer a la vitesse de la lumiere avec d''autres Itys peu importe la distance','Itys','itys',orianis),
	('Pare-feu','Bloque la plupart des intrusions informatiques et des malwares','Itys','itys',orianis),
	('Intrusion','+10% pour pirater un systeme informatique ou concevoir un malware','Itys','itys',orianis),
	('Auto-reparation','Permet de se reparer automatiquement, octroyant la regeneration naturelle de PV','Itys','itys',orianis),
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
	('Poids plume','Augmente le poids max de l''inventaire de 50%','Vampyris','vampyris',orianis),
	('Regeneration','Le corps de l''hote se regenere de 20 PV / tour en permanence et les blessures se referment plus rapidement','Azort','symbiont azort',orianis),
	('Increvable','meme a moins de 0 PV, le corps se regenere et l''hote peut continuer a agir, cependant cela impact sa sante mentale','Azort','symbiont azort',orianis),
	('Force dementielle','chaque reussite critique en force octroie 1 point de force definitif et les super-critiques en octroient 2','Azort','symbiont azort',orianis),
	('Adaptabilite','L''hote est protege de toutes les variations climatique et d''environnement. Un temps d''adaptation est cependandant necessaire pour s''acclimater a un nouvel environnement','Iridyanis','symbiont iridyanis',orianis),
	('Defense mutante','Apres avoir subit une attaque, il est possible de reduire de moitie les degats des prochaines attaques similaires. La reduction met 1 tour complet a se mettre en place et rend l''hote deux fois plus vulnerables a tout type d''attaque.','Iridyanis','symbiont iridyanis',orianis),
	('Boucle adaptative','Apres avoir subit une attaque, les prochaines attaques du meme type sont reduites de 10% (jusqu''a 100%, cumulable). Si un autre type d''attaque est subit entre temps, l''effet est reinitialise','Iridyanis','symbiont iridyanis',orianis),
	('Butin','Permet d''engranger des PV et PM supplementaires dans des cagnottes speciales qui s''ajoutent aux totaux de PV max et PM max','Enairo','symbiont enairo',orianis),
	('Gout du sang','En blessant une cible, vous gagnez 1d10 dans la cagnotte ayant la valeur la plus faible (jusqu''a 3 fois par cible). Si vous tuez une cible avec les 3 charges cumulees, vous obtenez 1d20 bonus dans les deux cagnottes','Enairo','symbiont enairo',orianis),
	('Bonne etoile','En cas de reussite, votre cagnotte la plus faible gagne autant que le chiffre des unites de votre jet (0 = +10 pts)','Enairo','symbiont enairo',orianis),
	('Mauvaise fortune','En cas d''echec, votre cagnotte la plus elevee perd autant que le chiffre des unites de votre jet (0 = -10 pts)','Enairo','symbiont enairo',orianis),
	('Defaite ineluctable','Chaque fois que vous encaissez des degats, vous perdez 10% des degats subits dans vos deux cagnottes','Enairo','symbiont enairo',orianis),
	('Dette','Si une cagnotte est negative, chaque gain dessus est divise par 2','Enairo','symbiont enairo',orianis),
	('Discretion','+10% en infiltration et camouflage','Espion','affiliation espion',orianis),
	('Spectre de l''ombre','deplacements x2 quand aucune cible ennemie n''a la vision sur vous','Espion','affiliation espion',orianis),
	('Frappe preventive','En etant camoufle, permet de beneficier d''une attaque d''opportunite avec un bonus de 20%','Espion','affiliation espion',orianis),
	('Loi du silence','Votre affiliation est secrète, si elle devait etre decouverte votre seule option serait le suicide volontaire ou non','Espion','affiliation espion',orianis),
	('Dualite energetique','Permet de puiser directement dans les PV pour utiliser des competences lorsque les PM viennent a manquer','Religieux','affiliation religieux',orianis),
	('Karma ascendant','Vous demarrez a -10 de Karma, mais celui-ci ne peut qu''augmenter et et ne peut pas diminuer','Religieux','affiliation religieux',orianis),
	('Pacifiste','Retire tous les bonus et inflige -20% sur toutes les actions offensives. Le mode offensif est egalement interdit','Religieux','affiliation religieux',orianis),
	('Taxe universelle','Pour toute somme d''argent percue, celle-ci est augmentee de 10%','Federation du commerce','orianis-main affiliation federation-commerce',orianis),
	('Hors taxe','Pour toute depende d''argent avec une entite rattachee a la federation, vous versez 10% de moins de la somme totale','Federation du commerce','orianis-main affiliation federation-commerce',orianis),
	('Trader','Autoriser a realiser n''importe quelle action legale en lien avec la bourse. Il est possible d''acheter / vendre des actions','Federation du commerce','orianis-main affiliation federation-commerce',orianis),
	('Mutation spontanee','Tous les 2 niveaux, sur un jet de chance reussi, permet d''obtenir une mutation qui permet de de rajouter ou changer vos talents (5 max au total)','Scientifique','orianis-main affiliation scientifique',orianis),
	('Evolution personnelle','Octroie l''access aux technologies permettant l''hybridation transgenique et/ou l''obtention d''un symbiote legal','Scientifique','orianis-main affiliation scientifique',orianis),
	('Diamants eternels','Permet de posseder les cryptodevises ainsi que le devise physique de contrebande','Contrebandier','orianis-main affiliation contrebandier',orianis),
	('Marches parallele','Permet d''acheter les technologies et autres avantages lies aux autres factions via la contrebande et ses devises','Contrebandier','orianis-main affiliation contrebandier',orianis),
	('Vaurien','+10% en piratage','Contrebandier','orianis-main affiliation contrebandier',orianis),
	('Armemement adaptatif','Octroie un equipement militaire de classe F','Militaire','orianis-main affiliation militaire',orianis),
	('Protocoles restrictifs','Les equipements de classes S sont reserves aux sous-lieutenant de niveau 5 minimum, la classe X aux commandants niveau 8 minimum et Omega aux generaux de niveau 10 minimum','Militaire','orianis-main affiliation militaire',orianis),
	('Laissez-passer A-38','Octroie une immunite diplomatique','Bureaucrate','orianis-main affiliation bureaucrate',orianis),
	('Suffrage universel','Les decisions importantes de groupe doivent etre votees par tous ses membres, ceux qui refusent de suivre le resultat auront un malus de 20% pour agi a l''encontre de cette decision.','Bureaucrate','orianis-main affiliation bureaucrate',orianis),
	('Prelevement a la source','Vous percevez toutes les recompenses de groupes, en versant aux autres membres leur part, vous les taxez a hauteur de 10% sur leurs revenus.','Bureaucrate','orianis-main affiliation bureaucrate',orianis);
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
	SELECT id_race INTO idr FROM Race WHERE nom = 'Lythis' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Lythis' ORDER BY id_skill LIMIT 5) LOOP
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
	SELECT id_race INTO idr FROM Race WHERE nom = 'Machina' AND id_extension = terae;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Machina' AND nom = 'Mental d''acier' ORDER BY id_skill LIMIT 1) LOOP
		INSERT INTO RaceSkills VALUES (idr, sk.id_skill);
	END LOOP;
	RAISE NOTICE 'Inserts in RaceSkills completed';
	-- OrgSkills
	SELECT id_org INTO ido FROM Organizations WHERE nom = 'Espion' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Espion' AND id_extension = orianis ORDER BY id_skill) LOOP
		INSERT INTO OrgSkills VALUES (ido, sk.id_skill);
	END LOOP;
	SELECT id_org INTO ido FROM Organizations WHERE nom = 'Religieux' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Religieux' AND id_extension = orianis ORDER BY id_skill) LOOP
		INSERT INTO OrgSkills VALUES (ido, sk.id_skill);
	END LOOP;
	SELECT id_org INTO ido FROM Organizations WHERE nom = 'Federation du commerce' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Federation du commerce' AND id_extension = orianis ORDER BY id_skill) LOOP
		INSERT INTO OrgSkills VALUES (ido, sk.id_skill);
	END LOOP;
	SELECT id_org INTO ido FROM Organizations WHERE nom = 'Scientifique' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Scientifique' AND id_extension = orianis ORDER BY id_skill) LOOP
		INSERT INTO OrgSkills VALUES (ido, sk.id_skill);
	END LOOP;
	SELECT id_org INTO ido FROM Organizations WHERE nom = 'Contrebandier' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Contrebandier' AND id_extension = orianis ORDER BY id_skill) LOOP
		INSERT INTO OrgSkills VALUES (ido, sk.id_skill);
	END LOOP;
	SELECT id_org INTO ido FROM Organizations WHERE nom = 'Militaire' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Militaire' AND id_extension = orianis ORDER BY id_skill) LOOP
		INSERT INTO OrgSkills VALUES (ido, sk.id_skill);
	END LOOP;
	SELECT id_org INTO ido FROM Organizations WHERE nom = 'Bureaucrate' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Bureaucrate' AND id_extension = orianis ORDER BY id_skill) LOOP
		INSERT INTO OrgSkills VALUES (ido, sk.id_skill);
	END LOOP;
	RAISE NOTICE 'Inserts in OrgSkills completed';
	-- SymbiontSkills
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Azort' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Azort' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Iridyanis' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Iridyanis' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	SELECT id_symbiont INTO ids FROM Symbiont WHERE nom = 'Enairo' AND id_extension = orianis;
	FOR sk IN (SELECT id_skill FROM Skills WHERE origine = 'Enairo' ORDER BY id_skill) LOOP
		INSERT INTO SymbiontSkills VALUES (ids, sk.id_skill);
	END LOOP;
	RAISE NOTICE 'Inserts in SymbiontSkills completed';
	-- Terae update
	UPDATE Skills
	SET origine = 'ROOT', webclass = 'machina affiliation root'
	WHERE nom = 'Cloud' AND origine = 'Machina' AND id_extension = terae;
	RAISE NOTICE 'Updates for Terae completed';
END orianisupdate $$;


-- Perform update of characterr
ALTER TABLE public.Characterr ADD COLUMN hybrid_race INT CONSTRAINT character_hybrid_default DEFAULT NULL;
ALTER TABLE public.Characterr ADD COLUMN id_symbiont INT CONSTRAINT character_symbiont_default DEFAULT NULL;
ALTER TABLE public.Characterr ADD COLUMN pilot_p INT CONSTRAINT character_pilotp_notnull NOT NULL CONSTRAINT character_pilotp_default DEFAULT -1;
ALTER TABLE public.Characterr ADD COLUMN pilot_a INT CONSTRAINT character_pilota_notnull NOT NULL CONSTRAINT character_pilota_default DEFAULT -1;
UPDATE Characterr SET hybrid_race = NULL, id_symbiont = NULL, pilot_p = -1, pilot_a = -1;
ALTER TABLE public.Characterr ADD CONSTRAINT FK_character_hybrid FOREIGN KEY (hybrid_race) REFERENCES public.Race(id_race);
ALTER TABLE public.Characterr ADD CONSTRAINT FK_character_symbiont FOREIGN KEY (id_symbiont) REFERENCES public.Symbiont(id_symbiont);
ALTER TABLE public.Characterr DROP CONSTRAINT character_kardef_check;


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
	IF prevsb IS NOT NULL THEN
		DELETE FROM havingskill
		WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan AND id_skill IN (SELECT id_skill FROM SymbiontSkills WHERE id_symbiont = prevsb);
	END IF;
	UPDATE characterr
	SET id_symbiont = sb
	WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	IF sb IS NOT NULL THEN
		FOR sk IN (SELECT id_skill FROM SymbiontSkills WHERE id_symbiont = sb) LOOP
			PERFORM assign_skill(dbkey, idserv, idchan, sk.id_skill);
		END LOOP;
	END IF;
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
	-- update here
	IF LOWER(stat) = 'pa' THEN
		UPDATE Characterr
		SET pilot_a = val
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(stat) = 'pp' THEN
		UPDATE Characterr
		SET pilot_p = val
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
