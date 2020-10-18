from model import RecipeManager, User

if __name__ == '__main__':
    print(dir(RecipeManager))
    man = RecipeManager.new_from_env()
    user = User.register_new_user(man, 'emi', 'Secure Password Lol')
    print(f'{user.uid} : {user.username} {user.pass_hash}')
    user.username = 'thea'
    user.save()
    print(f'{user.uid} : {user.username} {user.pass_hash}')

