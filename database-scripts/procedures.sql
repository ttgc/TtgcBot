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
DECLARE
	nbr INT;
BEGIN
	SELECT COUNT(*) INTO nbr FROM membre
	WHERE (id_member = mj);
	IF nbr = 0 THEN
		INSERT INTO Membre
		VALUES (mj,'N');
	END IF;
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
DECLARE
	nbr INT;
BEGIN
	SELECT COUNT(*) INTO nbr FROM membre
	WHERE (id_member = mj);
	IF nbr = 0 THEN
		INSERT INTO Membre
		VALUES (mj,'N');
	END IF;
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
	PERFORM JDRstopallextend(idserv,idchan);
	FOR line IN (SELECT charkey FROM Characterr WHERE id_server = idserv AND id_channel = idchan) LOOP
		PERFORM chardelete(line.charkey, idserv, idchan);
	END LOOP;
	DELETE FROM finalize
	WHERE id_server = idserv AND id_channel = idchan;
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
		VALUES (line.charkey);
		SELECT MAX(id_inventory) INTO inv FROM inventaire
		WHERE charkey = line.charkey;
		INSERT INTO Characterr
		VALUES (line.charkey, line.nom, line.lore, line.lvl, line.PV, line.PVmax, line.PM, line.PMmax, line.strength, line.spirit, line.charisma, line.agility, line.karma, line.defaultkarma, line.argent, line.light_points, line.dark_points, line.intuition, line.mental, line.rolled_dice, line.succes, line.fail, line.critic_success, line.critic_fail, line.super_critic_success, line.super_critic_fail, idserv, dest, line.gm, line.gm_default, inv, line.id_member);
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
		UPDATE Characterr
		SET argent = argent + val
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
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

CREATE OR REPLACE FUNCTION charsetlore
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	lor Characterr.lore%TYPE
) RETURNS void AS $$
BEGIN
	UPDATE Characterr
	SET lore = lor
	WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION charsetname
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	name Characterr.lore%TYPE
) RETURNS void AS $$
BEGIN
	UPDATE Characterr
	SET nom = name
	WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION hasroll
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	valmax INT,
	val INT
) RETURNS void AS $$
BEGIN
	IF val = 42 THEN
		UPDATE Characterr
		SET super_critic_success = super_critic_success + 1
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	ELSE
		IF val = 66 THEN
			UPDATE Characterr
			SET super_critic_fail = super_critic_fail + 1
			WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
		ELSE
			IF val <= 10 THEN
				UPDATE Characterr
				SET critic_success = critic_success + 1
				WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
			ELSE
				IF val >= 91 THEN
					UPDATE Characterr
					SET critic_fail = critic_fail + 1
					WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
				ELSE
					IF val <= valmax THEN
						UPDATE Characterr
						SET succes = succes + 1
						WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
					ELSE
						UPDATE Characterr
						SET fail = fail + 1
						WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
					END IF;
				END IF;
			END IF;
		END IF;
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION switchmod
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	def_ BOOLEAN
) RETURNS void AS $$
DECLARE
	curmod Gamemods.gm_code%TYPE;
BEGIN
	IF def_ THEN
		SELECT gm_default INTO curmod FROM Characterr
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
		IF curmod = 'O' THEN
			curmod := 'D';
		ELSE
			curmod := 'O';
		END IF;
		UPDATE Characterr
		SET gm_default = curmod
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	ELSE
		SELECT gm INTO curmod FROM Characterr
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
		IF curmod = 'O' THEN
			curmod := 'D';
		ELSE
			curmod := 'O';
		END IF;
		UPDATE Characterr
		SET gm = curmod
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION charlink
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	idmemb Characterr.id_member%TYPE
) RETURNS void AS $$
DECLARE
	nbr INT;
BEGIN
	SELECT COUNT(*) INTO nbr FROM Membre
	WHERE (id_member = idmemb);
	IF nbr = 0 THEN
		INSERT INTO Membre
		VALUES (idmemb,'N');
	END IF;
	UPDATE Characterr
	SET id_member = idmemb
	WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION charunlink
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS void AS $$
BEGIN
	UPDATE Characterr
	SET id_member = 'NULL'
	WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION levelup
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS void AS $$
BEGIN
	UPDATE Characterr
	SET lvl = lvl + 1
	WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION additem
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	itname Items.nom%TYPE,
	quantite INT
) RETURNS void AS $$
DECLARE
	item Items.id_item%TYPE;
	inv Inventaire.id_inventory%TYPE;
	nbr INT;
