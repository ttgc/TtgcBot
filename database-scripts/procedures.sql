CREATE OR REPLACE FUNCTION charcreate
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS void AS $$
DECLARE
	inv inventaire.id_inventory%TYPE;
BEGIN
	INSERT INTO inventaire (charkey)
	VALUES (dbkey);
	SELECT MAX(id_inventory) INTO inv FROM inventaire
	WHERE charkey = dbkey;
	INSERT INTO Characterr
	VALUES (dbkey, dbkey, '', 1, 1, 1, 1, 1, 50, 50, 50, 50, 0, 0, 0, 1, 1, 3, 100, 0, 0, 0, 0, 0, 0, 0, idserv, idchan, 'O', 'O', inv, 'NULL');
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION jdrcreate
(
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	mj Membre.id_member%TYPE
) RETURNS void AS $$
BEGIN
	INSERT INTO JDR (id_server, id_channel, id_member)
	VALUES (idserv, idchan, mj);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION mjtransfer
(
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	mj Membre.id_member%TYPE
) RETURNS void AS $$
BEGIN
	UPDATE JDR
	SET id_member = mj
	WHERE id_server = idserv AND id_channel = idchan;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION chardelete
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS void AS $$
BEGIN
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
	FOR line IN (SELECT charkey FROM Characterr WHERE id_server = idserv AND id_channel = idchan) LOOP
		PERFORM chardelete(line.charkey, idserv, idchan);
	END LOOP;
	DELETE FROM JDR
	WHERE id_server = idserv AND id_channel = idchan;
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
		VALUES (dbkey);
		SELECT MAX(id_inventory) INTO inv FROM inventaire
		WHERE charkey = dbkey;
		INSERT INTO Characterr
		VALUES (line.charkey, line.name, line.lore, line.lvl, line.PV, line.PVmax, line.PM, line.PMmax, line.strength, line.spirit, line.charisma, line.agility, line.karma, line.defaultkarma, line.argent, line.light_points, line.dark_points, line.intuition, line.mental, line.rolled_dice, line.success, line.fail, line.critic_success, line.critic_fail, line.super_critic_success, line.super_critic_fail, idserv, dest, line.gm, line.gm_default, inv, line.id_member);
	END LOOP;
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
END;
$$ LANGUAGE plpgsql;