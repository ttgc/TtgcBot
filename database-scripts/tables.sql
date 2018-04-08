------------------------------------------------------------
--        Script Postgre 
------------------------------------------------------------



------------------------------------------------------------
-- Table: Membre
------------------------------------------------------------
CREATE TABLE public.Membre(
	id_member        VARCHAR (25) CONSTRAINT membre_id_null NOT NULL ,
	perms            CHAR (1)   ,
	local_perms		 CHAR (1)   ,
	CONSTRAINT prk_constraint_Membre PRIMARY KEY (id_member)
);


------------------------------------------------------------
-- Table: Perms
------------------------------------------------------------
CREATE TABLE public.Perms(
	code    CHAR (1) CONSTRAINT perms_code_null NOT NULL ,
	libelle VARCHAR (25) CONSTRAINT perms_libelle_null NOT NULL ,
	CONSTRAINT prk_constraint_Perms PRIMARY KEY (code)
);


------------------------------------------------------------
-- Table: JDR
------------------------------------------------------------
CREATE TABLE public.JDR(
	id_server  VARCHAR (25) CONSTRAINT jdr_server_null NOT NULL ,
	id_channel VARCHAR (25) CONSTRAINT jdr_channel_null NOT NULL ,
	creation   DATE CONSTRAINT jdr_creation_null NOT NULL ,
	PJs        INT   ,
	id_member  VARCHAR (25)  ,
	CONSTRAINT prk_constraint_JDR PRIMARY KEY (id_server,id_channel)
);


------------------------------------------------------------
-- Table: Character
------------------------------------------------------------
CREATE TABLE public.Character(
	charkey              VARCHAR (25) CONSTRAINT character_charkey_null NOT NULL ,
	nom                  VARCHAR (25)  ,
	lore                 VARCHAR (2000)  ,
	lvl		             INT   ,
	PV                   INT   ,
	PVmax                INT   ,
	PM                   INT   ,
	PMmax                INT   ,
	strength             INT   ,
	spirit               INT   ,
	charisma             INT   ,
	agility              INT   ,
	karma                INT   ,
	argent               INT   ,
	light_points         INT   ,
	dark_points          INT   ,
	intuition            INT   ,
	mental               INT   ,
	rolled_dice          INT   ,
	succes               INT   ,
	fail                 INT   ,
	critic_success       INT   ,
	critic_fail          INT   ,
	super_critic_success INT   ,
	super_critic_fail    INT   ,
	id_server            VARCHAR (25)  ,
	id_channel           VARCHAR (25)  ,
	gm                   CHAR (1)   ,
	gm_default		     CHAR (1)   ,
	id_inventory         INT   ,
  charlink             VARCHAR (25)   ,
	CONSTRAINT prk_constraint_Character PRIMARY KEY (charkey)
);


------------------------------------------------------------
-- Table: Gamemods
------------------------------------------------------------
CREATE TABLE public.Gamemods(
	gm_code CHAR (1) CONSTRAINT gamemods_code_null NOT NULL ,
	gm_name VARCHAR (25) CONSTRAINT gamemods_name_null NOT NULL ,
	CONSTRAINT prk_constraint_Gamemods PRIMARY KEY (gm_code)
);


------------------------------------------------------------
-- Table: Items
------------------------------------------------------------
CREATE TABLE public.Items(
	id_item     SERIAL CONSTRAINT items_id_null NOT NULL ,
	nom         VARCHAR (25) CONSTRAINT items_name_null NOT NULL ,
	description VARCHAR (25)  ,
	weight      FLOAT CONSTRAINT items_weight_null NOT NULL ,
	CONSTRAINT prk_constraint_Items PRIMARY KEY (id_item)
);


------------------------------------------------------------
-- Table: Inventaire
------------------------------------------------------------
CREATE TABLE public.Inventaire(
	id_inventory SERIAL CONSTRAINT inventaire_id_null NOT NULL ,
	size_        INT CONSTRAINT inventaire_size_null NOT NULL ,
	size_max     INT CONSTRAINT inventaire_sizemax_null NOT NULL ,
	charkey      VARCHAR (25)  ,
	CONSTRAINT prk_constraint_Inventaire PRIMARY KEY (id_inventory)
);


------------------------------------------------------------
-- Table: Serveur
------------------------------------------------------------
CREATE TABLE public.Serveur(
	id_server    VARCHAR (25) CONSTRAINT serveur_id_null NOT NULL ,
	MJrole       VARCHAR (25)  ,
	prefix       VARCHAR (25) CONSTRAINT serveur_prefix_null NOT NULL CONSTRAINT serveur_prefix_default DEFAULT '/' ,
	keeping_role BOOL CONSTRAINT serveur_keepingrole_null NOT NULL ,
	CONSTRAINT prk_constraint_Serveur PRIMARY KEY (id_server)
);


------------------------------------------------------------
-- Table: Local Perms
------------------------------------------------------------
CREATE TABLE public.Local_Perms(
	code    CHAR (1) CONSTRAINT localperms_code_null NOT NULL ,
	libelle VARCHAR (25) CONSTRAINT localperms_libelle_null NOT NULL ,
	CONSTRAINT prk_constraint_Local_Perms PRIMARY KEY (code)
);


