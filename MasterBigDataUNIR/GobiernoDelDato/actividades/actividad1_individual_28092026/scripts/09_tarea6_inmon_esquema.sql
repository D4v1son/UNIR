/*
Actividad 1 - Gobierno del dato: Parte II-B, Tarea 6
Modelo Inmon en 3FN, sobre los mismos datos de "Licencias_Terrazas_Integradas".

A diferencia del modelo Kimball (Tarea 5), aquí no se repiten ni el nombre del
distrito ni el del barrio en cada fila: se normalizan en tablas separadas
siguiendo su dependencia funcional real (un barrio pertenece a un distrito,
un local pertenece a un barrio), eliminando la redundancia y las dependencias
transitivas.
*/

CREATE DATABASE GobiernoDatoAct1_3FN;
GO
USE GobiernoDatoAct1_3FN;
GO

CREATE TABLE Distrito (
    id_distrito     INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    desc_distrito   VARCHAR(60) NOT NULL UNIQUE
);
GO

CREATE TABLE Barrio (
    id_barrio       INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    id_distrito     INT NOT NULL REFERENCES Distrito(id_distrito),
    desc_barrio     VARCHAR(60) NOT NULL,
    CONSTRAINT UQ_Barrio UNIQUE (id_distrito, desc_barrio)
);
GO

CREATE TABLE Local (
    id_local        VARCHAR(20) NOT NULL PRIMARY KEY,
    id_barrio       INT NOT NULL REFERENCES Barrio(id_barrio)
);
GO

CREATE TABLE Terraza (
    id_terraza              INT NOT NULL PRIMARY KEY,
    id_local                VARCHAR(20) NOT NULL REFERENCES Local(id_local),
    desc_periodo_terraza    VARCHAR(20),
    desc_situacion_terraza  VARCHAR(40),
    Superficie_ES           DECIMAL(10,2),
    Superficie_RA           DECIMAL(10,2),
    Superficie_TO           DECIMAL(10,2) NOT NULL,
    mesas_es                SMALLINT,
    sillas_es               SMALLINT
);
GO

CREATE TABLE TipoLicencia (
    id_tipo_licencia    INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    desc_tipo_licencia  VARCHAR(100) NOT NULL UNIQUE
);
GO

CREATE TABLE SituacionLicencia (
    id_situacion_licencia          INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    desc_tipo_situacion_licencia   VARCHAR(100) NOT NULL UNIQUE
);
GO

CREATE TABLE Licencia (
    id_local                VARCHAR(20) NOT NULL REFERENCES Local(id_local),
    ref_licencia            VARCHAR(40) NOT NULL,
    id_tipo_licencia        INT NOT NULL REFERENCES TipoLicencia(id_tipo_licencia),
    id_situacion_licencia   INT NOT NULL REFERENCES SituacionLicencia(id_situacion_licencia),
    Fecha_Dec_Lic           DATE,
    CONSTRAINT PK_Licencia PRIMARY KEY (id_local, ref_licencia)
);
GO

CREATE INDEX IX_Barrio_Local     ON Local(id_barrio);
CREATE INDEX IX_Terraza_Local    ON Terraza(id_local);
CREATE INDEX IX_Licencia_Local   ON Licencia(id_local);
GO
