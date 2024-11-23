from website import create_app

app = create_app()

#  only if we run this file, not import the file main.py are we going to execute debug mode as true
# for some reason if you were to import main.py from another file, it would just run the web server
if __name__ == '__main__':
    app.run(debug=True)