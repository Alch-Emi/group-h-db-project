# Group h's Recipe Manager

This is h's submission to the Databases project, a command-line database driven recipe
manager, including the ability for multiple users to save, edit, share, and search
recipes, and track their own ingredients

## Components

This project is broken into several components:

 - A model, used to abstract the connection to the database, and provide maleable
   representations of several entities, such as Users, Recipes, and Ingredients.  This is
   completely independant from the other modules.  The code for this can be found in the
   local/model directory, with a simple demo available in local/model_demo.py

 - A user interface, primarilly stored in local/InputLoops.py.  This handles any and all
   user interaction, including a full TUI allowing login, registration, inventory
   management, recipe management, recipe searching, and more.

 - A generator, found in local/generator.  This is used to generate fake, random data to
   fill the database, using a starter vocabulary.

## Installation & Execution

To install:

```bash

# Download the project
git clone https://github.com/Alch-Emi/group-h-db-project.git
cd group-h-db-project

# Set up a virtual environment
python -m venv .
. bin/activate

# Install requirements
pip install -r requirements.txt

# Enter the source directory
cd local
```

Before continuing, you need to configure the database by setting the `DATABASE`
environment variable.  This should be set to a postgres database url.  For more
information, please see [the reference here][1].

To run the TUI:

```bash
python InputLoops.py
```

To run the generator:

```bash
python generator/generator.py
```

To run the model demo:

```bash
python model_demo.py
```

[1]: https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
