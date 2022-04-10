create table main_chords
(
    id         integer      not null
        primary key autoincrement,
    instrument varchar(100) not null,
    song_text  text         not null,
    date       datetime     not null,
    song_name  varchar(100) not null
);
