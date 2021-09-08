import logging
from app import db


def submit_and_redirect_or_rollback(method_name):
    try:
        db.session.commit()
        return True
    except Exception as e:
        logging.error(f'Encountered error in {method_name} {str(e)}')
        db.session.rollback()

    return False


def add_to_session_and_submit(data, method_name):
    db.session.add(data)
    return submit_and_redirect_or_rollback(method_name)
