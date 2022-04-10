create table api_apptime
(
    id           integer     not null
        primary key autoincrement,
    game_name    text        not null,
    price_old    varchar(10) not null,
    price_new    varchar(10) not null,
    sale_percent varchar(10) not null,
    cover        text        not null,
    app_link     text        not null,
    date         datetime    not null
);
