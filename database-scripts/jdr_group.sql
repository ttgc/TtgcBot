CREATE TABLE public.JDR_Groupe(
	grkey VARCHAR (25) CONSTRAINT jdrgroupe_grkey_null NOT NULL ,
	id_server VARCHAR (25) CONSTRAINT jdrgroupe_idserver_null NOT NULL ,
  id_channel VARCHAR (25) CONSTRAINT jdrgroupe_idchannel_null NOT NULL ,
  localMJ VARCHAR (25) CONSTRAINT jdrgroupe_localMJ_default DEFAULT NULL ,
  joinable BOOL CONSTRAINT jdrgroupe_joinable_null NOT NULL CONSTRAINT jdrgroupe_joinable_default DEFAULT false ,
	CONSTRAINT prk_constraint_jdrgroupe PRIMARY KEY (grkey, id_server, id_channel)
)WITHOUT OIDS;

CREATE TABLE public.JDR_Groupe_Member(
	grkey VARCHAR (25) CONSTRAINT jdrgroupemember_grkey_null NOT NULL ,
	id_server VARCHAR (25) CONSTRAINT jdrgroupemember_idserver_null NOT NULL ,
  id_channel VARCHAR (25) CONSTRAINT jdrgroupemember_idchannel_null NOT NULL ,
  charkey VARCHAR (25) CONSTRAINT jdrgroupemember_charkey_null NOT NULL ,
	CONSTRAINT prk_constraint_jdrgroupemember PRIMARY KEY (grkey, id_server, id_channel, charkey)
)WITHOUT OIDS;

ALTER TABLE public.JDR_Groupe ADD CONSTRAINT FK_jdrgroupe_jdr FOREIGN KEY (id_server, id_channel) REFERENCES public.JDR(id_server, id_channel);
ALTER TABLE public.JDR_Groupe_Member ADD CONSTRAINT FK_jdrgroupemember_groupe FOREIGN KEY (grkey, id_server, id_channel) REFERENCES public.JDR_Groupe(grkey, id_server, id_channel);
ALTER TABLE public.JDR_Groupe_Member ADD CONSTRAINT FK_jdrgroupemember_character FOREIGN KEY (id_server, id_channel, charkey) REFERENCES public.Characterr(id_server, id_channel, charkey);


--REWRITTEN FUNCTIONS
CREATE OR REPLACE FUNCTION chardelete
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS void AS $$
BEGIN
	--update here
  DELETE FROM JDR_Groupe_Member
  WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan;
	--end of update
  DELETE FROM havingskill
	WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan;
	DELETE FROM Pet
	WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan;
	DELETE FROM Characterr
	WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan;
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
	DELETE FROM finalize
	WHERE id_server = idserv AND id_channel = idchan;
  --update here
  DELETE FROM JDR_Groupe
  WHERE id_server = idserv AND id_channel = idchan;
  --end of update
  PERFORM clearmap(idserv,idchan);
	DELETE FROM JDR
	WHERE id_server = idserv AND id_channel = idchan;
END;
$$ LANGUAGE plpgsql;


-- new fonctions
CREATE OR REPLACE FUNCTION add_group
(
	dbkey JDR_Groupe.grkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS void AS $$
BEGIN
	INSERT INTO JDR_Groupe (grkey, id_server, id_channel) VALUES (dbkey, idserv, idchan);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_group
(
	dbkey JDR_Groupe.grkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
  overrideMJ JDR_Groupe.localMJ%TYPE,
  groupisjoinable JDR_Groupe.joinable%TYPE
) RETURNS void AS $$
BEGIN
	UPDATE JDR_Groupe
  SET localMJ = overrideMJ, joinable = groupisjoinable
  WHERE grkey = dbkey AND id_server = idserv AND id_channel = idchan;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_group
(
	dbkey JDR_Groupe.grkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS void AS $$
BEGIN
  DELETE FROM JDR_Groupe_Member
  WHERE grkey = dbkey AND id_server = idserv AND id_channel = idchan;
	DELETE FROM JDR_Groupe
  WHERE grkey = dbkey AND id_server = idserv AND id_channel = idchan;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION join_group
(
	grp JDR_Groupe.grkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
  charact Characterr.charkey%TYPE
) RETURNS void AS $$
BEGIN
	INSERT INTO JDR_Groupe_Member
  VALUES (grp, idserv, idchan, charact);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION leave_group
(
	grp JDR_Groupe.grkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
  charact Characterr.charkey%TYPE
) RETURNS void AS $$
BEGIN
  DELETE FROM JDR_Groupe_Member
  WHERE grkey = dbkey AND id_server = idserv AND id_channel = idchan AND charkey = charact;
END;
$$ LANGUAGE plpgsql;
