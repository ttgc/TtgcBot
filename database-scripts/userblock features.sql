CREATE TABLE public.User_Blocklist(
	user_number SERIAL CONSTRAINT userblock_number_null NOT NULL ,
	username    VARCHAR (25)  ,
	id_server   VARCHAR (25)  ,
	CONSTRAINT prk_constraint_userblock PRIMARY KEY (user_number)
)WITHOUT OIDS;

ALTER TABLE public.User_Blocklist ADD CONSTRAINT FK_userblock_idserv FOREIGN KEY (id_server) REFERENCES public.Serveur(id_server);

CREATE OR REPLACE FUNCTION userblock
(
	usr USER_BLOCKLIST.USERNAME%TYPE,
	idserv SERVEUR.ID_SERVER%TYPE
) RETURNS INT AS $$
DECLARE
	id INT;
BEGIN
	INSERT INTO User_Blocklist (username,id_server)
	VALUES (usr,idserv);
	SELECT MAX(user_number) INTO id FROM User_Blocklist
	WHERE (username = usr AND id_server = idserv);
	RETURN id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION userunblock
(
	id USER_BLOCKLIST.USER_NUMBER%TYPE
) RETURNS void AS $$
BEGIN
	DELETE FROM User_Blocklist
	WHERE user_number = id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION find_userblocked
(
	usr USER_BLOCKLIST.USERNAME%TYPE,
	idserv SERVEUR.ID_SERVER%TYPE
) RETURNS INT AS $$
DECLARE
	id INT;
BEGIN
	SELECT MIN(user_number) INTO id FROM User_Blocklist
	WHERE (username = usr AND id_server = idserv);
	RETURN id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION userblock_list
(
	idserv SERVEUR.ID_SERVER%TYPE
) RETURNS SETOF User_Blocklist AS $$
BEGIN
	RETURN QUERY
	SELECT username FROM User_Blocklist
	WHERE (id_server = idserv);
END;
$$ LANGUAGE plpgsql;