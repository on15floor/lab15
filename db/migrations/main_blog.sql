create table main_blog
(
    id    integer      not null
        primary key autoincrement,
    icon  text         not null,
    title varchar(100) not null,
    intro varchar(300) not null,
    text  text         not null,
    date  datetime     not null
);
