create table car_works_regular
(
    id                integer      not null
        primary key autoincrement,
    car_id        integer      not null,
    mileage       integer      not null,
    month         integer      not null,
    work_name     varchar(300) not null
);
