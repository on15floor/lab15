create table car_works_done
(
    id                integer      not null
        primary key autoincrement,
    car_id        integer not null,
    mileage       integer      not null,
    work_date     date         not null,
    work_name     varchar(300) not null,
    work_type     varchar(300) not null,
    price         integer,
    currency      varchar(10)
);
