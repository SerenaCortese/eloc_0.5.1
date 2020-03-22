from flask import render_template

from . import err


#WATCH OUT
#the error handlers will be invoked only for errors originated in the blueprint
#app_errorhandler can be used insted

@err.app_errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@err.app_errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500