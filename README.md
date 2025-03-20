## Setting up the HAT

sudo raspi-config
 
and do

3 Interface Options
I6 Serial Port
Login shell over serial? No
Serial port hardware enabled? Yes

pip install KitronikAirQualityControlHAT

### fixup

Modify KiktronikAirQualityControlHAT.py in the library on line 381 as follows: (https://github.com/KitronikLtd/Kitronik-Raspberry-Pi-Air-Quality-Control-HAT-Python/pull/4)

```
def displayText(self, text, line, x_offset = 0):
    if line < 1: line = 1
    if line > 6: line = 6
    y = (line * 11) - 10
    (font_width, font_height) = self.font.getbbox(text)[2:4]
    self.draw.text((x_offset, y), text, font = self.font, fill = 1)
```

## To save to the requirements

pip freeze > requirements.txt

## To run, first activate the venv:

./venv/Scripts/activate.ps1

Then run

flask run

flask socketio docs: https://flask-socketio.readthedocs.io/en/latest/getting_started.html#receiving-messages

python socketio docs: https://python-socketio.readthedocs.io/en/stable/intro.html#

source venv/bin/activate

run with gunicorn":
gunicorn --bind 0.0.0.0:8000 app:app

and make sure nginx is wired into this:

server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        proxy_pass http://127.0.0.1:8000;  # Replace 8000 with Gunicorn's port
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

under 

/etc/nginx/sites-enabled/default

Now add gunicorn as a service so it starts up

Create sudo nano /etc/systemd/system/gunicorn.service

```
[Unit]
Description=Gunicorn instance to serve app
After=network.target
Requires=nginx.service

[Service]
User=gjh
Group=gjh
ProtectHome=false
WorkingDirectory=/home/gjh/repos/saunaPy
ExecStart=/home/gjh/repos/saunaPy/venv/bin/gunicorn --bind 0.0.0.0:8000 app:app

[Install]
WantedBy=multi-user.target
```

Now install the service: sudo systemctl enable gunicorn.service

