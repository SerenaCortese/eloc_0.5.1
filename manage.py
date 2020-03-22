from app import create_app

from app.models import User
#todo - can't remove the previous code line for some reason...



app = create_app('default') #It rerurns Flask obj

if __name__ == '__main__':
    app.run()