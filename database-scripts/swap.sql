ALTER TABLE public.Characterr ADD COLUMN linked BOOL;

CREATE OR REPLACE FUNCTION charselect
(
  dbkey Characterr.charkey%TYPE,
  idserv JDR.id_server%TYPE,
  idchan JDR.id_channel%TYPE,
  idmemb Characterr.id_member%TYPE
) RETURNS void AS $$
BEGIN
  UPDATE Characterr
  SET linked = false
  WHERE (id_server = idserv AND id_channel = idchan AND id_member = idmemb);
  UPDATE Characterr
  SET linked = true
  WHERE (id_server = idserv AND id_channel = idchan AND id_member = idmemb AND charkey = dbkey);
END;
$$ LANGUAGE plpgsql;

--update charlink
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
  --update here
  PERFORM charselect(dbkey,idserv,idchan,idmemb);
  --end of update
END;
$$ LANGUAGE plpgsql;

--Perform update of characterr
DO $$
<<swapupdate>>
DECLARE
  nbr INT;
BEGIN
  SELECT COUNT(*) INTO nbr FROM
  (SELECT id_member,id_server,id_channel,COUNT(charkey) AS nbr FROM Characterr
  WHERE id_member <> 'NULL'
  GROUP BY id_member,id_server,id_channel HAVING COUNT(charkey) >1
  ORDER BY id_member) AS rows;
  RAISE NOTICE 'Number of double characters assigned to the same member : %', nbr;
  IF nbr = 0 THEN
    UPDATE Characterr
    SET linked = true
    WHERE id_member <> 'NULL';
    RAISE NOTICE 'Update performed';
  END IF;
END swapupdate $$;
