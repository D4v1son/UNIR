/*
Actividad 1 - Gobierno del dato: Parte II-B, Tarea 5
Modelo dimensional (Kimball) en SQL Server, a partir de "Licencias_Terrazas_Integradas".
Esquema en estrella: 1 tabla de hechos + 3 dimensiones.
*/

CREATE DATABASE GobiernoDatoAct1;
GO
USE GobiernoDatoAct1;
GO

-- ================================================================ DIMENSIONES

CREATE TABLE Dim_Fecha (
    id_fecha        INT           NOT NULL PRIMARY KEY,   -- formato YYYYMMDD
    fecha           DATE          NOT NULL,
    dia             TINYINT       NOT NULL,
    mes             TINYINT       NOT NULL,
    nombre_mes      VARCHAR(20)   NOT NULL,
    trimestre       TINYINT       NOT NULL,
    anio            SMALLINT      NOT NULL
);
GO

CREATE TABLE Dim_Ubicacion (
    id_ubicacion        INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    desc_distrito_local VARCHAR(60)  NOT NULL,
    desc_barrio_local   VARCHAR(60)  NOT NULL,
    CONSTRAINT UQ_Ubicacion UNIQUE (desc_distrito_local, desc_barrio_local)
);
GO

CREATE TABLE Dim_TipoLicencia (
    id_tipo_licencia             INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    desc_tipo_licencia           VARCHAR(100) NOT NULL,
    desc_tipo_situacion_licencia VARCHAR(100) NOT NULL,
    CONSTRAINT UQ_TipoLicencia UNIQUE (desc_tipo_licencia, desc_tipo_situacion_licencia)
);
GO

-- ================================================================ HECHOS

CREATE TABLE Hechos_Terrazas (
    id_hecho          BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    id_fecha          INT    NOT NULL REFERENCES Dim_Fecha(id_fecha),
    id_ubicacion      INT    NOT NULL REFERENCES Dim_Ubicacion(id_ubicacion),
    id_tipo_licencia  INT    NOT NULL REFERENCES Dim_TipoLicencia(id_tipo_licencia),
    id_terraza        INT    NOT NULL,
    id_local          VARCHAR(20) NOT NULL,
    ref_licencia      VARCHAR(40) NOT NULL,
    Superficie_TO     DECIMAL(10,2) NOT NULL,   -- medida principal
    mesas_es          SMALLINT,
    sillas_es         SMALLINT
);
GO

CREATE INDEX IX_Hechos_Fecha     ON Hechos_Terrazas(id_fecha);
CREATE INDEX IX_Hechos_Ubicacion ON Hechos_Terrazas(id_ubicacion);
CREATE INDEX IX_Hechos_Tipo      ON Hechos_Terrazas(id_tipo_licencia);
GO
