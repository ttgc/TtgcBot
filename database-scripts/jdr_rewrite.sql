DROP TABLE Items CASCADE;

CREATE TABLE public.Items(
	id_inventory   INT,
  item_name      VARCHAR(100),
	qte			       INT CONSTRAINT item_qte_null NOT NULL CONSTRAINT item_qte_check CHECK (qte > 0) ,
  weight         FLOAT CONSTRAINT item_weight_null NOT NULL CONSTRAINT item_weight_check (weight > 0),
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
		IF poids > poids_max THEN
			RAISE EXCEPTION 'Inventory size exceeded';
		ELSE
			UPDATE inventaire
			SET size_ = poids
			WHERE id_inventory = new.id_inventory;
		END IF;
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
		WHERE (item_name = item AND id_inventory = inv);
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
