CREATE FUNCTION initJDR () RETURNS TRIGGER AS $initJDR$
BEGIN
	IF INSERTING THEN
		new.creation := sysdate();
		new.PJs := 0;
	END IF;
	IF UPDATING THEN
		new.creation := old.creation;
		UPDATE JDRextension
		SET id_src = new.id_channel
		WHERE id_server = new.id_server AND id_src = old.id_channel;
	END IF;
	IF DELETING THEN
		DELETE FROM JDRextension
		WHERE id_server = old.id_server AND id_src = old.id_channel;
	END IF;
END;
$initJDR$ LANGUAGE plpgsql;

CREATE TRIGGER initJDR
BEFORE INSERT OR UPDATE OR DELETE ON JDR
FOR EACH ROW
EXECUTE PROCEDURE initJDR();

CREATE FUNCTION initCharacter () RETURNS TRIGGER AS $initCharacter$
BEGIN
	IF INSERTING OR UPDATING THEN
		UPDATE JDR
		SET PJs = PJs + 1
		WHERE id_server = new.id_server AND id_channel = new.id_channel;
		new.rolled_dice := new.critic_succes + new.critic_fail + new.super_critic_succes + new.super_critic_fail + new.succes + new.fail;
		UPDATE inventaire
		SET size_max = 40*FLOOR(new.force/10)/10
		WHERE charkey = new.charkey;
	END IF;
	IF DELETING OR UPDATING THEN
		UPDATE JDR
		SET PJs = PJs - 1
		WHERE id_server = old.id_server AND id_channel = old.id_channel;
		IF DELETING THEN
			DELETE FROM contient
			WHERE id_inventory = old.id_inventory;
			DELETE FROM inventory
			WHERE id_inventory = old.id_inventory;
		END IF;
		IF UPDATING THEN
			UPDATE inventaire
			SET size_max = 40*FLOOR(new.force/10)/10
			WHERE charkey = old.charkey;
		END IF;
	END IF;
END;
$initCharacter$ LANGUAGE plpgsql;

CREATE TRIGGER initCharacter
BEFORE INSERT OR UPDATE OR DELETE ON Characterr
FOR EACH ROW
EXECUTE PROCEDURE initCharacter();

CREATE FUNCTION inventory_Manager () RETURNS TRIGGER AS $inventory_Manager$
DECLARE
	poids ITEMS.WEIGHT%TYPE;
	it_poids ITEMS.WEIGHT%TYPE;
BEGIN
	IF INSERTING OR UPDATING THEN
		SELECT size_ INTO poids FROM inventaire
		WHERE id_inventory = new.id_inventory;
		SELECT weight INTO it_poids FROM items
		WHERE id_item = new.id_item;
		poids := poids + (new.qte * it_poids);
		SELECT size_max INTO it_poids FROM inventaire
		WHERE id_inventory = new.id_inventory;
		IF CEIL(poids) > it_poids THEN
			RAISE EXCEPTION 'Inventory size exceeded';
		ELSE
			UPDATE inventaire
			SET size_ = CEIL(poids)
			WHERE id_inventory = new.id_inventory;
		END IF;
	END IF;
	IF DELETING OR UPDATING THEN
		SELECT size_ INTO poids FROM inventaire
		WHERE id_inventory = old.id_inventory;
		SELECT weight INTO it_poids FROM items
		WHERE id_item = old.id_item;
		poids := poids - (old.qte * it_poids);
		UPDATE inventaire
		SET size_ = CEIL(poids)
		WHERE id_inventory = old.id_inventory;
	END IF;
END;
$inventory_Manager$ LANGUAGE plpgsql;

CREATE TRIGGER inventory_Manager
BEFORE INSERT OR UPDATE OR DELETE ON contient
FOR EACH ROW
EXECUTE PROCEDURE inventory_Manager();

CREATE FUNCTION initInventory () RETURNS TRIGGER AS $initInventory$
BEGIN
	new.size_ := 0;
	new.size_max := 20;
END;
$initInventory$ LANGUAGE plpgsql;

CREATE TRIGGER initInventory
BEFORE INSERT ON inventaire
FOR EACH ROW
EXECUTE PROCEDURE initInventory();

CREATE FUNCTION purge_date_check () RETURNS TRIGGER AS $purge_date_check$
BEGIN
	IF INSERTING THEN
		new.datein := sysdate();
	ELSE
		new.datein = old.datein;
	END IF;
END;
$purge_date_check$ LANGUAGE plpgsql;

CREATE TRIGGER purge_date_check
BEFORE INSERT OR UPDATE ON purge
FOR EACH ROW
EXECUTE PROCEDURE purge_date_check();

CREATE FUNCTION item_updater () RETURNS TRIGGER AS $item_updater$
BEGIN
	new.weight := old.weight;
END;
$item_updater$ LANGUAGE plpgsql;

CREATE TRIGGER item_updater
BEFORE UPDATE ON items
FOR EACH ROW
EXECUTE PROCEDURE item_updater();

CREATE FUNCTION extendinit () RETURNS TRIGGER AS $extendinit$
DECLARE
	nbr INT;
	mj JDR.id_member%TYPE;
BEGIN
	IF DELETING OR UPDATING THEN
		PERFORM JDRdelete(old.id_server, old.id_target);
	END IF;
	IF INSERTING OR UPDATING THEN
		SELECT COUNT(*) INTO nbr FROM JDR
		WHERE (id_server = new.id_server AND id_channel = new.id_target);
		SELECT id_member INTO mj FROM JDR
		WHERE (id_server = new.id_server AND id_channel = new.id_src);
		IF nbr > 0 THEN
			PERFORM JDRdelete(new.id_server, new.id_target);
		END IF;
		PERFORM JDRcreate(new.id_server, new.id_target, mj);
	END IF;
END;
$extendinit$ LANGUAGE plpgsql;

CREATE TRIGGER extendinit
BEFORE INSERT OR UPDATE OR DELETE ON JDRextension
FOR EACH ROW
EXECUTE PROCEDURE extendinit();