BEGIN
	SELECT id_item INTO item FROM Items
	WHERE (nom = itname);
	SELECT id_inventory INTO inv FROM Characterr
	WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	SELECT COUNT(*) INTO nbr FROM contient
	WHERE (id_inventory = inv AND id_item = item);
	IF nbr = 0 THEN
		INSERT INTO contient
		VALUES (item,inv,quantite);
	ELSE
		UPDATE contient
		SET qte = qte + quantite
		WHERE (id_item = item AND id_inventory = inv);
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION removeitem
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	itname Items.nom%TYPE,
	quantite INT
) RETURNS void AS $$
DECLARE
	item Items.id_item%TYPE;
	inv Inventaire.id_inventory%TYPE;
	nbr INT;
BEGIN
	SELECT id_item INTO item FROM Items
	WHERE (nom = itname);
	SELECT id_inventory INTO inv FROM Characterr
	WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	SELECT qte INTO nbr FROM contient
	WHERE (id_inventory = inv AND id_item = item);
	nbr := nbr - quantite;
	IF nbr = 0 THEN
		DELETE FROM contient
		WHERE (id_item = item AND id_inventory = inv);
	ELSE
		UPDATE contient
		SET qte = qte - quantite
		WHERE (id_item = item AND id_inventory = inv);
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION createitem
(
	name Items.nom%TYPE,
	descr Items.description%TYPE,
	poids Items.weight%TYPE
) RETURNS Items.id_item%TYPE AS $$
DECLARE
	idit Items.id_item%TYPE;
	nbr INT;
BEGIN
	SELECT COUNT(*) INTO nbr FROM Items
	WHERE (nom = name AND description = descr AND weight = poids);
	IF nbr = 0 THEN
		INSERT INTO Items (nom,description,weight)
		VALUES (name,descr,poids);
	END IF;
	SELECT id_item INTO idit FROM Items
	WHERE (nom = name AND description = descr AND weight = poids);
	RETURN idit;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION deleteitem
(
	item Items.id_item%TYPE
) RETURNS void AS $$
BEGIN
	DELETE FROM contient
	WHERE id_item = item;
	DELETE FROM items
	WHERE id_item = item;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION grantperms
(
	idmemb Membre.id_member%TYPE,
	perm Perms.code%TYPE
) RETURNS void AS $$
DECLARE
	nbr INT;
BEGIN
	SELECT COUNT(*) INTO nbr FROM membre
	WHERE (id_member = idmemb);
	IF nbr = 0 THEN
		INSERT INTO Membre
		VALUES (idmemb,perm);
	ELSE
		UPDATE Membre
		SET perms = perm
		WHERE (id_member = idmemb);
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION switchblacklist
(
	idmemb Membre.id_member%TYPE,
	eventual_reason Blacklist.reason%TYPE
) RETURNS void AS $$
DECLARE
	nbr INT;
	nbr2 INT;
BEGIN
	SELECT COUNT(*) INTO nbr FROM blacklist
	WHERE (id_member = idmemb);
	IF nbr = 0 THEN
		SELECT COUNT(*) INTO nbr2 FROM Membre
		WHERE (id_member = idmemb);
		IF nbr2 = 0 THEN
			INSERT INTO membre
			VALUES (idmemb,'N');
		END IF;
		INSERT INTO blacklist
		VALUES (idmemb,eventual_reason);
	ELSE
		DELETE FROM blacklist
		WHERE (id_member = idmemb);
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION togglekeepingrole
(
	idserv Serveur.id_server%TYPE
) RETURNS void AS $$
DECLARE
	enabled Serveur.keeping_role%TYPE;
