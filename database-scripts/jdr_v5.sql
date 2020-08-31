-- Add new gamemods
INSERT INTO Gamemods VALUES ('I', 'Illumination'), ('S', 'Sepulchral');


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
