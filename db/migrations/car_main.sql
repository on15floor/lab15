create table car_main
(
    id                integer      not null
        primary key autoincrement,
    brand         varchar(100) not null,
    model         varchar(100) not null,
    year          integer      not null,
    vin           varchar(100) not null,
    purchase_date date         not null,
    price         integer      not null,
    currency      varchar(10)  not null,
    active        bool         not null,
    comment       text
);
