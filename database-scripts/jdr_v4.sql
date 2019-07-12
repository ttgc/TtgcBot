-- Add and rename some class
UPDATE Classe SET nom = 'Enchanteur' WHERE id_race = 6;
INSERT INTO Classe(id_race,nom) VALUES (6,'Protecteur');
UPDATE Classe SET nom = 'Ensorceleuse' WHERE id_race = 4 AND nom = 'Succube libre';

-- Add stats
ALTER TABLE public.Characterr ADD COLUMN prec INT;
ALTER TABLE public.Characterr ADD COLUMN luck INT;
ALTER TABLE public.Characterr ADD CONSTRAINT character_prec_check CHECK (prec > 0 AND prec <= 100);
ALTER TABLE public.Characterr ADD CONSTRAINT character_luck_check CHECK (luck > 0 AND luck <= 100);

-- Perform update of characterr
UPDATE Characterr SET prec = 50, luck = 50;

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
	VALUES (dbkey, dbkey, '', 1, 1, 1, 1, 1, 50, 50, 50, 50, 0, 0, 0, 1, 1, 3, 100, 0, 0, 0, 0, 0, 0, 0, idserv, idchan, 'O', 'O', inv, 'NULL',false,cl,false,0,50,50);
	--end of update
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
	-- update here
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
