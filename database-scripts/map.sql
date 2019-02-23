CREATE TABLE public.Maptoken(
  id_server     VARCHAR(25)     ,
  id_channel    VARCHAR(25)     ,
  name          VARCHAR(25)     ,
  x             INT             ,
  y             INT             ,
  z             INT             ,
  CONSTRAINT prk_constraint_maptoken PRIMARY KEY (id_server,id_channel,name)
)WITHOUT OIDS;

CREATE TABLE public.Tokenarea(
  id_shape      SERIAL          ,
  id_server     VARCHAR(25)     ,
  id_channel    VARCHAR(25)     ,
  token         VARCHAR(25)     ,
  shape         INT             ,
  dx            INT             ,
  dy            INT             ,
  dz            INT             ,
  param         VARCHAR(100)    ,
  CONSTRAINT prk_constraint_tokenarea PRIMARY KEY (id_shape)
)WITHOUT OIDS;

ALTER TABLE public.Maptoken ADD CONSTRAINT FK_maptoken_jdr FOREIGN KEY (id_server,id_channel) REFERENCES public.JDR(id_server,id_channel);
ALTER TABLE public.Tokenarea ADD CONSTRAINT FK_tokenarea_map FOREIGN KEY (id_server,id_channel,token) REFERENCES public.Maptoken(id_server,id_channel,name);

--FUNCTION
CREATE OR REPLACE FUNCTION addtoken
(
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
  tkname Maptoken.name%TYPE,
  tkx Maptoken.x%TYPE,
  tky Maptoken.y%TYPE,
  tkz Maptoken.z%TYPE
) RETURNS void AS $$
BEGIN
	INSERT INTO Maptoken
	VALUES (idserv,idchan,tkname,x,y,z);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION clearmap
(
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS void AS $$
BEGIN
	DELETE FROM Tokenarea
  WHERE id_server = idserv AND id_channel = idchan;
  DELETE FROM Maptoken
  WHERE id_server = idserv AND id_channel = idchan;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION rmtoken
(
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
  tkname Maptoken.name%TYPE
) RETURNS void AS $$
BEGIN
  DELETE FROM Tokenarea
  WHERE id_server = idserv AND id_channel = idchan AND token = tkname;
  DELETE FROM Maptoken
  WHERE id_server = idserv AND id_channel = idchan AND name = tkname;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION movetoken
(
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
  tkname Maptoken.name%TYPE,
  dx INT,
  dy INT,
  dz INT
) RETURNS void AS $$
BEGIN
  UPDATE Maptoken
  SET x = x+dx,
  y = y+dy,
  z = z+dz
  WHERE id_server = idserv AND id_channel = idchan AND name = tkname;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION addeffect
(
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
  tkname Maptoken.name%TYPE,
  effshape Tokenarea.shape%TYPE,
  effdx Tokenarea.dx%TYPE,
  effdy Tokenarea.dy%TYPE,
  effdz Tokenarea.dz%TYPE,
  effparameters Tokenarea.param%TYPE
) RETURNS INT AS $$
DECLARE
  areaid INT;
BEGIN
  INSERT INTO Tokenarea (id_server,id_channel,token,shape,dx,dy,dz,param)
  VALUES (idserv,idchan,tkname,effshape,effdx,effdy,effdz,effparameters);
  SELECT MAX(id_shape) INTO areaid FROM Tokenarea
  WHERE (id_server = idserv AND id_channel = idchan AND token = tkname);
  RETURN areaid;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION rmeffect
(
	idshape Tokenarea.id_shape%TYPE
) RETURNS void AS $$
BEGIN
  DELETE FROM Tokenarea
  WHERE id_shape = idshape;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION cleareffect
(
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
  tkname Maptoken.name%TYPE
) RETURNS void AS $$
BEGIN
  DELETE FROM Tokenarea
  WHERE id_server = idserv AND id_channel = idchan AND token = tkname;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION getmaptoken
(
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
  tkname Maptoken.name%TYPE
) RETURNS SETOF Maptoken AS $$
BEGIN
  RETURN QUERY
  SELECT * FROM Maptoken
  WHERE id_server = idserv AND id_channel = idchan AND name = tkname;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION gettokeneffects
(
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE,
  tkname Maptoken.name%TYPE
) RETURNS SETOF Tokenarea AS $$
BEGIN
  RETURN QUERY
  SELECT * FROM Tokenarea
  WHERE id_server = idserv AND id_channel = idchan AND token = tkname;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION getmap
(
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS SETOF Maptoken AS $$
BEGIN
  RETURN QUERY
  SELECT * FROM Maptoken
  WHERE id_server = idserv AND id_channel = idchan;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION getmapeffect
(
	idserv JDR.id_server%TYPE,
	idchan JDR.id_channel%TYPE
) RETURNS SETOF Maptoken AS $$
BEGIN
  RETURN QUERY
  SELECT * FROM Maptoken
  WHERE id_server = idserv AND id_channel = idchan;
END;
$$ LANGUAGE plpgsql;
