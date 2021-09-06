from app.main import bp


@bp.get('/')
def home():
    return 'Hello World'