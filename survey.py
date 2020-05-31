from app import app

app._static_folder = '/webApp/app/static'

if __name__ == '__main__':
    app.run(debug=True)