BEGIN
	SELECT keeping_role INTO enabled FROM serveur
	WHERE (id_server = idserv);
	UPDATE serveur
	SET keeping_role = (NOT enabled)
	WHERE id_server = idserv;
	IF enabled THEN
		DELETE FROM keeprole
		WHERE (id_server = idserv);
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION backuprolemember
(
	idmemb Membre.id_member%TYPE,
	idserv Serveur.id_server%TYPE,
	idrole Role.id_role%TYPE
) RETURNS void AS $$
DECLARE
	nbr INT;
BEGIN
	SELECT COUNT(*) INTO nbr FROM membre
	WHERE (id_member = idmemb);
	IF nbr = 0 THEN
		INSERT INTO membre
		VALUES (idmemb,'N');
	END IF;
	INSERT INTO keeprole
	VALUES (idmemb,idserv,idrole);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION restorerolemember
(
	idmemb Membre.id_member%TYPE,
	idserv Serveur.id_server%TYPE,
	idrole Role.id_role%TYPE
) RETURNS void AS $$
BEGIN
	DELETE FROM keeprole
	WHERE (id_member = idmemb AND id_server = idserv AND id_role = idrole);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION addrole
(
	idserv Serveur.id_server%TYPE,
	idrole Role.id_role%TYPE
) RETURNS void AS $$
BEGIN
	INSERT INTO role
	VALUES (idrole,idserv);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION removerole
(
	idserv Serveur.id_server%TYPE,
	idrole Role.id_role%TYPE
) RETURNS void AS $$
BEGIN
	DELETE FROM keeprole
	WHERE (id_server = idserv AND id_role = idrole);
	DELETE FROM role
	WHERE (id_server = idserv AND id_role = idrole);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION clearkeeprole
(
	idserv Serveur.id_server%TYPE
) RETURNS int AS $$
DECLARE
	nbr INT;
BEGIN
	SELECT COUNT(id_member) INTO nbr FROM keeprole
	WHERE id_server = idserv;
	DELETE FROM keeprole
	WHERE id_server = idserv;
	RETURN nbr;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION addserver
(
	idserv Serveur.id_server%TYPE
) RETURNS void AS $$
DECLARE
	nbr INT;
BEGIN
	SELECT COUNT(*) INTO nbr FROM purge
	WHERE id_server = idserv;
	IF nbr = 0 THEN
		INSERT INTO serveur (id_server,prefixx,keeping_role)
		VALUES (idserv,'/',false);
	ELSE
		DELETE FROM purge
		WHERE id_server = idserv;
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION removeserver
(
	idserv Serveur.id_server%TYPE
) RETURNS void AS $$
BEGIN
	INSERT INTO purge
	VALUES (idserv,current_date);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION setroleserver
(
	idserv Serveur.id_server%TYPE,
	rltype CHAR(1),
	rol Serveur.mjrole%TYPE
) RETURNS void AS $$
BEGIN
	IF rltype = 'A' THEN
		UPDATE serveur
		SET adminrole = rol
		WHERE id_server = idserv;
	END IF;
	IF rltype = 'M' THEN
		UPDATE serveur
		SET mjrole = rol
		WHERE id_server = idserv;
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION setprefix
(
	idserv Serveur.id_server%TYPE,
	pref Serveur.prefixx%TYPE
) RETURNS void AS $$
BEGIN
	UPDATE serveur
	SET prefixx = pref
	WHERE id_server = idserv;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION blockword
(
	idserv Serveur.id_server%TYPE,
	word Word_blocklist.content%TYPE
) RETURNS void AS $$
DECLARE
	nbr INT;
BEGIN
	SELECT COUNT(*) INTO nbr FROM word_blocklist
	WHERE (content = word AND id_server = idserv);
	IF nbr = 0 THEN
		INSERT INTO word_blocklist (content,id_server)
		VALUES (word,idserv);
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION unblockword
(
	idserv Serveur.id_server%TYPE,
	word Word_blocklist.content%TYPE
) RETURNS void AS $$
BEGIN
	DELETE FROM word_blocklist
	WHERE (id_server = idserv AND content = word);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION purgeserver
(
	days INT
) RETURNS INT AS $$
DECLARE
	datemin DATE;
	nbr INT;
	line RECORD;
	jdrl RECORD;
	rol RECORD;
