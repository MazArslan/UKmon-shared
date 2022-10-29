/* DDL to create singles-table in mariadb */

use ukmon;

create table singles(
    ver varchar(6),
    Y smallint,
    M tinyint, 
    D tinyint,
    h tinyint,
    mi tinyint,
    s float,
    Mag float,
    Dur float,
    Az1 float,
    Alt1 float,
    Az2 float,
    Alt2 float,
    Ra1 float,
    Dec1 float,
    Ra2 float,
    Dec2 float,
    ID varchar(6),
    Longi float,
    Lati float,
    Alt float,
    Tz tinyint,
    AngVel float,
    Shwr varchar(6),
    filname varchar(64),
    Dtstamp float);

create table matches(
    _dbver varchar(6),
    _num tinyint,
    _localtime varchar(18), 
    _mjd float, 
    _sol float, 
    _ID1 varchar(16), 
    _ID2 varchar(4), 
    _amag float, 
    _ra_o float, 
    _dc_o float,
    _ra_t float,
    _dc_t float,
    _elng float,
    _elat float,
    _vo float,
    _vi float,
    _vg float,
    _vs float,
    _a float,
    _q float,
    _e float,
    _p float,
    _peri float,
    _node float,
    _incl FLOAT, 
    _stream varchar(16),
    _dr FLOAT,
    _dvpct FLOAT,
    _mag FLOAT,
    _Qo FLOAT,
    _dur FLOAT,
    _av FLOAT, 
    _Voa FLOAT, 
    _Pra FLOAT, 
    _Pdc FLOAT, 
    _GPlng FLOAT, 
    _GPlat FLOAT, 
    _ra1 FLOAT, 
    _dc1 FLOAT, 
    _az1 FLOAT, 
    _ev1 FLOAT, 
    _lng1 FLOAT, 
    _lat1 FLOAT, 
    _H1 FLOAT, 
    _LD1 FLOAT, 
    _Qr1 FLOAT, 
    _Qd1 FLOAT, 
    _ra2 FLOAT, 
    _dc2 FLOAT, 
    _lng2 FLOAT, 
    _lat2 FLOAT, 
    _H2 FLOAT, 
    _LD2 FLOAT, 
    _Qr2 FLOAT, 
    _Qd2 FLOAT, 
    _LD21 FLOAT, 
    _az1r FLOAT, 
    _ev1r FLOAT, 
    _evro FLOAT, 
    _evrt FLOAT, 
    _Nts FLOAT, 
    _Nos FLOAT, 
    _leap FLOAT, 
    _rstar FLOAT, 
    _ddeg FLOAT, 
    _cdeg FLOAT, 
    _drop FLOAT, 
    _inout FLOAT, 
    _tme FLOAT, 
    _dt FLOAT, 
    _GD FLOAT, 
    _Qc FLOAT, 
    _dGP FLOAT, 
    _Gmpct FLOAT, 
    _dv12pct FLOAT, 
    _zmv FLOAT, 
    _Ed FLOAT, 
    _Ex FLOAT, 
    _QA FLOAT, 
    _Y_ut smallint, 
    _M_ut tinyint, 
    _D_ut tinyint, 
    _h_ut tinyint, 
    _mi_ut tinyint, 
    _s_ut FLOAT, 
    _Nops FLOAT, 
    _Qp FLOAT, 
    _pdeg_sd FLOAT, 
    _rao_sd FLOAT, 
    _dco_sd FLOAT, 
    _vo_sd FLOAT, 
    _rat_sd FLOAT, 
    _dct_sd FLOAT, 
    _vg_sd FLOAT, 
    _a_sd FLOAT, 
    _1_a FLOAT, 
    _1_a_sd FLOAT, 
    _q_sd FLOAT, 
    _e_sd FLOAT, 
    _peri_sd FLOAT, 
    _node_sd FLOAT, 
    _incl_sd FLOAT, 
    _Er_sd FLOAT, 
    _ZF FLOAT, 
    _OH FLOAT, 
    _ZHR FLOAT,
    Dummy FLOAT,
    d2 FLOAT,
    d3 FLOAT,
    dtstamp FLOAT,
    orbname varchar(32),
    src varchar(12),
    urlstr varchar(128),
    imgstr varchar(160),
    dateval varchar(16),
    mjd float,
    id varchar(16),
    iau smallint,
    shwrname varchar(128),
    mass float,
    pi float,
    Q float,
    true_anom float,
    EA float,
    MA float,
    Tj float,
    T float,
    last_peri varchar(16),
    jacchia1 float,
    Jacchia2 float,
    numstats tinyint,
    stations varchar(256),
    isfb varchar(6)
    );