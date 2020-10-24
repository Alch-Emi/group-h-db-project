# h's Project Report #
Phase 4

Several small changes were made to our table planning documents (ER Diagram & Reduction to
Tables), including the following:

 - `storage_location` was moved to the `ingredients` table from the `ingredient_ownership`
   table.  The thought process behind this was that since most users will store an
   ingredient in one place, there's no need to track this per-user.

 - An `owner` field was added to the `recipes` table to facilitate a relationship wherein
   recipes can be owned by users.  That this was left out was mostly an oversight.  Adding
   it in allows users to edit recipes they create, list their recipes, and delete recipes
   they no longer want.

 - Several small changes in the names of the tables were made, largely in order to use a
   standardized naming scheme.  Examples of the changes include pluralizing tables like
   `recipes` and `users`, and making `rid` lowercase.

Detailed SQL statements can used to create the tables used can be seen in the db_init.py
file, and will be automatically executed when the program is run, creating the tables if
they don't yet exist.  For convenience's sake, a small subset of these this rendered below:

```sql
CREATE TABLE IF NOT EXISTS steps(
    rid             INT         NOT NULL,
    stepnum         INT         NOT NULL,
    description     TEXT        NOT NULL,
    FOREIGN KEY(rid) REFERENCES recipes(rid),
    UNIQUE(rid, stepnum)
);

CREATE TABLE IF NOT EXISTS dates_made(
    id              SERIAL      PRIMARY KEY,
    uid             INT         NOT NULL,
    rid             INT         NOT NULL,
    dateMade        TIMESTAMP   NOT NULL DEFAULT NOW(),
    FOREIGN KEY(uid) REFERENCES users(uid),
    FOREIGN KEY(rid) REFERENCES recipes(rid)
);

CREATE TABLE IF NOT EXISTS users(
    uid             SERIAL      PRIMARY KEY,
    username        VARCHAR(50) NOT NULL UNIQUE,
    password_hash   VARCHAR(60) NOT NULL
);
```

Our sample data was generated using a random generator, visible in the `generator`
subdirectory of the project.  This generator uses the project's existing API to populate
the database using data produced using procedural generation and several source files
containing the vocabulary used.

A video demonstration of our project can be seen at https://youtu.be/4W0ghJ3Li7Q

Our code is available online at https://github.com/Alch-Emi/group-h-db-project
