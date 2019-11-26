-- >> INVENTORY <<
DROP TABLE Items CASCADE;
DROP TABLE contient;
DROP TRIGGER IF EXISTS delcharacter ON Characterr;

CREATE TABLE public.Items(
	id_inventory   INT,
  item_name      VARCHAR(100),
	qte			       INT CONSTRAINT item_qte_null NOT NULL CONSTRAINT item_qte_check CHECK (qte > 0) ,
  weight         FLOAT CONSTRAINT item_weight_null NOT NULL CONSTRAINT item_weight_check CHECK (weight > 0),
	CONSTRAINT prk_constraint_item PRIMARY KEY (id_inventory,item_name)
)WITHOUT OIDS;

ALTER TABLE public.Items ADD CONSTRAINT FK_items_inventory FOREIGN KEY (id_inventory) REFERENCES public.Inventaire(id_inventory);

-- Reimplementation of broken features
CREATE OR REPLACE FUNCTION delCharacter () RETURNS TRIGGER AS $delCharacter$
BEGIN
	DELETE FROM items
	WHERE id_inventory = old.id_inventory;
	DELETE FROM inventaire
	WHERE id_inventory = old.id_inventory;
	RETURN old;
END;
$delCharacter$ LANGUAGE plpgsql;

CREATE TRIGGER delCharacter
AFTER DELETE ON Characterr
FOR EACH ROW
EXECUTE PROCEDURE delCharacter();

CREATE OR REPLACE FUNCTION inventory_Manager () RETURNS TRIGGER AS $inventory_Manager$
DECLARE
	poids ITEMS.WEIGHT%TYPE;
  poids_max ITEMS.WEIGHT%TYPE;
BEGIN
	IF TG_OP = 'DELETE' OR TG_OP = 'UPDATE' THEN
		SELECT size_ INTO poids FROM inventaire
		WHERE id_inventory = old.id_inventory;
		poids := poids - (old.qte * old.weight);
		UPDATE inventaire
		SET size_ = poids
		WHERE id_inventory = old.id_inventory;
	END IF;
	IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
		SELECT size_ INTO poids FROM inventaire
		WHERE id_inventory = new.id_inventory;
		poids := poids + (new.qte * new.weight);
		SELECT size_max INTO poids_max FROM inventaire
		WHERE id_inventory = new.id_inventory;
		--IF poids > poids_max THEN
			--RAISE EXCEPTION 'Inventory size exceeded';
		--ELSE
		UPDATE inventaire
		SET size_ = poids
		WHERE id_inventory = new.id_inventory;
		--END IF;
	END IF;
	IF TG_OP = 'DELETE' THEN
		RETURN old;
	ELSE
		RETURN new;
	END IF;
END;
$inventory_Manager$ LANGUAGE plpgsql;

CREATE TRIGGER inventory_Manager
BEFORE INSERT OR UPDATE OR DELETE ON Items
FOR EACH ROW
EXECUTE PROCEDURE inventory_Manager();

CREATE OR REPLACE FUNCTION additem
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	itname Items.item_name%TYPE,
	quantite INT,
  poids Items.weight%TYPE
) RETURNS void AS $$
DECLARE
	inv Inventaire.id_inventory%TYPE;
	nbr INT;
BEGIN
  SELECT id_inventory INTO inv FROM Characterr
  WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	SELECT COUNT(*) INTO nbr FROM Items
	WHERE (item_name LIKE LOWER(itname) AND id_inventory = inv);
	IF nbr = 0 THEN
		INSERT INTO Items
		VALUES (inv,itname,quantite,poids);
	ELSE
		UPDATE Items
		SET qte = qte + quantite
		WHERE (item_name = itname AND id_inventory = inv);
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION removeitem
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	itname Items.item_name%TYPE,
	quantite INT
) RETURNS void AS $$
DECLARE
	inv Inventaire.id_inventory%TYPE;
	nbr INT;
BEGIN
	SELECT id_inventory INTO inv FROM Characterr
	WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	SELECT qte INTO nbr FROM Items
	WHERE (id_inventory = inv AND item_name = itname);
	nbr := nbr - quantite;
	IF nbr <= 0 THEN
		DELETE FROM Items
		WHERE (item_name = itname AND id_inventory = inv);
	ELSE
		UPDATE Items
		SET qte = nbr
		WHERE (item_name = itname AND id_inventory = inv);
	END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION forceinvcalc () RETURNS void AS $$
DECLARE
	poids INVENTAIRE.SIZE_%TYPE;
	inv RECORD;
	item RECORD;
	po Characterr.argent%TYPE;
BEGIN
	FOR inv IN (SELECT id_inventory FROM inventaire) LOOP
		SELECT argent INTO po FROM characterr WHERE id_inventory = inv.id_inventory;
		poids := CEIL(po/5000);
		FOR item IN (SELECT item_name,qte,weight FROM Items WHERE id_inventory = inv.id_inventory) LOOP
			poids := poids + (item.qte * item.weight);
		END LOOP;
		UPDATE inventaire
		SET size_ = poids
		WHERE id_inventory = inv.id_inventory;
	END LOOP;
END;
$$ LANGUAGE plpgsql;

-- >> XP <<
ALTER TABLE public.Characterr ADD COLUMN xp INT;

-- Perform update of characterr
DO $$
<<xpupdate>>
BEGIN
  UPDATE Characterr
	SET xp = 0;
END xpupdate $$;

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
BEGIN
	INSERT INTO inventaire (charkey)
	VALUES (dbkey);
	SELECT MAX(id_inventory) INTO inv FROM inventaire
	WHERE charkey = dbkey;
	--update here
	INSERT INTO Characterr
	VALUES (dbkey, dbkey, '', 1, 1, 1, 1, 1, 50, 50, 50, 50, 0, 0, 0, 1, 1, 3, 100, 0, 0, 0, 0, 0, 0, 0, idserv, idchan, 'O', 'O', inv, 'NULL',false,cl,false,0);
	--end of update
END;
$$ LANGUAGE plpgsql;

-- new fonctions
CREATE OR REPLACE FUNCTION charxp
(
	dbkey Characterr.charkey%TYPE,
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
	amount Characterr.xp%TYPE,
	allowlevelup BOOL
) RETURNS INT AS $$
DECLARE
	earnedlvl INT;
	curxp Characterr.xp%TYPE;
BEGIN
	earnedlvl := 0;
	IF allowlevelup THEN
		SELECT xp INTO curxp FROM Characterr
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
		earnedlvl := FLOOR((curxp + amount) / 100);
		amount := curxp + amount - (earnedlvl * 100);
		UPDATE Characterr
		SET xp = amount
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	ELSE
		UPDATE Characterr
		SET xp = xp + amount
		WHERE (charkey = dbkey AND id_server = idserv AND id_channel = idchan);
	END IF;
	RETURN earnedlvl;
END;
$$ LANGUAGE plpgsql;
