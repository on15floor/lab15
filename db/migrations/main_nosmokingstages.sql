create table main_nosmokingstages
(
    id         integer      not null
        primary key autoincrement,
    name       varchar(100) not null,
    time       real         not null,
    time_descr varchar(100) not null,
    text       text         not null
);
