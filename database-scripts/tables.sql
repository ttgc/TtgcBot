------------------------------------------------------------
--        Script Postgre 
------------------------------------------------------------



------------------------------------------------------------
-- Table: Membre
------------------------------------------------------------
CREATE TABLE public.Membre(
	id_member        VARCHAR (25) CONSTRAINT membre_id_null NOT NULL ,
	perms            CHAR (1)   ,
	--local_perms		 CHAR (1)   ,
	CONSTRAINT prk_constraint_Membre PRIMARY KEY (id_member)
)WITHOUT OIDS;


------------------------------------------------------------
-- Table: Perms
------------------------------------------------------------
CREATE TABLE public.Perms(
	code    CHAR (1) CONSTRAINT perms_code_null NOT NULL ,
	libelle VARCHAR (25) CONSTRAINT perms_libelle_null NOT NULL ,
	CONSTRAINT prk_constraint_Perms PRIMARY KEY (code)
)WITHOUT OIDS;


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
)WITHOUT OIDS;


------------------------------------------------------------
-- Table: Characterr
------------------------------------------------------------
CREATE TABLE public.Characterr(
	charkey              VARCHAR (25) CONSTRAINT character_charkey_null NOT NULL ,
	nom                  VARCHAR (25)  ,
	lore                 VARCHAR (2000)  ,
	lvl		             INT   CONSTRAINT character_lvl_check CHECK (lvl > 0),
	PV                   INT   ,
	PVmax                INT   CONSTRAINT character_pvmax_check CHECK (PVmax > 0),
	PM                   INT   CONSTRAINT character_pm_check CHECK (PM >= 0),
	PMmax                INT   CONSTRAINT character_pmmax_check CHECK (PMmax > 0),
	strength             INT   CONSTRAINT character_str_check CHECK (strength > 0 AND strength <= 100),
	spirit               INT   CONSTRAINT character_spr_check CHECK (spirit > 0 AND spirit <= 100),
	charisma             INT   CONSTRAINT character_cha_check CHECK (charisma > 0 AND charisma <= 100),
	agility              INT   CONSTRAINT character_agi_check CHECK (agility > 0 AND agility <= 100),
	karma                INT   CONSTRAINT character_kar_check CHECK (karma >= -10 AND karma <= 10),
	defaultkarma		 INT   CONSTRAINT character_kardef_check CHECK (defaultkarma IN (-5,-4,0,4,5)),
	argent               INT   CONSTRAINT character_argent_check CHECK (argent >= 0),
	light_points         INT   ,
	dark_points          INT   ,
	intuition            INT   CONSTRAINT character_int_check CHECK (intuition > 0 AND intuition <= 6),
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
	id_member			 VARCHAR (25) ,
	CONSTRAINT prk_constraint_Character PRIMARY KEY (charkey, id_server, id_channel) ,
	CONSTRAINT character_pvpvmax_check CHECK (PV <= PVmax) ,
	CONSTRAINT charcater_pmpmmax_check CHECK (PM <= PMmax)
)WITHOUT OIDS;


------------------------------------------------------------
-- Table: Gamemods
------------------------------------------------------------
CREATE TABLE public.Gamemods(
	gm_code CHAR (1) CONSTRAINT gamemods_code_null NOT NULL ,
	gm_name VARCHAR (25) CONSTRAINT gamemods_name_null NOT NULL ,
	CONSTRAINT prk_constraint_Gamemods PRIMARY KEY (gm_code)
)WITHOUT OIDS;


------------------------------------------------------------
-- Table: Items
------------------------------------------------------------
CREATE TABLE public.Items(
	id_item     SERIAL CONSTRAINT items_id_null NOT NULL ,
	nom         VARCHAR (50) CONSTRAINT items_name_null NOT NULL ,
	description VARCHAR (100)  ,
	weight      FLOAT CONSTRAINT items_weight_null NOT NULL ,
	CONSTRAINT prk_constraint_Items PRIMARY KEY (id_item)
)WITHOUT OIDS;


------------------------------------------------------------
-- Table: Inventaire
------------------------------------------------------------
CREATE TABLE public.Inventaire(
	id_inventory SERIAL CONSTRAINT inventaire_id_null NOT NULL ,
	size_        FLOAT CONSTRAINT inventaire_size_null NOT NULL ,
	size_max     INT CONSTRAINT inventaire_sizemax_null NOT NULL ,
	charkey      VARCHAR (25)  ,
	CONSTRAINT prk_constraint_Inventaire PRIMARY KEY (id_inventory)
)WITHOUT OIDS;


------------------------------------------------------------
-- Table: Serveur
------------------------------------------------------------
CREATE TABLE public.Serveur(
	id_server    VARCHAR (25) CONSTRAINT serveur_id_null NOT NULL ,
	MJrole       VARCHAR (25)  ,
	prefixx      VARCHAR (25) CONSTRAINT serveur_prefix_null NOT NULL CONSTRAINT serveur_prefix_default DEFAULT '/' ,
	keeping_role BOOL CONSTRAINT serveur_keepingrole_null NOT NULL ,
	adminrole	 VARCHAR (25)  ,
	CONSTRAINT prk_constraint_Serveur PRIMARY KEY (id_server)
)WITHOUT OIDS;