------------------------------------------------------------
-- Table: Word Blocklist
------------------------------------------------------------
CREATE TABLE public.Word_Blocklist(
	word_number SERIAL CONSTRAINT wordblock_number_null NOT NULL ,
	content     VARCHAR (25)  ,
	id_server   VARCHAR (25)  ,
	CONSTRAINT prk_constraint_Word_Blocklist PRIMARY KEY (word_number)
);


------------------------------------------------------------
-- Table: Role
------------------------------------------------------------
CREATE TABLE public.Role(
	id_role   VARCHAR (25) CONSTRAINT role_id_null NOT NULL ,
	id_server VARCHAR (25) CONSTRAINT role_server_null NOT NULL ,
	CONSTRAINT prk_constraint_Role PRIMARY KEY (id_role)
);


------------------------------------------------------------
-- Table: Blacklist
------------------------------------------------------------
CREATE TABLE public.Blacklist(
	id_member        VARCHAR (25) CONSTRAINT blacklist_member_null NOT NULL ,
	reason           VARCHAR (25)  ,
	--id_member_Membre VARCHAR (25)  ,
	CONSTRAINT prk_constraint_Blacklist PRIMARY KEY (id_member)
);


------------------------------------------------------------
-- Table: Contient
------------------------------------------------------------
CREATE TABLE public.Contient(
	id_item      INT CONSTRAINT contient_item_null NOT NULL ,
	id_inventory INT CONSTRAINT contient_inventory_null NOT NULL ,
	CONSTRAINT prk_constraint_Contient PRIMARY KEY (id_item,id_inventory)
);


------------------------------------------------------------
-- Table: Keeprole
------------------------------------------------------------
CREATE TABLE public.Keeprole(
	id_member VARCHAR (25) CONSTRAINT keeprole_member_null NOT NULL ,
	id_server VARCHAR (25) CONSTRAINT keeprole_server_null NOT NULL ,
	id_role   VARCHAR (25) CONSTRAINT keeprole_role_null NOT NULL ,
	CONSTRAINT prk_constraint_Keeprole PRIMARY KEY (id_member,id_server,id_role)
);



ALTER TABLE public.Membre ADD CONSTRAINT FK_Membre_perms FOREIGN KEY (perms) REFERENCES public.Perms(code);
ALTER TABLE public.Membre ADD CONSTRAINT FK_Membre_local_perms FOREIGN KEY (local_perms) REFERENCES public.Local_Perms(code);
ALTER TABLE public.JDR ADD CONSTRAINT FK_JDR_id_member FOREIGN KEY (id_member) REFERENCES public.Membre(id_member);
ALTER TABLE public.Character ADD CONSTRAINT FK_Character_id_server FOREIGN KEY (id_server) REFERENCES public.JDR(id_server);
ALTER TABLE public.Character ADD CONSTRAINT FK_Character_id_channel FOREIGN KEY (id_channel) REFERENCES public.JDR(id_channel);
ALTER TABLE public.Character ADD CONSTRAINT FK_Character_gm FOREIGN KEY (gm) REFERENCES public.Gamemods(gm_code);
ALTER TABLE public.Character ADD CONSTRAINT FK_Character_gm_default FOREIGN KEY (gm_default) REFERENCES public.Gamemods(gm_code);
ALTER TABLE public.Character ADD CONSTRAINT FK_Character_id_inventory FOREIGN KEY (id_inventory) REFERENCES public.Inventaire(id_inventory);
ALTER TABLE public.Inventaire ADD CONSTRAINT FK_Inventaire_charkey FOREIGN KEY (charkey) REFERENCES public.Character(charkey);
ALTER TABLE public.Word_Blocklist ADD CONSTRAINT FK_Word_Blocklist_id_server FOREIGN KEY (id_server) REFERENCES public.Serveur(id_server);
ALTER TABLE public.Role ADD CONSTRAINT FK_Role_id_server FOREIGN KEY (id_server) REFERENCES public.Serveur(id_server);
ALTER TABLE public.Blacklist ADD CONSTRAINT FK_Blacklist_id_member FOREIGN KEY (id_member) REFERENCES public.Membre(id_member);
ALTER TABLE public.Contient ADD CONSTRAINT FK_Contient_id_item FOREIGN KEY (id_item) REFERENCES public.Items(id_item);
ALTER TABLE public.Contient ADD CONSTRAINT FK_Contient_id_inventory FOREIGN KEY (id_inventory) REFERENCES public.Inventaire(id_inventory);
ALTER TABLE public.Keeprole ADD CONSTRAINT FK_Keeprole_id_member FOREIGN KEY (id_member) REFERENCES public.Membre(id_member);
ALTER TABLE public.Keeprole ADD CONSTRAINT FK_Keeprole_id_server FOREIGN KEY (id_server) REFERENCES public.Serveur(id_server);
ALTER TABLE public.Keeprole ADD CONSTRAINT FK_Keeprole_id_role FOREIGN KEY (id_role) REFERENCES public.Role(id_role);
ALTER TABLE public.Character ADD CONSTRAINT FK_Character_charlink FOREIGN KEY (charlink) REFERENCES public.Membre(id_member);
