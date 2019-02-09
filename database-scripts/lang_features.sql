CREATE TABLE public.Langlist(
	langcode CHAR (2) CONSTRAINT langlist_langcode_null NOT NULL ,
	langname VARCHAR (10) CONSTRAINT langlist_langname_null NOT NULL ,
	CONSTRAINT prk_constraint_langlist PRIMARY KEY (langcode)
)WITHOUT OIDS;

ALTER TABLE public.Membre ADD COLUMN lang CHAR(2);
ALTER TABLE public.Membre ADD CONSTRAINT FK_Membre_lang FOREIGN KEY (lang) REFERENCES public.Langlist(langcode);

INSERT INTO Langlist VALUES ('EN','English');
INSERT INTO Langlist VALUES ('FR','French');

CREATE OR REPLACE FUNCTION getlang
(
	idmemb Membre.id_member%TYPE
) RETURNS Langlist.langcode%TYPE AS $$
DECLARE
	nbr INT;
	lg Langlist.langcode%TYPE;
BEGIN
	lg := 'EN';
	SELECT COUNT(*) INTO nbr FROM Membre
	WHERE (id_member = idmemb);
	IF nbr <> 0 THEN
		SELECT lang INTO lg FROM Membre
		WHERE id_member = idmemb;
	END IF;
	RETURN COALESCE(lg,'EN');
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION setlang
(
	idmemb Membre.id_member%TYPE,
	lg Langlist.langcode%TYPE
) RETURNS void AS $$
DECLARE
	nbr INT;
BEGIN
	SELECT COUNT(*) INTO nbr FROM Membre
	WHERE (id_member = idmemb);
	IF nbr = 0 THEN
		INSERT INTO Membre
		VALUES (idmemb,'N',lg);
	ELSE
		UPDATE Membre
		SET lang = lg
		WHERE id_member = idmemb;
	END IF;
END;
$$ LANGUAGE plpgsql;