------------------------------------------------------------
-- Table: Local Perms
------------------------------------------------------------
--CREATE TABLE public.Local_Perms(
	--code    CHAR (1) CONSTRAINT localperms_code_null NOT NULL ,
	--libelle VARCHAR (25) CONSTRAINT localperms_libelle_null NOT NULL ,
	--CONSTRAINT prk_constraint_Local_Perms PRIMARY KEY (code)
--)WITHOUT OIDS;


------------------------------------------------------------
-- Table: Word Blocklist
------------------------------------------------------------
CREATE TABLE public.Word_Blocklist(
	word_number SERIAL CONSTRAINT wordblock_number_null NOT NULL ,
	content     VARCHAR (25)  ,
	id_server   VARCHAR (25)  ,
	CONSTRAINT prk_constraint_Word_Blocklist PRIMARY KEY (word_number)
)WITHOUT OIDS;


------------------------------------------------------------
-- Table: Role
------------------------------------------------------------
CREATE TABLE public.Role(
	id_role   VARCHAR (25) CONSTRAINT role_id_null NOT NULL ,
	id_server VARCHAR (25) CONSTRAINT role_server_null NOT NULL ,
	CONSTRAINT prk_constraint_Role PRIMARY KEY (id_role,id_server)
)WITHOUT OIDS;


------------------------------------------------------------
-- Table: Blacklist
------------------------------------------------------------
CREATE TABLE public.Blacklist(
	id_member        VARCHAR (25) CONSTRAINT blacklist_member_null NOT NULL ,
	reason           VARCHAR (100)  ,
	--id_member_Membre VARCHAR (25)  ,
	CONSTRAINT prk_constraint_Blacklist PRIMARY KEY (id_member)
)WITHOUT OIDS;


------------------------------------------------------------
-- Table: Contient
------------------------------------------------------------
CREATE TABLE public.Contient(
	id_item      INT CONSTRAINT contient_item_null NOT NULL ,
	id_inventory INT CONSTRAINT contient_inventory_null NOT NULL ,
	qte			 INT CONSTRAINT contient_qte_null NOT NULL CONSTRAINT contient_qte_check CHECK (qte > 0) ,
	CONSTRAINT prk_constraint_Contient PRIMARY KEY (id_item,id_inventory)
)WITHOUT OIDS;


------------------------------------------------------------
-- Table: Keeprole
------------------------------------------------------------
CREATE TABLE public.Keeprole(
	id_member VARCHAR (25) CONSTRAINT keeprole_member_null NOT NULL ,
	id_server VARCHAR (25) CONSTRAINT keeprole_server_null NOT NULL ,
	id_role   VARCHAR (25) CONSTRAINT keeprole_role_null NOT NULL ,
	CONSTRAINT prk_constraint_Keeprole PRIMARY KEY (id_member,id_server,id_role)
)WITHOUT OIDS;



ALTER TABLE public.Membre ADD CONSTRAINT FK_Membre_perms FOREIGN KEY (perms) REFERENCES public.Perms(code);
--ALTER TABLE public.Membre ADD CONSTRAINT FK_Membre_local_perms FOREIGN KEY (local_perms) REFERENCES public.Local_Perms(code);
ALTER TABLE public.JDR ADD CONSTRAINT FK_JDR_id_member FOREIGN KEY (id_member) REFERENCES public.Membre(id_member);
ALTER TABLE public.JDR ADD CONSTRAINT FK_JDR_id_server FOREIGN KEY (id_server) REFERENCES public.Serveur(id_server);
ALTER TABLE public.Characterr ADD CONSTRAINT FK_Character_id_serverchan FOREIGN KEY (id_server,id_channel) REFERENCES public.JDR(id_server,id_channel);
--ALTER TABLE public.Characterr ADD CONSTRAINT FK_Character_id_channel FOREIGN KEY (id_channel) REFERENCES public.JDR(id_channel);
ALTER TABLE public.Characterr ADD CONSTRAINT FK_Character_gm FOREIGN KEY (gm) REFERENCES public.Gamemods(gm_code);
ALTER TABLE public.Characterr ADD CONSTRAINT FK_Character_gm_default FOREIGN KEY (gm_default) REFERENCES public.Gamemods(gm_code);
ALTER TABLE public.Characterr ADD CONSTRAINT FK_Character_id_inventory FOREIGN KEY (id_inventory) REFERENCES public.Inventaire(id_inventory);
ALTER TABLE public.Characterr ADD CONSTRAINT FK_Character_id_member FOREIGN KEY (id_member) REFERENCES public.Membre(id_member);
--ALTER TABLE public.Inventaire ADD CONSTRAINT FK_Inventaire_charkey FOREIGN KEY (charkey) REFERENCES public.Characterr(charkey);
ALTER TABLE public.Word_Blocklist ADD CONSTRAINT FK_Word_Blocklist_id_server FOREIGN KEY (id_server) REFERENCES public.Serveur(id_server);
ALTER TABLE public.Role ADD CONSTRAINT FK_Role_id_server FOREIGN KEY (id_server) REFERENCES public.Serveur(id_server);
ALTER TABLE public.Blacklist ADD CONSTRAINT FK_Blacklist_id_member FOREIGN KEY (id_member) REFERENCES public.Membre(id_member);
ALTER TABLE public.Contient ADD CONSTRAINT FK_Contient_id_item FOREIGN KEY (id_item) REFERENCES public.Items(id_item);
ALTER TABLE public.Contient ADD CONSTRAINT FK_Contient_id_inventory FOREIGN KEY (id_inventory) REFERENCES public.Inventaire(id_inventory);
ALTER TABLE public.Keeprole ADD CONSTRAINT FK_Keeprole_id_member FOREIGN KEY (id_member) REFERENCES public.Membre(id_member);
--ALTER TABLE public.Keeprole ADD CONSTRAINT FK_Keeprole_id_server FOREIGN KEY (id_server) REFERENCES public.Serveur(id_server);
ALTER TABLE public.Keeprole ADD CONSTRAINT FK_Keeprole_id_role FOREIGN KEY (id_role,id_server) REFERENCES public.Role(id_role,id_server);

