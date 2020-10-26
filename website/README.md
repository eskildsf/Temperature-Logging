# Website
For a tutorial on how to set up NGINX, uwsgi and serve Flask websites on Ubuntu, see https://medium.com/swlh/deploy-flask-applications-with-uwsgi-and-nginx-on-ubuntu-18-04-2a47f378c3d2.

Python dependencies are:
 * [Flask](https://flask.palletsprojects.com/)
 * [PeeWee](https://github.com/coleifer/peewee)

Install both by `pip install flask peewee`

JavaScript dependencies are:
 * [JQuery](https://jquery.com/)
 * [Prototype](http://prototypejs.org/)
 * [Canvas.js](https://canvasjs.com/)

These are included.

## Configuration

The following has to be configured:

* `uwsgi.ini` 
  * Website directory
  * Socket directory
* `nginx.conf`
  * Path of uwsgi socket
  * Domain name
* `src/website.py`
  * Password - remember that this should be identical to the one on the ESP8266

You are welcome to also configure [Sentry](https://sentry.io/) but it is not required.
