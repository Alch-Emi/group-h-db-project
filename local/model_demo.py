from model import RecipeManager, User

if __name__ == '__main__':
    # Create RecipeManager
    man = RecipeManager.new_from_env()

    # Clean out database (for demo only)
    c = man.get_cursor()
    c.execute("DELETE FROM users WHERE username = 'thea';")
    c.close()

    # Register new user
    user = User.register_new_user(man, 'emi', 'Secure Password Lol')
    print(f'New User: {user.uid} : {user.username} {user.pass_hash}')

    # Change the user's username
    user.username = 'thea'
    user.save()
    print(f'Changed Username: {user.uid} : {user.username} {user.pass_hash}')

    # Fetch the user from the database
    user = None
    user = User.get_user(man, 'thea')
    print(f'Fetched from database: {user.uid} : {user.username} {user.pass_hash}')