INSERT INTO Perms VALUES ('N','None');
INSERT INTO Perms VALUES ('O','Owner');
INSERT INTO Perms VALUES ('M','Manager');
INSERT INTO Perms VALUES ('P','Premium');
--INSERT INTO Local_perms VALUES ('N','None');
--INSERT INTO Local_perms VALUES ('A','Admin');
INSERT INTO Membre VALUES ('NULL','N');
INSERT INTO Gamemods VALUES ('O','Offensive');
INSERT INTO Gamemods VALUES ('D','Defensive');


CREATE TABLE public.Purge(
	id_server VARCHAR (25) CONSTRAINT purge_server_null NOT NULL ,
	datein DATE CONSTRAINT purge_datein_null NOT NULL ,
	CONSTRAINT prk_constraint_purge PRIMARY KEY (id_server)
)WITHOUT OIDS;

ALTER TABLE public.Purge ADD CONSTRAINT FK_purge_id_server FOREIGN KEY (id_server) REFERENCES public.Serveur(id_server);

CREATE TABLE public.JDRextension(
	id_server VARCHAR (25) ,
	id_src VARCHAR (25) ,
	id_target VARCHAR (25) ,
	CONSTRAINT prk_constraint_jdrextension PRIMARY KEY (id_target)
)WITHOUT OIDS;

ALTER TABLE public.JDRextension ADD CONSTRAINT FK_jdrextension_src FOREIGN KEY (id_server,id_src) REFERENCES public.JDR(id_server,id_channel);
ALTER TABLE public.JDRextension ADD CONSTRAINT FK_jdrextension_target FOREIGN KEY (id_server,id_target) REFERENCES public.JDR(id_server,id_channel);

--Adding warn features
CREATE TABLE public.warn(
	id_server VARCHAR (25) ,
	id_member VARCHAR (25) ,
	warn_number	INT CONSTRAINT warn_warnnumber_null NOT NULL CONSTRAINT warn_warnnumber_check CHECK (warn_number > 0) ,
	CONSTRAINT prk_constraint_warn PRIMARY KEY (id_server,id_member)
)WITHOUT OIDS;

CREATE TABLE public.warnconfig(
	id_server VARCHAR (25) ,
	warn_number INT CONSTRAINT warnconfig_warnnumber_check CHECK (warn_number > 0) ,
	sanction VARCHAR (25) CONSTRAINT warnconfig_sanction_null NOT NULL ,
	CONSTRAINT prk_constraint_warnconfig PRIMARY KEY (id_server,warn_number)
)WITHOUT OIDS;

ALTER TABLE public.warn ADD CONSTRAINT FK_warn_id_server FOREIGN KEY (id_server) REFERENCES public.Serveur(id_server);
ALTER TABLE public.warn ADD CONSTRAINT FK_warn_id_member FOREIGN KEY (id_member) REFERENCES public.Membre(id_member);
ALTER TABLE public.warnconfig ADD CONSTRAINT FK_warnconfig_id_server FOREIGN KEY (id_server) REFERENCES public.Serveur(id_server);

--Adding finalize features
CREATE TABLE public.finalize(
	id_server VARCHAR (25) ,
	id_channel VARCHAR (25) ,
	title VARCHAR (50) ,
	description VARCHAR (1000) CONSTRAINT finalize_descr_null NOT NULL ,
	CONSTRAINT prk_constraint_finalize PRIMARY KEY (id_server,id_channel,title)
)WITHOUT OIDS;

ALTER TABLE public.finalize ADD CONSTRAINT FK_finalize_jdr FOREIGN KEY (id_server,id_channel) REFERENCES public.JDR(id_server,id_channel);