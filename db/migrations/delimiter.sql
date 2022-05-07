CREATE TABLE best_scores(
    [id] [INTEGER] PRIMARY KEY AUTOINCREMENT NOT NULL,
    [date] DATE DEFAULT (DATETIME('now')),
    [user_id] [NVARCHAR](30) NOT NULL,
    [user_name] [NVARCHAR](100) NOT NULL,
    [best_score] [INTEGER] NOT NULL
);

INSERT INTO best_scores
    ( user_id, user_name, best_score)
VALUES
    ('user_2022110000000', 'Иван', 100),
    ('user_2022110000001', 'Петр', 150),
    ('user_2022110000002', 'Александр', 200),
    ('user_2022110000003', 'Михаил', 250),
    ('user_2022110000004', 'Лев', 300),
    ('user_2022110000005', 'Дмитрий', 350),
    ('user_2022110000006', 'Аркадий', 400),
    ('user_2022110000007', 'Владлен', 450),
    ('user_2022110000008', 'Артем', 500),
    ('user_2022110000009', 'Виктор', 550),
    ('user_2022110000010', 'Денис', 600),
    ('user_2022110000011', 'Роман', 650),
    ('user_2022110000012', 'Никита', 700),
    ('user_2022110000013', 'Егор', 750),
    ('user_2022110000014', 'Тимур', 800),
    ('user_2022110000015', 'Саша', 850);