BEGIN
	nbr := 0;
	datemin := current_date - days;
	FOR line IN (SELECT * FROM purge WHERE datein < datemin) LOOP
		FOR jdrl IN (SELECT id_server,id_channel FROM JDR WHERE id_server = line.id_server) LOOP
			PERFORM jdrdelete(jdrl.id_server,jdrl.id_channel);
		END LOOP;
		FOR rol IN (SELECT id_role FROM role WHERE id_server = idserv) LOOP
			PERFORM removerole(idserv,rol.id_role);
		END LOOP;
		DELETE FROM keeprole
		WHERE (id_server = line.id_server);
		DELETE FROM word_blocklist
		WHERE (id_server = line.id_server);
		DELETE FROM purge
		WHERE (id_server = line.id_server);
		DELETE FROM serveur
		WHERE (id_server = line.id_server);
		nbr := nbr + 1;
	END LOOP;
	RETURN nbr;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION JDRextend
(
	idserv JDR.id_server%TYPE,
	src JDR.id_channel%TYPE,
	target JDR.id_channel%TYPE
) RETURNS void AS $$
DECLARE
	nbr INT;
	mj MEMBRE.id_member%TYPE;
BEGIN
	SELECT COUNT(*) INTO nbr FROM jdr
	WHERE id_server = idserv AND id_channel = target;
	IF nbr <> 0 THEN
		PERFORM JDRdelete(idserv,target);
	END IF;
	SELECT id_member INTO mj FROM jdr
	WHERE id_server = idserv AND id_channel = src;
	PERFORM JDRcreate(idserv,target,mj);
	INSERT INTO JDRextension
	VALUES (idserv,src,target);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION JDRstopextend
(
	idserv JDR.id_server%TYPE,
	src JDR.id_channel%TYPE,
	target JDR.id_channel%TYPE
) RETURNS void AS $$
BEGIN
	DELETE FROM JDRextension
	WHERE id_server = idserv AND id_src = src AND id_target = target;
	PERFORM JDRdelete(idserv,target);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION JDRstopallextend
(
	idserv JDR.id_server%TYPE,
	src JDR.id_channel%TYPE
) RETURNS void AS $$
DECLARE
	line RECORD;
BEGIN
	FOR line IN (SELECT id_target FROM JDRextension WHERE id_server = idserv AND id_src = src) LOOP
		PERFORM JDRstopextend(idserv,src,line.id_target);
	END LOOP;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_character
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS SETOF Characterr AS $$
DECLARE
	nbr INT;
	src JDR.id_channel%TYPE;
