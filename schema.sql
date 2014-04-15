drop table if exists entries;
create table entries (
id integer primary key autoincrement,
contest text not null,
user text not null,
rank integer,
score real
);