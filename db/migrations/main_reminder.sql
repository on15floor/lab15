create table main_reminders
(
    id                integer      not null
        primary key autoincrement,
    reminder          varchar(100) not null,
    day               varchar(100) not null,
    month             varchar(100) not null,
    active            bool         not null
);
