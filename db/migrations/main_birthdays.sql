create table main_birthdays
(
    id                integer      not null
        primary key autoincrement,
    name              varchar(100) not null,
    male              bool         not null,
    birthdate         date         not null,
    birthdate_checked bool         not null,
    comment           text         not null
);
