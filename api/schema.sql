drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  'uuid' text not null,
  'name' text not null,
  'address' text not null,
  'address2' text not null,
  'city' text not null,
  'state' text not null,
  'zip' integer not null,
  'country' text not null,
  'phone' integer not null,
  'website' text not null,
  'created_at' text not null
);