BEGIN
	SELECT COUNT(*) INTO nbr FROM JDRextension
	WHERE (id_server = idserv AND id_target = idchan);
	IF nbr = 0 THEN
		RETURN QUERY
		SELECT * FROM Characterr
		WHERE charkey = dbkey AND id_server = idserv AND id_channel = idchan;
	ELSE
		SELECT id_src INTO src FROM JDRextension
		WHERE (id_server = idserv AND id_target = idchan);
		RETURN QUERY
		SELECT * FROM Characterr
		WHERE charkey = dbkey AND id_server = idserv AND id_channel = src;
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_allcharacter
(
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS SETOF Characterr AS $$
DECLARE
	nbr INT;
	src JDR.id_channel%TYPE;
BEGIN
	SELECT COUNT(*) INTO nbr FROM JDRextension
	WHERE (id_server = idserv AND id_target = idchan);
	IF nbr = 0 THEN
		RETURN QUERY
		SELECT * FROM Characterr
		WHERE id_server = idserv AND id_channel = idchan;
	ELSE
		SELECT id_src INTO src FROM JDRextension
		WHERE (id_server = idserv AND id_target = idchan);
		RETURN QUERY
		SELECT * FROM Characterr
		WHERE id_server = idserv AND id_channel = src;
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_jdr
(
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS SETOF JDR AS $$
DECLARE
	nbr INT;
	src JDR.id_channel%TYPE;
BEGIN
	SELECT COUNT(*) INTO nbr FROM JDRextension
	WHERE (id_server = idserv AND id_target = idchan);
	IF nbr = 0 THEN
		RETURN QUERY
		SELECT * FROM JDR
		WHERE id_server = idserv AND id_channel = idchan;
	ELSE
		SELECT id_src INTO src FROM JDRextension
		WHERE (id_server = idserv AND id_target = idchan);
		RETURN QUERY
		SELECT * FROM JDR
		WHERE id_server = idserv AND id_channel = src;
	END IF;
END;
$$ LANGUAGE plpgsql;

--Warn features
CREATE OR REPLACE FUNCTION warnuser
(
	idmemb Warn.id_member%TYPE,
	idserv Warn.id_server%TYPE
) RETURNS void AS $$
DECLARE
	nbr INT;
	nbr2 INT;
BEGIN
	SELECT COUNT(*) INTO nbr FROM warn
	WHERE id_server = idserv AND id_member = idmemb;
	IF nbr = 0 THEN
		SELECT COUNT(*) INTO nbr2 FROM membre
		WHERE id_member = idmemb;
		IF nbr2 = 0 THEN
			INSERT INTO membre
			VALUES (idmemb,'N');
		END IF;
		INSERT INTO warn
		VALUES(idserv,idmemb,1);
	ELSE
		UPDATE warn
		SET warn_number = warn_number + 1
		WHERE id_server = idserv AND id_member = idmemb;
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION unwarnuser
(
	idmemb Warn.id_member%TYPE,
	idserv Warn.id_server%TYPE
) RETURNS void AS $$
DECLARE
	nbr INT;
BEGIN
	SELECT warn_number INTO nbr FROM warn
	WHERE id_server = idserv AND id_member = idmemb;
	IF nbr = 1 THEN
		DELETE FROM warn
		WHERE id_server = idserv AND id_member = idmemb;
	ELSE
		UPDATE warn
		SET warn_number = warn_number - 1
		WHERE id_server = idserv AND id_member = idmemb;
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION warnconfigure
(
	idserv Warnconfig.id_server%TYPE,
	warns Warnconfig.warn_number%TYPE,
	action Warnconfig.sanction%TYPE
) RETURNS void AS $$
DECLARE
	nbr INT;
BEGIN
	IF LOWER(action) = 'disable' THEN
		DELETE FROM warnconfig
		WHERE (id_server = idserv AND warn_number = warns);
	ELSE
		SELECT COUNT(*) INTO nbr FROM warnconfig
		WHERE (id_server = idserv AND warn_number = warns);
		IF nbr = 0 THEN
			INSERT INTO warnconfig
			VALUES (idserv,warns,action);
		ELSE
			UPDATE warnconfig
			SET sanction = action
			WHERE (id_server = idserv AND warn_number = warns);
		END IF;
	END IF;
END;
$$ LANGUAGE plpgsql;

--Use function for JDR
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
		gm = 'D'
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
	IF LOWER(item) = 'darkpt' THEN
		UPDATE Characterr
		SET dark_points = dark_points - 1,
		karma = -10,
		gm = 'O'
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
END;
$$ LANGUAGE plpgsql;

--finalize features
CREATE OR REPLACE FUNCTION finalizer
(
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS SETOF finalize AS $$
BEGIN
	RETURN QUERY
	SELECT * FROM finalize
	WHERE id_server = idserv AND id_channel = idchan;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION set_finalize_field
(
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	titl finalize.title%TYPE,
	descr finalize.description%TYPE
) RETURNS void AS $$
DECLARE
	nbr INT;
BEGIN
	SELECT COUNT(*) INTO nbr FROM finalize
	WHERE (id_server = idserv AND id_channel = idchan AND title = titl);
	IF nbr = 0 THEN
		INSERT INTO finalize
		VALUES (idserv,idchan,titl,descr);
	ELSE
		UPDATE finalize
		SET description = descr
		WHERE (id_server = idserv AND id_channel = idchan AND title = titl);
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION del_finalize_field
(
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	titl finalize.title%TYPE
) RETURNS void AS $$
BEGIN
	DELETE FROM finalize
	WHERE (id_server = idserv AND id_channel = idchan AND title = titl);
END;
$$ LANGUAGE plpgsql;